from fastapi import APIRouter, Depends
from typing import Dict, Any

from ..models.agent_models import HealthResponse
from ..services.agent_service import AgentService

router = APIRouter(tags=["health"])


def get_agent_service() -> AgentService:
    """Dependency to get agent service instance"""
    return AgentService()


@router.get("/health", response_model=HealthResponse)
async def health_check(agent_service: AgentService = Depends(get_agent_service)):
    """Get health status of all agents"""
    health_data = agent_service.get_health_status()
    return HealthResponse(**health_data)


@router.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Multi-Agent Management Server",
        "version": "1.0.0",
        "endpoints": {
            "create_agent": "POST /agents",
            "list_agents": "GET /agents",
            "get_agent": "GET /agents/{agent_id}",
            "delete_agent": "DELETE /agents/{agent_id}",
            "start_agent": "POST /agents/{agent_id}/start",
            "stop_agent": "POST /agents/{agent_id}/stop",
            "health_check": "GET /health"
        }
    }
