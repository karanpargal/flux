"""
Wallet Service for managing agent wallets and ENS registration
"""

import os
import secrets
from typing import Dict, Any, Optional, List
from web3 import Web3
from web3.middleware import geth_poa_middleware
from ens import ENS
from cryptography.fernet import Fernet
import asyncio
import aiohttp
from datetime import datetime


class WalletService:
    """Service for managing agent wallets and ENS registration"""
    
    def __init__(self):
        self.encryption_key = os.getenv('WALLET_ENCRYPTION_KEY')
        if not self.encryption_key:
            self.encryption_key = Fernet.generate_key()
            print(f"⚠️ Generated new wallet encryption key. Set WALLET_ENCRYPTION_KEY environment variable.")
        
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Chain configurations for wallet creation
        self.chain_configs = {
            'ethereum': {
                'rpc_url': os.getenv('ETHEREUM_RPC_URL', 'https://sepolia.gateway.tenderly.co'),
                'chain_id': 11155111,
                'native_token': 'ETH',
                'ens_supported': True,
                'network_name': 'sepolia'
            },
            'polygon': {
                'rpc_url': os.getenv('POLYGON_RPC_URL', 'https://polygon-amoy-bor-rpc.publicnode.com'),
                'chain_id': 80002,
                'native_token': 'AMOY',
                'ens_supported': False,
                'network_name': 'amoy'
            },
            'bsc': {
                'rpc_url': os.getenv('BASE_RPC_URL', 'https://sepolia.base.org'),
                'chain_id': 84532,
                'native_token': 'ETH',
                'ens_supported': False,
                'network_name': 'base_sepolia'
            }
        }
        
        # Default chain for ENS registration
        self.default_chain = 'ethereum'
        
        # Initialize ENS instance for Sepolia
        self.ens_instance = None
        self._initialize_ens()
    
    def _initialize_ens(self):
        """Initialize ENS instance for Sepolia testnet"""
        try:
            # Get Web3 instance for Ethereum (Sepolia)
            w3 = self._get_web3_instance('ethereum')
            
            # Create ENS instance from Web3 instance
            # This automatically detects the network and uses appropriate ENS contracts
            self.ens_instance = ENS.from_web3(w3)
            
            print(f"✅ ENS initialized for Sepolia testnet")
            print(f"   Network: {self.chain_configs['ethereum']['network_name']}")
            print(f"   RPC URL: {self.chain_configs['ethereum']['rpc_url']}")
            
        except Exception as e:
            print(f"⚠️ Failed to initialize ENS: {str(e)}")
            self.ens_instance = None
    
    def _get_web3_instance(self, chain: str = 'ethereum') -> Web3:
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
    
    def _encrypt_private_key(self, private_key: str) -> str:
        """Encrypt a private key for secure storage"""
        return self.cipher_suite.encrypt(private_key.encode()).decode()
    
    def _decrypt_private_key(self, encrypted_key: str) -> str:
        """Decrypt a private key for use"""
        return self.cipher_suite.decrypt(encrypted_key.encode()).decode()
    
    def generate_wallet(self, chain: str = 'ethereum') -> Dict[str, Any]:
        """Generate a new wallet for an agent"""
        try:
            w3 = self._get_web3_instance(chain)
            
            # Generate a new private key
            private_key = secrets.token_hex(32)
            
            # Create account from private key
            account = w3.eth.account.from_key(private_key)
            
            # Encrypt the private key for storage
            encrypted_private_key = self._encrypt_private_key(private_key)
            
            wallet_info = {
                "address": account.address,
                "encrypted_private_key": encrypted_private_key,
                "chain": chain,
                "chain_id": self.chain_configs[chain]['chain_id'],
                "native_token": self.chain_configs[chain]['native_token'],
                "created_at": datetime.now().isoformat(),
                "balance": "0",  # Initial balance is 0
                "ens_name": None,  # Will be set when ENS is registered
                "ens_registered": False
            }
            
            print(f"✅ Generated new wallet: {account.address} on {chain}")
            return wallet_info
            
        except Exception as e:
            print(f"❌ Failed to generate wallet: {str(e)}")
            raise Exception(f"Wallet generation failed: {str(e)}")
    
    def resolve_ens_name(self, ens_name: str) -> Optional[str]:
        """Resolve ENS name to address on Sepolia testnet"""
        try:
            if not self.ens_instance:
                print("⚠️ ENS not initialized")
                return None
            
            # Get the address for the ENS name
            address = self.ens_instance.address(ens_name)
            if address:
                print(f"✅ Resolved {ens_name} -> {address}")
                return address
            else:
                print(f"❌ ENS name {ens_name} not found")
                return None
                
        except Exception as e:
            print(f"❌ Failed to resolve ENS name {ens_name}: {str(e)}")
            return None
    
    def reverse_resolve_address(self, address: str) -> Optional[str]:
        """Get ENS name for an address (reverse resolution) on Sepolia testnet"""
        try:
            if not self.ens_instance:
                print("⚠️ ENS not initialized")
                return None
            
            # Get the ENS name for the address
            ens_name = self.ens_instance.name(address)
            if ens_name:
                print(f"✅ Reverse resolved {address} -> {ens_name}")
                return ens_name
            else:
                print(f"❌ No ENS name found for address {address}")
                return None
                
        except Exception as e:
            print(f"❌ Failed to reverse resolve address {address}: {str(e)}")
            return None
    
    def get_ens_owner(self, ens_name: str) -> Optional[str]:
        """Get the owner of an ENS name on Sepolia testnet"""
        try:
            if not self.ens_instance:
                print("⚠️ ENS not initialized")
                return None
            
            # Get the owner of the ENS name
            owner = self.ens_instance.owner(ens_name)
            if owner:
                print(f"✅ Owner of {ens_name}: {owner}")
                return owner
            else:
                print(f"❌ No owner found for ENS name {ens_name}")
                return None
                
        except Exception as e:
            print(f"❌ Failed to get owner for ENS name {ens_name}: {str(e)}")
            return None
    
    def get_ens_resolver(self, ens_name: str) -> Optional[str]:
        """Get the resolver address for an ENS name on Sepolia testnet"""
        try:
            if not self.ens_instance:
                print("⚠️ ENS not initialized")
                return None
            
            # Get the resolver for the ENS name
            resolver = self.ens_instance.resolver(ens_name)
            if resolver:
                resolver_address = resolver.address
                print(f"✅ Resolver for {ens_name}: {resolver_address}")
                return resolver_address
            else:
                print(f"❌ No resolver found for ENS name {ens_name}")
                return None
                
        except Exception as e:
            print(f"❌ Failed to get resolver for ENS name {ens_name}: {str(e)}")
            return None
    
    def get_ens_text_record(self, ens_name: str, key: str) -> Optional[str]:
        """Get text record for an ENS name on Sepolia testnet"""
        try:
            if not self.ens_instance:
                print("⚠️ ENS not initialized")
                return None
            
            # Get text record for the ENS name
            text_value = self.ens_instance.get_text(ens_name, key)
            if text_value:
                print(f"✅ Text record {key} for {ens_name}: {text_value}")
                return text_value
            else:
                print(f"❌ No text record {key} found for ENS name {ens_name}")
                return None
                
        except Exception as e:
            print(f"❌ Failed to get text record {key} for ENS name {ens_name}: {str(e)}")
            return None

    async def register_ens_name(self, wallet_info: Dict[str, Any], agent_name: str, 
                              company_name: str, agent_id: str) -> Dict[str, Any]:
        """Register ENS name for an agent wallet on Sepolia testnet"""
        try:
            # Only register ENS on Ethereum mainnet/testnet
            if wallet_info['chain'] != 'ethereum':
                print(f"⚠️ ENS registration only supported on Ethereum, skipping for {wallet_info['chain']}")
                return wallet_info
            
            if not self.ens_instance:
                print("⚠️ ENS not initialized, cannot register name")
                wallet_info.update({
                    "ens_registration_status": "failed",
                    "ens_error": "ENS not initialized"
                })
                return wallet_info
            
            # Clean agent name for ENS compatibility
            clean_agent_name = agent_name.replace(' ', '').replace('_', '').replace('-', '').lower()
            
            # Use .eth for testnet (Sepolia uses same .eth domain)
            ens_name = f"{clean_agent_name}.eth"
            
            try:
                # Check if the name is available
                existing_address = self.resolve_ens_name(ens_name)
                if existing_address:
                    print(f"⚠️ ENS name {ens_name} already exists, trying alternative...")
                    short_agent_id = agent_id[:8].lower()
                    ens_name = f"{clean_agent_name}{short_agent_id}.eth"
                    existing_address = self.resolve_ens_name(ens_name)
                    
                    if existing_address:
                        print(f"⚠️ Alternative ENS name {ens_name} also exists")
                
                # For Sepolia testnet, we'll simulate ENS registration
                # In production, you would need to:
                # 1. Fund the wallet with ETH for gas fees
                # 2. Register the ENS name through the ENS registry contract
                # 3. Set up the resolver to point to the wallet address
                
                print(f"🔍 ENS name proposed: {ens_name}")
                print(f"📍 Would register ENS {ens_name} -> {wallet_info['address']}")
                print(f"🌐 Network: Sepolia testnet")
                
                # Check if we can get ENS registry info
                try:
                    # Try to get some basic ENS info to verify connection
                    test_resolve = self.resolve_ens_name("vitalik.eth")  # Well-known ENS name
                    if test_resolve:
                        print(f"✅ ENS connection verified (resolved vitalik.eth -> {test_resolve})")
                    else:
                        print("ℹ️ ENS connection established but test resolution failed")
                except Exception as test_error:
                    print(f"ℹ️ ENS test resolution failed: {str(test_error)}")
                
                # Mark as prepared for registration
                wallet_info.update({
                    "ens_name": ens_name,
                    "ens_registered": False,  # Would be True after successful registration
                    "ens_registration_status": "prepared",
                    "ens_registration_note": f"ENS name {ens_name} prepared for Sepolia testnet. Registration requires funding and manual setup.",
                    "ens_network": "sepolia",
                    "ens_registry_available": existing_address is None
                })
                
                print(f"✅ ENS name prepared for agent: {ens_name}")
                
            except Exception as ens_error:
                print(f"⚠️ ENS setup failed: {str(ens_error)}")
                wallet_info.update({
                    "ens_name": ens_name if 'ens_name' in locals() else None,
                    "ens_registered": False,
                    "ens_registration_status": "failed",
                    "ens_error": str(ens_error)
                })
            
            return wallet_info
            
        except Exception as e:
            print(f"❌ ENS registration failed: {str(e)}")
            wallet_info.update({
                "ens_registration_status": "failed",
                "ens_error": str(e)
            })
            return wallet_info
    
    async def get_wallet_balance(self, wallet_info: Dict[str, Any]) -> str:
        """Get the current balance of a wallet"""
        try:
            w3 = self._get_web3_instance(wallet_info['chain'])
            balance_wei = w3.eth.get_balance(wallet_info['address'])
            balance_eth = w3.from_wei(balance_wei, 'ether')
            
            return str(balance_eth)
            
        except Exception as e:
            print(f"❌ Failed to get wallet balance: {str(e)}")
            return "0"
    
    async def update_wallet_balance(self, wallet_info: Dict[str, Any]) -> Dict[str, Any]:
        """Update the balance information for a wallet"""
        try:
            new_balance = await self.get_wallet_balance(wallet_info)
            wallet_info['balance'] = new_balance
            wallet_info['balance_updated_at'] = datetime.now().isoformat()
            
            print(f"💰 Updated balance for {wallet_info['address']}: {new_balance} {wallet_info['native_token']}")
            return wallet_info
            
        except Exception as e:
            print(f"❌ Failed to update wallet balance: {str(e)}")
            return wallet_info
    
    def get_wallet_private_key(self, wallet_info: Dict[str, Any]) -> str:
        """Get decrypted private key (use with caution)"""
        try:
            return self._decrypt_private_key(wallet_info['encrypted_private_key'])
        except Exception as e:
            raise Exception(f"Failed to decrypt private key: {str(e)}")
    
    def validate_wallet_info(self, wallet_info: Dict[str, Any]) -> bool:
        """Validate wallet information structure"""
        required_fields = ['address', 'encrypted_private_key', 'chain', 'chain_id', 'created_at']
        
        for field in required_fields:
            if field not in wallet_info:
                return False
        
        # Validate address format
        if not wallet_info['address'].startswith('0x') or len(wallet_info['address']) != 42:
            return False
        
        return True
    
    async def create_agent_wallet(self, agent_name: str, company_name: str, 
                                agent_id: str, chain: str = 'ethereum') -> Dict[str, Any]:
        """Complete wallet creation process for an agent including ENS registration"""
        try:
            print(f"🔨 Creating wallet for agent: {agent_name} ({company_name})")
            
            # Generate the wallet
            wallet_info = self.generate_wallet(chain)
            
            # Register ENS name
            wallet_info = await self.register_ens_name(wallet_info, agent_name, company_name, agent_id)
            
            # Update balance (will be 0 initially)
            wallet_info = await self.update_wallet_balance(wallet_info)
            
            # Add agent-specific information
            wallet_info.update({
                "agent_id": agent_id,
                "agent_name": agent_name,
                "company_name": company_name,
                "wallet_purpose": "agent_operations"
            })
            
            print(f"✅ Agent wallet created successfully!")
            print(f"   Address: {wallet_info['address']}")
            print(f"   ENS: {wallet_info.get('ens_name', 'Not registered')}")
            print(f"   Chain: {wallet_info['chain']}")
            
            return wallet_info
            
        except Exception as e:
            print(f"❌ Failed to create agent wallet: {str(e)}")
            raise Exception(f"Agent wallet creation failed: {str(e)}")
    
    async def test_ens_functionality(self) -> Dict[str, Any]:
        """Test ENS functionality on Sepolia testnet"""
        test_results = {
            "ens_initialized": False,
            "web3_connected": False,
            "network_info": {},
            "test_resolution": {},
            "errors": []
        }
        
        try:
            # Test ENS initialization
            if self.ens_instance:
                test_results["ens_initialized"] = True
                print("✅ ENS instance is initialized")
            else:
                test_results["errors"].append("ENS instance not initialized")
                print("❌ ENS instance not initialized")
            
            # Test Web3 connection
            try:
                w3 = self._get_web3_instance('ethereum')
                if w3.is_connected():
                    test_results["web3_connected"] = True
                    test_results["network_info"] = {
                        "chain_id": w3.eth.chain_id,
                        "block_number": w3.eth.block_number,
                        "network": self.chain_configs['ethereum']['network_name']
                    }
                    print(f"✅ Connected to Web3 - Chain ID: {w3.eth.chain_id}, Block: {w3.eth.block_number}")
                else:
                    test_results["errors"].append("Web3 not connected")
                    print("❌ Web3 not connected")
            except Exception as w3_error:
                test_results["errors"].append(f"Web3 connection error: {str(w3_error)}")
                print(f"❌ Web3 connection error: {str(w3_error)}")
            
            # Test ENS resolution with well-known names
            test_names = ["vitalik.eth", "ens.eth", "ethereum.eth"]
            
            for name in test_names:
                try:
                    address = self.resolve_ens_name(name)
                    reverse_name = None
                    if address:
                        reverse_name = self.reverse_resolve_address(address)
                    
                    test_results["test_resolution"][name] = {
                        "address": address,
                        "reverse_name": reverse_name,
                        "success": address is not None
                    }
                    
                except Exception as resolve_error:
                    test_results["test_resolution"][name] = {
                        "error": str(resolve_error),
                        "success": False
                    }
                    test_results["errors"].append(f"Resolution error for {name}: {str(resolve_error)}")
            
            # Summary
            successful_resolutions = sum(1 for result in test_results["test_resolution"].values() if result.get("success", False))
            test_results["summary"] = {
                "total_tests": len(test_names),
                "successful_resolutions": successful_resolutions,
                "overall_success": test_results["ens_initialized"] and test_results["web3_connected"] and successful_resolutions > 0
            }
            
            if test_results["summary"]["overall_success"]:
                print(f"✅ ENS functionality test passed! {successful_resolutions}/{len(test_names)} names resolved successfully")
            else:
                print(f"⚠️ ENS functionality test completed with issues. {successful_resolutions}/{len(test_names)} names resolved successfully")
            
            return test_results
            
        except Exception as e:
            test_results["errors"].append(f"Test execution error: {str(e)}")
            print(f"❌ ENS functionality test failed: {str(e)}")
            return test_results


def create_wallet_service() -> WalletService:
    """Factory function to create WalletService instance"""
    return WalletService()


# Global wallet service instance
_wallet_service_instance = None


def get_wallet_service() -> WalletService:
    """Get or create wallet service instance"""
    global _wallet_service_instance
    if _wallet_service_instance is None:
        _wallet_service_instance = create_wallet_service()
    return _wallet_service_instance
