from fastapi import APIRouter, Depends, BackgroundTasks
from typing import List

from ..models.agent_models import AgentCreateRequest, AgentResponse
from ..services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["agents"])


def get_agent_service() -> AgentService:
    """Dependency to get agent service instance"""
    return AgentService()


@router.post("", response_model=AgentResponse)
async def create_agent(
    agent_config: AgentCreateRequest, 
    background_tasks: BackgroundTasks,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Create a new agent"""
    return await agent_service.create_agent(agent_config)


@router.get("", response_model=List[AgentResponse])
async def list_agents(agent_service: AgentService = Depends(get_agent_service)):
    """List all agents"""
    return agent_service.list_agents()


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str, 
    agent_service: AgentService = Depends(get_agent_service)
):
    """Get specific agent information"""
    return agent_service.get_agent(agent_id)


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str, 
    agent_service: AgentService = Depends(get_agent_service)
):
    """Delete an agent"""
    return agent_service.delete_agent(agent_id)


@router.post("/{agent_id}/start")
async def start_agent(
    agent_id: str, 
    agent_service: AgentService = Depends(get_agent_service)
):
    """Start a stopped agent"""
    return await agent_service.start_agent(agent_id)


@router.post("/{agent_id}/stop")
async def stop_agent(
    agent_id: str, 
    agent_service: AgentService = Depends(get_agent_service)
):
    """Stop a running agent"""
    return agent_service.stop_agent(agent_id)
