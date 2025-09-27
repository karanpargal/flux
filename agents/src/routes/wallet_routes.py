from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel

from ..models.agent_models import AgentWalletInfo
from ..services import get_company_agent_service
from ..services.company_agent_service import CompanyAgentService
from ..services.wallet_service import get_wallet_service, WalletService

router = APIRouter(prefix="/wallets", tags=["wallets"])


class WalletBalanceResponse(BaseModel):
    """Response model for wallet balance"""
    agent_id: str
    wallet_address: str
    balance: str
    native_token: str
    chain: str
    last_updated: str


class ENSRegistrationResponse(BaseModel):
    """Response model for ENS registration status"""
    agent_id: str
    wallet_address: str
    ens_name: str
    registration_status: str
    registration_note: str = None


class ENSTestResponse(BaseModel):
    """Response model for ENS functionality test"""
    ens_initialized: bool
    web3_connected: bool
    network_info: Dict[str, Any] = {}
    test_resolution: Dict[str, Any] = {}
    errors: List[str] = []
    summary: Dict[str, Any] = {}


class ENSResolveRequest(BaseModel):
    """Request model for ENS resolution"""
    ens_name: str


class ENSResolveResponse(BaseModel):
    """Response model for ENS resolution"""
    ens_name: str
    address: str = None
    success: bool
    error: str = None


@router.get("/agent/{agent_id}", response_model=AgentWalletInfo)
async def get_agent_wallet(
    agent_id: str,
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service)
):
    """Get wallet information for a specific agent"""
    try:
        agent_info = company_agent_service.get_company_agent(agent_id)
        
        if not agent_info.wallet_info:
            raise HTTPException(status_code=404, detail="No wallet found for this agent")
        
        return agent_info.wallet_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent wallet: {str(e)}")


