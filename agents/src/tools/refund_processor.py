import os
import time
import json
from typing import Dict, Any, Optional, List
from cryptography.fernet import Fernet
from web3 import Web3
from web3.middleware import geth_poa_middleware
import aiohttp


class RefundProcessor:
    """Tool for processing blockchain refunds with validation and execution"""
    
    def __init__(self, company_id: str, max_refund_amount: str, expected_address: str,
                 custom_api_url: Optional[str] = None, custom_api_headers: Optional[Dict[str, str]] = None,
                 custom_api_field: Optional[str] = None, escalation_threshold: Optional[str] = None):
        self.company_id = company_id
        self.max_refund_amount = max_refund_amount
        self.expected_address = expected_address
        self.custom_api_url = custom_api_url
        self.custom_api_headers = custom_api_headers or {}
        self.custom_api_field = custom_api_field
        self.escalation_threshold = escalation_threshold or max_refund_amount
        
        self.encryption_key = os.getenv('REFUND_ENCRYPTION_KEY')
        if not self.encryption_key:
            self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Chain configurations
        self.chain_configs = {
            'ethereum': {
                'rpc_url': os.getenv('ETHEREUM_RPC_URL', 'https://sepolia.gateway.tenderly.co'),
                'chain_id': 11155111,
                'native_token': 'ETH'
            },
            'polygon': {
                'rpc_url': os.getenv('POLYGON_RPC_URL', 'https://polygon-amoy-bor-rpc.publicnode.com'),
                'chain_id': 80002,
                'native_token': 'AMOY'
            },
            'bsc': {
                'rpc_url': os.getenv('BASE_RPC_URL', 'https://sepolia.base.org'),
                'chain_id': 84532,
                'native_token': 'ETH'
            }
        }
    
    
    async def _call_custom_api(self, api_url: str, headers: Dict[str, str], 
                              field_to_compare: str, transaction_hash: str, 
                              chain: str) -> Dict[str, Any]:
        """Call company's custom API to validate transaction data"""
        try:
            if not api_url:
                return {"valid": True, "message": "No custom API configured"}
            
            # Prepare request data
            request_data = {
                "transaction_hash": transaction_hash,
                "chain": chain,
                "field_to_compare": field_to_compare
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=request_data, headers=headers) as response:
                    if response.status != 200:
                        return {
                            "valid": False,
                            "error": f"Custom API returned status {response.status}"
                        }
                    
                    data = await response.json()
                    
                    # Check if the API response indicates validation success
                    if data.get("valid", False):
                        return {
                            "valid": True,
                            "message": "Custom API validation successful",
                            "api_response": data
                        }
                    else:
                        return {
                            "valid": False,
                            "error": data.get("error", "Custom API validation failed"),
                            "api_response": data
                        }
                        
        except Exception as e:
            return {
                "valid": False,
                "error": f"Custom API call failed: {str(e)}"
            }
    
    def _encrypt_private_key(self, private_key: str) -> str:
        """Encrypt a private key for secure storage"""
        return self.cipher_suite.encrypt(private_key.encode()).decode()
    
    def _decrypt_private_key(self, encrypted_key: str) -> str:
        """Decrypt a private key for use"""
        return self.cipher_suite.decrypt(encrypted_key.encode()).decode()
    
    def _get_web3_instance(self, chain: str) -> Web3:
        """Get Web3 instance for the specified chain"""
        if chain not in self.chain_configs:
            raise ValueError(f"Unsupported chain: {chain}")
        
        config = self.chain_configs[chain]
        w3 = Web3(Web3.HTTPProvider(config['rpc_url']))
        
        # Add PoA middleware for some chains
        if chain in ['bsc', 'polygon']:
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        if not w3.is_connected():
            raise ConnectionError(f"Failed to connect to {chain} network")
        
        return w3
    
    async def _verify_transaction(self, tx_hash: str, chain: str, expected_from: str, 
                                expected_to: str, expected_amount: str, 
                                token_address: Optional[str] = None, 
                                allow_overpayment: bool = False) -> Dict[str, Any]:
        """Verify a transaction using GoldRush API"""
        try:
            api_key = os.getenv('GOLDRUSH_API_KEY')
            if not api_key:
                return {"verified": False, "error": "GoldRush API key not configured"}
            
            # Map chain names to GoldRush format
            chain_mapping = {
                'ethereum': 'eth-sepolia',
                'polygon': 'polygon-amoy',
                'bsc': 'base-sepolia'
            }
            
            goldrush_chain = chain_mapping.get(chain)
            if not goldrush_chain:
                return {"verified": False, "error": f"Unsupported chain for verification: {chain}"}
            
            base_url = "https://api.goldrush.dev/v1"
            headers = {"Authorization": f"Bearer {api_key}"}
            url = f"{base_url}/{goldrush_chain}/transaction_v2/{tx_hash}"
            params = {"with-internal": "true"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        return {
                            "verified": False,
                            "error": f"Failed to fetch transaction: {response.status}"
                        }
                    
                    data = await response.json()
            
            items = data.get("items", [])
            if not items:
                return {"verified": False, "error": "No transaction found"}
            
            tx = items[0]
            
            # Check if transaction was successful
            if not tx.get("successful", False):
                return {"verified": False, "error": "Transaction was not successful"}
            
            # Verify transaction details
            mismatches = []
            
            # Check from address
            actual_from = tx.get("from_address", "").lower()
            if actual_from != expected_from.lower():
                mismatches.append({
                    "field": "from_address",
                    "expected": expected_from.lower(),
                    "actual": actual_from
                })
            
            # Check to address
            actual_to = tx.get("to_address", "").lower()
            if actual_to != expected_to.lower():
                mismatches.append({
                    "field": "to_address",
                    "expected": expected_to.lower(),
                    "actual": actual_to
                })
            
            # Check amount - handle overpayment scenarios
            actual_amount = int(tx.get("value", "0"))
            expected_amount_wei = int(expected_amount)
            
            if allow_overpayment:
                # For overpayment scenarios, actual amount should be >= expected amount
                if actual_amount < expected_amount_wei:
                    mismatches.append({
                        "field": "amount",
                        "expected": f"At least {expected_amount}",
                        "actual": str(actual_amount),
                        "error": "Payment amount is less than expected"
                    })
            else:
                # Exact amount matching (original behavior)
                if actual_amount != expected_amount_wei:
                    mismatches.append({
                        "field": "amount",
                        "expected": expected_amount,
                        "actual": str(actual_amount)
                    })
            
            if mismatches:
                return {
                    "verified": False,
                    "mismatches": mismatches
                }
            else:
                return {
                    "verified": True,
                    "message": "Transaction verified successfully",
                    "actual_amount": str(actual_amount),
                    "expected_amount": expected_amount,
                    "overpayment": str(max(0, actual_amount - expected_amount_wei)) if allow_overpayment else "0"
                }
                
        except Exception as e:
            return {
                "verified": False,
                "error": f"Verification failed: {str(e)}"
            }
    
    async def process_refund(self, user_address: str, transaction_hash: str, 
                           requested_amount: str, agent_private_key: str, 
                           refund_chain: str, max_refund_amount: Optional[str] = None,
                           reason: Optional[str] = None) -> Dict[str, Any]:
        """Process a refund transaction"""
        start_time = time.time()
        
        try:
            if not self.expected_address:
                return {
                    "success": False,
                    "error": f"No company address configured for company {self.company_id}"
                }
            
            effective_max_refund = max_refund_amount or self.max_refund_amount
            requested_amount_wei = int(requested_amount)
            max_refund_wei = int(effective_max_refund)
            
            if requested_amount_wei > max_refund_wei:
                escalation_threshold = int(self.escalation_threshold)
                if requested_amount_wei > escalation_threshold:
                    return {
                        "success": False,
                        "escalation_required": True,
                        "error": f"Requested amount {requested_amount} exceeds escalation threshold {escalation_threshold}. Human intervention required.",
                        "escalation_reason": "Amount exceeds company escalation threshold"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Requested amount {requested_amount} exceeds maximum refund {effective_max_refund}"
                    }
            
            if self.custom_api_url:
                custom_api_result = await self._call_custom_api(
                    api_url=self.custom_api_url,
                    headers=self.custom_api_headers,
                    field_to_compare=self.custom_api_field,
                    transaction_hash=transaction_hash,
                    chain=refund_chain
                )
                
                if not custom_api_result.get('valid', False):
                    return {
                        "success": False,
                        "error": f"Custom API validation failed: {custom_api_result.get('error', 'Unknown error')}"
                    }
            
            tx_verification = await self._verify_transaction(
                tx_hash=transaction_hash,
                chain=refund_chain,
                expected_from=user_address,
                expected_to=self.expected_address,
                expected_amount=requested_amount
            )
            
            if not tx_verification.get("verified", False):
                return {
                    "success": False,
                    "error": f"Transaction verification failed: {tx_verification.get('error', 'Unknown error')}"
                }
            
            # Decrypt the private key
            private_key = self._decrypt_private_key(agent_private_key)
            
            # Get Web3 instance
            w3 = self._get_web3_instance(refund_chain)
            
            # Create account from private key
            account = w3.eth.account.from_key(private_key)
            
            # Check account balance
            balance = w3.eth.get_balance(account.address)
            refund_amount_wei = int(requested_amount)
            
            if balance < refund_amount_wei:
                return {
                    "success": False,
                    "error": f"Insufficient balance: {balance} wei < {refund_amount_wei} wei"
                }
            
            # Get current gas price
            gas_price = w3.eth.gas_price
            
            # Estimate gas for the transaction
            gas_estimate = 21000  # Standard transfer gas limit
            
            # Build transaction
            transaction = {
                'from': account.address,
                'to': user_address,
                'value': refund_amount_wei,
                'gas': gas_estimate,
                'gasPrice': gas_price,
                'nonce': w3.eth.get_transaction_count(account.address)
            }
            
            # Sign and send transaction
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "refund_tx_hash": receipt.transactionHash.hex(),
                "refund_amount": requested_amount,
                "gas_used": receipt.gasUsed,
                "processing_time": processing_time,
                "user_address": user_address,
                "reason": reason
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                "success": False,
                "error": f"Refund processing failed: {str(e)}",
                "processing_time": processing_time
            }
    
    async def validate_refund_request(self, user_address: str, transaction_hash: str, 
                                     requested_amount: str, refund_chain: str,
                                     max_refund_amount: Optional[str] = None) -> Dict[str, Any]:
        """Validate a refund request without processing"""
        try:
            if not self.expected_address:
                return {
                    "valid": False,
                    "error": f"No company address configured for company {self.company_id}"
                }
            
            effective_max_refund = max_refund_amount or self.max_refund_amount
            requested_amount_wei = int(requested_amount)
            max_refund_wei = int(effective_max_refund)
            
            if requested_amount_wei > max_refund_wei:
                escalation_threshold = int(self.escalation_threshold)
                if requested_amount_wei > escalation_threshold:
                    return {
                        "valid": False,
                        "escalation_required": True,
                        "error": f"Requested amount {requested_amount} exceeds escalation threshold {escalation_threshold}. Human intervention required.",
                        "escalation_reason": "Amount exceeds company escalation threshold"
                    }
                else:
                    return {
                        "valid": False,
                        "error": f"Requested amount {requested_amount} exceeds maximum refund {effective_max_refund}"
                    }
            
            if self.custom_api_url:
                custom_api_result = await self._call_custom_api(
                    api_url=self.custom_api_url,
                    headers=self.custom_api_headers,
                    field_to_compare=self.custom_api_field,
                    transaction_hash=transaction_hash,
                    chain=refund_chain
                )
                
                if not custom_api_result.get('valid', False):
                    return {
                        "valid": False,
                        "error": f"Custom API validation failed: {custom_api_result.get('error', 'Unknown error')}"
                    }
            
            # Verify the original transaction
            tx_verification = await self._verify_transaction(
                tx_hash=transaction_hash,
                chain=refund_chain,
                expected_from=user_address,
                expected_to=self.expected_address,
                expected_amount=requested_amount
            )
            
            if not tx_verification.get("verified", False):
                return {
                    "valid": False,
                    "error": f"Transaction verification failed: {tx_verification.get('error', 'Unknown error')}"
                }
            
            return {
                "valid": True,
                "message": "Refund request validation successful",
                "user_address": user_address,
                "transaction_hash": transaction_hash,
                "requested_amount": requested_amount
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation failed: {str(e)}"
            }
    
    async def process_overpayment_refund(self, user_address: str, transaction_hash: str, 
                                       expected_amount: str, agent_private_key: str, 
                                       refund_chain: str, max_refund_amount: Optional[str] = None,
                                       reason: Optional[str] = None) -> Dict[str, Any]:
        """Process a refund for overpayment scenarios where user paid more than expected"""
        start_time = time.time()
        
        try:
            if not self.expected_address:
                return {
                    "success": False,
                    "error": f"No company address configured for company {self.company_id}"
                }
            
            tx_verification = await self._verify_transaction(
                tx_hash=transaction_hash,
                chain=refund_chain,
                expected_from=user_address,
                expected_to=self.expected_address,
                expected_amount=expected_amount,
                allow_overpayment=True
            )
            
            if not tx_verification.get("verified", False):
                return {
                    "success": False,
                    "error": f"Transaction verification failed: {tx_verification.get('error', 'Unknown error')}"
                }
            
            actual_amount = int(tx_verification.get("actual_amount", "0"))
            expected_amount_wei = int(expected_amount)
            overpayment_amount = actual_amount - expected_amount_wei
            
            if overpayment_amount <= 0:
                return {
                    "success": False,
                    "error": "No overpayment detected. Actual payment matches or is less than expected amount."
                }
            
            # Check if refund amount is within limits
            effective_max_refund = max_refund_amount or self.max_refund_amount
            max_refund_wei = int(effective_max_refund)
            
            if overpayment_amount > max_refund_wei:
                escalation_threshold = int(self.escalation_threshold)
                if overpayment_amount > escalation_threshold:
                    return {
                        "success": False,
                        "escalation_required": True,
                        "error": f"Overpayment amount {overpayment_amount} exceeds escalation threshold {escalation_threshold}. Human intervention required.",
                        "escalation_reason": "Overpayment amount exceeds company escalation threshold",
                        "overpayment_amount": str(overpayment_amount),
                        "expected_amount": expected_amount,
                        "actual_amount": str(actual_amount)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Overpayment amount {overpayment_amount} exceeds maximum refund {effective_max_refund}",
                        "overpayment_amount": str(overpayment_amount),
                        "expected_amount": expected_amount,
                        "actual_amount": str(actual_amount)
                    }
            
            if self.custom_api_url:
                custom_api_result = await self._call_custom_api(
                    api_url=self.custom_api_url,
                    headers=self.custom_api_headers,
                    field_to_compare=self.custom_api_field,
                    transaction_hash=transaction_hash,
                    chain=refund_chain
                )
                
                if not custom_api_result.get('valid', False):
                    return {
                        "success": False,
                        "error": f"Custom API validation failed: {custom_api_result.get('error', 'Unknown error')}"
                    }
            
            private_key = self._decrypt_private_key(agent_private_key)
            
            w3 = self._get_web3_instance(refund_chain)
            
            account = w3.eth.account.from_key(private_key)
            
            balance = w3.eth.get_balance(account.address)
            
            if balance < overpayment_amount:
                return {
                    "success": False,
                    "error": f"Insufficient balance: {balance} wei < {overpayment_amount} wei"
                }
            
            gas_price = w3.eth.gas_price
            
            gas_estimate = 21000 
            
            transaction = {
                'from': account.address,
                'to': user_address,
                'value': overpayment_amount,
                'gas': gas_estimate,
                'gasPrice': gas_price,
                'nonce': w3.eth.get_transaction_count(account.address)
            }
            
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "refund_tx_hash": receipt.transactionHash.hex(),
                "refund_amount": str(overpayment_amount),
                "overpayment_amount": str(overpayment_amount),
                "expected_amount": expected_amount,
                "actual_amount": str(actual_amount),
                "gas_used": receipt.gasUsed,
                "processing_time": processing_time,
                "user_address": user_address,
                "reason": reason or f"Refund for overpayment: paid {actual_amount} wei instead of {expected_amount} wei"
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                "success": False,
                "error": f"Overpayment refund processing failed: {str(e)}",
                "processing_time": processing_time
            }
    
    def get_refund_processor_schema(self) -> Dict[str, Any]:
        """Get the OpenAI function calling schema for refund processing"""
        return {
            "name": "process_refund",
            "description": "Process a refund transaction to a user's wallet address",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_address": {
                        "type": "string",
                        "description": "The user's wallet address to send the refund to"
                    },
                    "transaction_hash": {
                        "type": "string",
                        "description": "The original transaction hash to verify"
                    },
                    "requested_amount": {
                        "type": "string",
                        "description": "The amount to refund (in wei)"
                    },
                    "agent_private_key": {
                        "type": "string",
                        "description": "The encrypted private key for the agent's wallet"
                    },
                    "refund_chain": {
                        "type": "string",
                        "description": "The blockchain network for the refund (ethereum, polygon, bsc)",
                        "enum": ["ethereum", "polygon", "bsc"]
                    },
                    "max_refund_amount": {
                        "type": "string",
                        "description": "Maximum refund amount allowed (in wei) - overrides company default"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the refund"
                    }
                },
                "required": ["user_address", "transaction_hash", "requested_amount", "agent_private_key", "refund_chain"]
            }
        }
    
    def get_refund_validation_schema(self) -> Dict[str, Any]:
        """Get the OpenAI function calling schema for refund validation"""
        return {
            "name": "validate_refund_request",
            "description": "Validate a refund request without processing the transaction",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_address": {
                        "type": "string",
                        "description": "The user's wallet address requesting the refund"
                    },
                    "transaction_hash": {
                        "type": "string",
                        "description": "The original transaction hash to verify"
                    },
                    "requested_amount": {
                        "type": "string",
                        "description": "The amount requested for refund (in wei)"
                    },
                    "refund_chain": {
                        "type": "string",
                        "description": "The blockchain network for the refund (ethereum, polygon, bsc)",
                        "enum": ["ethereum", "polygon", "bsc"]
                    },
                    "max_refund_amount": {
                        "type": "string",
                        "description": "Maximum refund amount allowed (in wei) - overrides company default"
                    }
                },
                "required": ["user_address", "transaction_hash", "requested_amount", "refund_chain"]
            }
        }
    
    def get_overpayment_refund_schema(self) -> Dict[str, Any]:
        """Get the OpenAI function calling schema for overpayment refund processing"""
        return {
            "name": "process_overpayment_refund",
            "description": "Process a refund for overpayment scenarios where user paid more than the expected amount",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_address": {
                        "type": "string",
                        "description": "The user's wallet address to send the refund to"
                    },
                    "transaction_hash": {
                        "type": "string",
                        "description": "The original transaction hash to verify"
                    },
                    "expected_amount": {
                        "type": "string",
                        "description": "The expected/correct amount that should have been paid (in wei)"
                    },
                    "agent_private_key": {
                        "type": "string",
                        "description": "The encrypted private key for the agent's wallet"
                    },
                    "refund_chain": {
                        "type": "string",
                        "description": "The blockchain network for the refund (ethereum, polygon, bsc)",
                        "enum": ["ethereum", "polygon", "bsc"]
                    },
                    "max_refund_amount": {
                        "type": "string",
                        "description": "Maximum refund amount allowed (in wei) - overrides company default"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the refund"
                    }
                },
                "required": ["user_address", "transaction_hash", "expected_amount", "agent_private_key", "refund_chain"]
            }
        }


