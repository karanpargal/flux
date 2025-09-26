import os
import aiohttp
from typing import Any, Dict


async def verify_transaction(
    tx_hash: str,
    chain_name: str,
    from_address: str,
    to_address: str,
    token_address: str,
    amount: str,
    is_native: bool = False
) -> Dict[str, Any]:
    """
    Verify if a blockchain transaction matches the expected parameters
    
    Args:
        tx_hash: Transaction hash to verify
        chain_name: Blockchain name (e.g., 'eth-mainnet')
        from_address: Expected sender address
        to_address: Expected receiver address
        token_address: Token contract address (use 'native' for native token)
        amount: Expected amount (in wei for native, token units for ERC-20)
        is_native: Whether this is a native token transfer (True) or a token transfer (False)
        
    Returns:
        Dictionary with verification result and mismatches if any
    """
    try:
        # GoldRush API configuration
        api_key = os.getenv('GOLDRUSH_API_KEY', 'your-default-api-key')
        base_url = "https://api.goldrush.dev/v1"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Fetch transaction from GoldRush API
        url = f"{base_url}/{chain_name}/transaction_v2/{tx_hash}"
        params = {"with-internal": "true"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    return {
                        "verified": False,
                        "error": f"Failed to fetch transaction: {response.status}"
                    }
                
                data = await response.json()
        
        # Extract transaction data
        items = data.get("items", [])
        if not items:
            return {"verified": False, "error": "No transaction found"}
        
        tx = items[0]
        
        # Check if transaction was successful
        if not tx.get("successful", False):
            return {"verified": False, "error": "Transaction was not successful"}
        
        # Compare values and collect mismatches
        mismatches = []
        
        if is_native:
            # For native token transfers
            # Check from address
            actual_from = tx.get("from_address", "").lower()
            expected_from = from_address.lower()
            if actual_from != expected_from:
                mismatches.append({
                    "field": "from_address",
                    "expected": expected_from,
                    "actual": actual_from
                })
            
            # Check to address (for native transfers, this is the actual recipient)
            actual_to = tx.get("to_address", "").lower()
            expected_to = to_address.lower()
            if actual_to != expected_to:
                mismatches.append({
                    "field": "to_address", 
                    "expected": expected_to,
                    "actual": actual_to
                })
            
            # Check amount (main value field for native transfers)
            actual_amount = tx.get("value", "0")
            if actual_amount != amount:
                mismatches.append({
                    "field": "amount",
                    "expected": amount,
                    "actual": actual_amount
                })
                
        else:
            # For ERC-20 token transfers
            # Check from address (transaction initiator)
            actual_from = tx.get("from_address", "").lower()
            expected_from = from_address.lower()
            if actual_from != expected_from:
                mismatches.append({
                    "field": "from_address",
                    "expected": expected_from,
                    "actual": actual_from
                })
            
            # For ERC-20, check that to_address is the token contract
            actual_to = tx.get("to_address", "").lower()
            expected_token_contract = token_address.lower()
            if actual_to != expected_token_contract:
                mismatches.append({
                    "field": "token_contract",
                    "expected": expected_token_contract,
                    "actual": actual_to
                })
            
            # Check transfer event logs for actual recipient and amount
            log_events = tx.get("log_events", [])
            found_transfer = False
            
            for event in log_events:
                if (event.get("sender_address", "").lower() == token_address.lower() and
                    "transfer" in event.get("decoded", {}).get("name", "").lower()):
                    
                    params = event.get("decoded", {}).get("params", [])
                    if len(params) >= 3:
                        # Check actual recipient (from transfer event)
                        actual_recipient = params[1].get("value", "").lower()
                        expected_recipient = to_address.lower()
                        if actual_recipient != expected_recipient:
                            mismatches.append({
                                "field": "transfer_recipient",
                                "expected": expected_recipient,
                                "actual": actual_recipient
                            })
                        
                        # Check amount
                        actual_amount = params[2].get("value", "")
                        if actual_amount != amount:
                            mismatches.append({
                                "field": "amount",
                                "expected": amount,
                                "actual": actual_amount
                            })
                        
                        found_transfer = True
                        break
            
            if not found_transfer:
                mismatches.append({
                    "field": "token_transfer",
                    "expected": f"Transfer of {amount} tokens to {to_address}",
                    "actual": "No matching transfer event found"
                })
        
        # Return result
        if mismatches:
            return {
                "verified": False,
                "mismatches": mismatches
            }
        else:
            return {
                "verified": True,
                "message": "All parameters match"
            }
            
    except Exception as e:
        return {
            "verified": False,
            "error": f"Verification failed: {str(e)}"
        }


def get_transaction_verification_schema() -> Dict[str, Any]:
    """Get the OpenAI function calling schema for transaction verification"""
    return {
        "name": "verify_transaction",
        "description": "Verify if a blockchain transaction matches the expected parameters",
        "parameters": {
            "type": "object",
            "properties": {
                "tx_hash": {
                    "type": "string",
                    "description": "The transaction hash to verify"
                },
                "chain_name": {
                    "type": "string",
                    "description": "The blockchain name (e.g., 'eth-mainnet', 'polygon-mainnet')"
                },
                "from_address": {
                    "type": "string",
                    "description": "The expected sender address"
                },
                "to_address": {
                    "type": "string", 
                    "description": "The expected receiver address (for native) or recipient (for ERC-20)"
                },
                "token_address": {
                    "type": "string",
                    "description": "The token contract address. Use 'native' for native blockchain token"
                },
                "amount": {
                    "type": "string",
                    "description": "The expected amount (in wei for native, token units for ERC-20)"
                },
                "is_native": {
                    "type": "boolean",
                    "description": "Whether this is a native token transfer (true) or ERC-20 transfer (false)",
                    "default": False
                }
            },
            "required": ["tx_hash", "chain_name", "from_address", "to_address", "token_address", "amount", "is_native"]
        }
    }


__all__ = [
    'verify_transaction', 
    'get_transaction_verification_schema'
]
