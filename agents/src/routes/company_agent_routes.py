from fastapi import APIRouter, Depends, BackgroundTasks
from typing import List

from ..models.agent_models import (
    CompanyAgentCreateRequest, 
    CompanyAgentResponse,
    AgentDiscoveryRequest,
    AgentDiscoveryResponse,
    AgentMessageRequest,
    AgentMessageResponse
)
from ..services import get_company_agent_service
from ..services.company_agent_service import CompanyAgentService

router = APIRouter(prefix="/company-agents", tags=["company-agents"])


@router.post("", response_model=CompanyAgentResponse)
async def create_company_agent(
    agent_config: CompanyAgentCreateRequest, 
    background_tasks: BackgroundTasks,
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service)
):
    """Create a new company-specific agent with mailbox agent"""
    return await company_agent_service.create_company_agent(agent_config)


@router.get("", response_model=List[CompanyAgentResponse])
async def list_company_agents(
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service)
):
    """List all company agents"""
    return company_agent_service.list_company_agents()


@router.get("/{agent_id}", response_model=CompanyAgentResponse)
async def get_company_agent(
    agent_id: str, 
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service)
):
    """Get specific company agent information"""
    return company_agent_service.get_company_agent(agent_id)


@router.delete("/{agent_id}")
async def delete_company_agent(
    agent_id: str, 
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service)
):
    """Delete a company agent and its mailbox agent"""
    return await company_agent_service.delete_company_agent(agent_id)


@router.post("/discover", response_model=AgentDiscoveryResponse)
async def discover_agents(
    discovery_request: AgentDiscoveryRequest,
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service)
):
    """Discover agents by capability"""
    return await company_agent_service.discover_agents(discovery_request)


@router.post("/send-message", response_model=AgentMessageResponse)
async def send_message_to_agent(
    message_request: AgentMessageRequest,
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service)
):
    """Send a message to a specific agent"""
    return await company_agent_service.send_message_to_agent(message_request)


@router.get("/company/{company_id}", response_model=List[CompanyAgentResponse])
async def get_company_agents(
    company_id: str,
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service)
):
    """Get all agents for a specific company"""
    all_agents = company_agent_service.list_company_agents()
    return [agent for agent in all_agents if agent.company_id == company_id]


@router.get("/health/status")
async def get_company_agents_health(
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service)
):
    """Get health status of all company agents"""
    return company_agent_service.get_company_health_status()