def create_refund_processor(company_id: str, max_refund_amount: str, expected_address: str,
                           custom_api_url: Optional[str] = None, custom_api_headers: Optional[Dict[str, str]] = None,
                           custom_api_field: Optional[str] = None, escalation_threshold: Optional[str] = None) -> RefundProcessor:
    """Create a RefundProcessor instance with company configuration"""
    return RefundProcessor(
        company_id=company_id,
        max_refund_amount=max_refund_amount,
        expected_address=expected_address,
        custom_api_url=custom_api_url,
        custom_api_headers=custom_api_headers,
        custom_api_field=custom_api_field,
        escalation_threshold=escalation_threshold
    )


async def process_refund(refund_processor: RefundProcessor, user_address: str, transaction_hash: str, 
                        requested_amount: str, agent_private_key: str, refund_chain: str,
                        max_refund_amount: Optional[str] = None, reason: Optional[str] = None) -> Dict[str, Any]:
    """Process a refund transaction"""
    return await refund_processor.process_refund(
        user_address, transaction_hash, requested_amount, agent_private_key,
        refund_chain, max_refund_amount, reason
    )


async def validate_refund_request(refund_processor: RefundProcessor, user_address: str, transaction_hash: str, 
                                requested_amount: str, refund_chain: str,
                                max_refund_amount: Optional[str] = None) -> Dict[str, Any]:
    """Validate a refund request without processing"""
    return await refund_processor.validate_refund_request(
        user_address, transaction_hash, requested_amount, refund_chain,
        max_refund_amount
    )


