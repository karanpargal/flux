from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import httpx
import time
import uuid
from datetime import datetime

from ..models.agent_models import (
    RestRequest, 
    RestResponse, 
    ChatRequest, 
    ChatResponse, 
    ChatMessage,
    ChatChoice,
    ChatUsage
)
from ..services import get_company_agent_service
from ..services.company_agent_service import CompanyAgentService

router = APIRouter(prefix="/api/rest", tags=["REST API"])


@router.get("/agents/{agent_id}/get", response_model=RestResponse)
async def get_agent_info(
    agent_id: str,
    service: CompanyAgentService = Depends(get_company_agent_service)
):
    """Get information from a specific agent via REST GET"""
    try:
        # Get agent information
        agent_info = service.get_company_agent(agent_id)
        
        # Make request to agent's REST endpoint
        agent_url = f"http://localhost:{agent_info.port}/rest/get"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(agent_url)
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to agent: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent info: {str(e)}")

@router.post("/agents/{agent_id}/post", response_model=RestResponse)
async def send_message_to_agent(
    agent_id: str,
    request: RestRequest,
    service: CompanyAgentService = Depends(get_company_agent_service)
):
    """Send a message to a specific agent via REST POST"""
    try:
        agent_info = service.get_company_agent(agent_id)
        
        agent_url = f"http://localhost:{agent_info.port}/rest/post"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(agent_url, json=request.dict())
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to agent: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending message to agent: {str(e)}")

@router.post("/agents/{agent_id}/chat/completions", response_model=ChatResponse)
async def chat_with_agent(
    agent_id: str,
    request: ChatRequest,
    service: CompanyAgentService = Depends(get_company_agent_service)
):
    """Chat with a specific agent using ASI1 LLM compatible chat protocol"""
    try:
        agent_info = service.get_company_agent(agent_id)
        
        agent_url = f"http://localhost:{agent_info.port}/chat/completions"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(agent_url, json=request.dict())
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to agent: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error chatting with agent: {str(e)}")

@router.get("/agents", response_model=List[Dict[str, Any]])
async def list_agents_with_rest_info(
    service: CompanyAgentService = Depends(get_company_agent_service)
):
    """List all agents with their REST API information"""
    try:
        agents = service.list_company_agents()
        agent_info = []
        
        for agent in agents:
            agent_data = {
                "agent_id": agent.agent_id,
                "company_id": agent.company_id,
                "company_name": agent.company_name,
                "agent_name": agent.agent_name,
                "port": agent.port,
                "address": agent.address,
                "status": agent.status,
                "capabilities": agent.capabilities,
                "description": agent.description,
                "rest_endpoints": {
                    "get": f"http://localhost:{agent.port}/rest/get",
                    "post": f"http://localhost:{agent.port}/rest/post",
                    "chat": f"http://localhost:{agent.port}/chat/completions"
                }
            }
            agent_info.append(agent_data)
        
        return agent_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing agents: {str(e)}")

@router.get("/agents/{agent_id}/endpoints", response_model=Dict[str, str])
async def get_agent_endpoints(
    agent_id: str,
    service: CompanyAgentService = Depends(get_company_agent_service)
):
    """Get REST API endpoints for a specific agent"""
    try:
        agent_info = service.get_company_agent(agent_id)
        
        return {
            "agent_id": agent_info.agent_id,
            "agent_name": agent_info.agent_name,
            "company_name": agent_info.company_name,
            "base_url": f"http://localhost:{agent_info.port}",
            "endpoints": {
                "get": f"http://localhost:{agent_info.port}/rest/get",
                "post": f"http://localhost:{agent_info.port}/rest/post",
                "chat": f"http://localhost:{agent_info.port}/chat/completions"
            },
            "usage_examples": {
                "get_request": f"curl http://localhost:{agent_info.port}/rest/get",
                "post_request": f"curl -X POST -H 'Content-Type: application/json' -d '{{\"text\": \"Hello\"}}' http://localhost:{agent_info.port}/rest/post",
                "chat_request": f"curl -X POST -H 'Content-Type: application/json' -d '{{\"messages\": [{{\"role\": \"user\", \"content\": \"Hello\"}}]}}' http://localhost:{agent_info.port}/chat/completions"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent endpoints: {str(e)}")