@router.get("/agent/{agent_id}/balance", response_model=WalletBalanceResponse)
async def get_agent_wallet_balance(
    agent_id: str,
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service),
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Get current balance for an agent's wallet"""
    try:
        agent_info = company_agent_service.get_company_agent(agent_id)
        
        if not agent_info.wallet_info:
            raise HTTPException(status_code=404, detail="No wallet found for this agent")
        
        # Update balance
        wallet_dict = agent_info.wallet_info.dict()
        updated_wallet = await wallet_service.update_wallet_balance(wallet_dict)
        
        # Update the registry with new balance
        if agent_id in company_agent_service.company_agents_registry:
            company_agent_service.company_agents_registry[agent_id]["wallet_info"] = updated_wallet
        
        return WalletBalanceResponse(
            agent_id=agent_id,
            wallet_address=updated_wallet["address"],
            balance=updated_wallet["balance"],
            native_token=updated_wallet["native_token"],
            chain=updated_wallet["chain"],
            last_updated=updated_wallet.get("balance_updated_at", updated_wallet["created_at"])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get wallet balance: {str(e)}")


@router.get("/agent/{agent_id}/ens", response_model=ENSRegistrationResponse)
async def get_agent_ens_info(
    agent_id: str,
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service)
):
    """Get ENS registration information for an agent's wallet"""
    try:
        agent_info = company_agent_service.get_company_agent(agent_id)
        
        if not agent_info.wallet_info:
            raise HTTPException(status_code=404, detail="No wallet found for this agent")
        
        wallet_info = agent_info.wallet_info
        
        return ENSRegistrationResponse(
            agent_id=agent_id,
            wallet_address=wallet_info.address,
            ens_name=wallet_info.ens_name or "Not registered",
            registration_status=wallet_info.ens_registration_status or "unknown",
            registration_note=getattr(wallet_info, 'ens_registration_note', None)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get ENS info: {str(e)}")


@router.post("/agent/{agent_id}/ens/register")
async def register_agent_ens(
    agent_id: str,
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service),
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Register or update ENS name for an agent's wallet"""
    try:
        agent_info = company_agent_service.get_company_agent(agent_id)
        
        if not agent_info.wallet_info:
            raise HTTPException(status_code=404, detail="No wallet found for this agent")
        
        wallet_dict = agent_info.wallet_info.dict()
        
        # Re-attempt ENS registration
        updated_wallet = await wallet_service.register_ens_name(
            wallet_dict,
            agent_info.agent_name,
            agent_info.company_name,
            agent_id
        )
        
        # Update the registry
        if agent_id in company_agent_service.company_agents_registry:
            company_agent_service.company_agents_registry[agent_id]["wallet_info"] = updated_wallet
        
        return ENSRegistrationResponse(
            agent_id=agent_id,
            wallet_address=updated_wallet["address"],
            ens_name=updated_wallet.get("ens_name", "Registration failed"),
            registration_status=updated_wallet.get("ens_registration_status", "failed"),
            registration_note=updated_wallet.get("ens_registration_note")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register ENS: {str(e)}")


@router.get("", response_model=List[AgentWalletInfo])
async def list_all_agent_wallets(
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service)
):
    """List all agent wallets"""
    try:
        agents = company_agent_service.list_company_agents()
        wallets = []
        
        for agent in agents:
            if agent.wallet_info:
                wallets.append(agent.wallet_info)
        
        return wallets
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list wallets: {str(e)}")


@router.get("/balances", response_model=List[WalletBalanceResponse])
async def get_all_wallet_balances(
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service),
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Get balances for all agent wallets"""
    try:
        agents = company_agent_service.list_company_agents()
        balances = []
        
        for agent in agents:
            if agent.wallet_info:
                try:
                    wallet_dict = agent.wallet_info.dict()
                    updated_wallet = await wallet_service.update_wallet_balance(wallet_dict)
                    
                    # Update the registry
                    if agent.agent_id in company_agent_service.company_agents_registry:
                        company_agent_service.company_agents_registry[agent.agent_id]["wallet_info"] = updated_wallet
                    
                    balances.append(WalletBalanceResponse(
                        agent_id=agent.agent_id,
                        wallet_address=updated_wallet["address"],
                        balance=updated_wallet["balance"],
                        native_token=updated_wallet["native_token"],
                        chain=updated_wallet["chain"],
                        last_updated=updated_wallet.get("balance_updated_at", updated_wallet["created_at"])
                    ))
                except Exception as wallet_error:
                    print(f"Failed to update balance for agent {agent.agent_id}: {str(wallet_error)}")
                    # Continue with other wallets
                    continue
        
        return balances
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get wallet balances: {str(e)}")


@router.get("/stats")
async def get_wallet_stats(
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service)
):
    """Get statistics about agent wallets"""
    try:
        agents = company_agent_service.list_company_agents()
        
        total_agents = len(agents)
        agents_with_wallets = sum(1 for agent in agents if agent.wallet_info)
        agents_with_ens = sum(1 for agent in agents if agent.wallet_info and agent.wallet_info.ens_name)
        
        chains_used = {}
        total_balance_eth = 0.0
        
        for agent in agents:
            if agent.wallet_info:
                chain = agent.wallet_info.chain
                chains_used[chain] = chains_used.get(chain, 0) + 1
                
                try:
                    balance = float(agent.wallet_info.balance)
                    if agent.wallet_info.native_token in ['ETH']:
                        total_balance_eth += balance
                except:
                    pass
        
        return {
            "total_agents": total_agents,
            "agents_with_wallets": agents_with_wallets,
            "agents_with_ens": agents_with_ens,
            "wallet_coverage_percentage": round((agents_with_wallets / total_agents * 100), 2) if total_agents > 0 else 0,
            "ens_coverage_percentage": round((agents_with_ens / agents_with_wallets * 100), 2) if agents_with_wallets > 0 else 0,
            "chains_used": chains_used,
            "estimated_total_balance_eth": round(total_balance_eth, 6)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get wallet stats: {str(e)}")


# ENS Testing Routes

@router.get("/ens/test", response_model=ENSTestResponse)
async def test_ens_functionality(
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Test ENS functionality on Sepolia testnet"""
    try:
        test_results = await wallet_service.test_ens_functionality()
        return ENSTestResponse(**test_results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test ENS functionality: {str(e)}")


@router.post("/ens/resolve", response_model=ENSResolveResponse)
async def resolve_ens_name(
    request: ENSResolveRequest,
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Resolve an ENS name to an address on Sepolia testnet"""
    try:
        address = wallet_service.resolve_ens_name(request.ens_name)
        
        return ENSResolveResponse(
            ens_name=request.ens_name,
            address=address,
            success=address is not None,
            error=None if address else "ENS name not found or resolution failed"
        )
        
    except Exception as e:
        return ENSResolveResponse(
            ens_name=request.ens_name,
            address=None,
            success=False,
            error=str(e)
        )


@router.get("/ens/reverse/{address}")
async def reverse_resolve_address(
    address: str,
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Get ENS name for an address (reverse resolution) on Sepolia testnet"""
    try:
        ens_name = wallet_service.reverse_resolve_address(address)
        
        return {
            "address": address,
            "ens_name": ens_name,
            "success": ens_name is not None,
            "error": None if ens_name else "No ENS name found for this address"
        }
        
    except Exception as e:
        return {
            "address": address,
            "ens_name": None,
            "success": False,
            "error": str(e)
        }


@router.get("/ens/owner/{ens_name}")
async def get_ens_owner(
    ens_name: str,
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Get the owner of an ENS name on Sepolia testnet"""
    try:
        owner = wallet_service.get_ens_owner(ens_name)
        
        return {
            "ens_name": ens_name,
            "owner": owner,
            "success": owner is not None,
            "error": None if owner else "ENS name not found or no owner"
        }
        
    except Exception as e:
        return {
            "ens_name": ens_name,
            "owner": None,
            "success": False,
            "error": str(e)
        }


@router.get("/ens/resolver/{ens_name}")
async def get_ens_resolver(
    ens_name: str,
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Get the resolver address for an ENS name on Sepolia testnet"""
    try:
        resolver_address = wallet_service.get_ens_resolver(ens_name)
        
        return {
            "ens_name": ens_name,
            "resolver_address": resolver_address,
            "success": resolver_address is not None,
            "error": None if resolver_address else "ENS name not found or no resolver"
        }
        
    except Exception as e:
        return {
            "ens_name": ens_name,
            "resolver_address": None,
            "success": False,
            "error": str(e)
        }


@router.get("/ens/text/{ens_name}/{key}")
async def get_ens_text_record(
    ens_name: str,
    key: str,
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Get text record for an ENS name on Sepolia testnet"""
    try:
        text_value = wallet_service.get_ens_text_record(ens_name, key)
        
        return {
            "ens_name": ens_name,
            "key": key,
            "value": text_value,
            "success": text_value is not None,
            "error": None if text_value else f"No text record '{key}' found for ENS name"
        }
        
    except Exception as e:
        return {
            "ens_name": ens_name,
            "key": key,
            "value": None,
            "success": False,
            "error": str(e)
        }