async def process_overpayment_refund(refund_processor: RefundProcessor, user_address: str, transaction_hash: str, 
                                   expected_amount: str, agent_private_key: str, refund_chain: str,
                                   max_refund_amount: Optional[str] = None, reason: Optional[str] = None) -> Dict[str, Any]:
    """Process a refund for overpayment scenarios"""
    return await refund_processor.process_overpayment_refund(
        user_address, transaction_hash, expected_amount, agent_private_key,
        refund_chain, max_refund_amount, reason
    )


def get_refund_processor_schema() -> Dict[str, Any]:
    """Get the OpenAI function calling schema for refund processing"""
    # Create a temporary instance to get the schema
    temp_processor = RefundProcessor("temp", "0", "0x0")
    return temp_processor.get_refund_processor_schema()


def get_refund_validation_schema() -> Dict[str, Any]:
    """Get the OpenAI function calling schema for refund validation"""
    # Create a temporary instance to get the schema
    temp_processor = RefundProcessor("temp", "0", "0x0")
    return temp_processor.get_refund_validation_schema()


def get_overpayment_refund_schema() -> Dict[str, Any]:
    """Get the OpenAI function calling schema for overpayment refund processing"""
    # Create a temporary instance to get the schema
    temp_processor = RefundProcessor("temp", "0", "0x0")
    return temp_processor.get_overpayment_refund_schema()


__all__ = [
    'RefundProcessor',
    'create_refund_processor',
    'process_refund',
    'validate_refund_request',
    'process_overpayment_refund',
    'get_refund_processor_schema',
    'get_refund_validation_schema',
    'get_overpayment_refund_schema'
]