from fastapi import APIRouter, Depends
from typing import Dict, Any

from ..models.agent_models import CompanyHealthResponse
from ..services import get_company_agent_service
from ..services.company_agent_service import CompanyAgentService

router = APIRouter(tags=["health"])


@router.get("/health", response_model=CompanyHealthResponse)
async def health_check(company_agent_service: CompanyAgentService = Depends(get_company_agent_service)):
    """Get health status of all company agents"""
    health_data = company_agent_service.get_company_health_status()
    return CompanyHealthResponse(**health_data)


@router.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Company Agent Management Server",
        "version": "1.0.0",
        "endpoints": {
            "create_company_agent": "POST /company-agents",
            "list_company_agents": "GET /company-agents",
            "get_company_agent": "GET /company-agents/{agent_id}",
            "delete_company_agent": "DELETE /company-agents/{agent_id}",
            "discover_agents": "POST /company-agents/discover",
            "send_message": "POST /company-agents/send-message",
            "chat_completion": "POST /chat/completions?agent_id={agent_id}",
            "list_available_agents": "GET /chat/agents",
            "get_agent_info": "GET /chat/agents/{agent_id}",
            "health_check": "GET /health"
        }
    }
