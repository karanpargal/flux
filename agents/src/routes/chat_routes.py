from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import httpx
import asyncio

from ..models.agent_models import (
    ChatRequest, 
    ChatResponse, 
    ChatMessage,
    CompanyAgentResponse
)
from ..services import get_company_agent_service
from ..services.company_agent_service import CompanyAgentService

router = APIRouter(prefix="/chat", tags=["chat"])




@router.post("/completions", response_model=ChatResponse)
async def chat_completion(
    agent_id: str,
    chat_request: ChatRequest,
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service)
):
    """
    Central chat completion endpoint that routes requests to specific agents.
    Send agent_id as a query parameter to specify which agent to use.
    """
    try:
        # Get agent information
        agent_info = company_agent_service.get_company_agent(agent_id)
        
        if agent_info.status != "running":
            raise HTTPException(
                status_code=400, 
                detail=f"Agent {agent_id} is not running. Status: {agent_info.status}"
            )
        
        # Prepare the request for the specific agent
        agent_url = f"http://localhost:{agent_info.port}/chat/completions"
        
        # Convert ChatMessage objects to dictionaries for the agent
        messages_data = []
        for msg in chat_request.messages:
            messages_data.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Prepare request payload for the agent
        agent_request = {
            "messages": messages_data,
            "model": chat_request.model or "asi1-mini",
            "temperature": chat_request.temperature or 0.7,
            "max_tokens": chat_request.max_tokens or 1000,
            "stream": chat_request.stream or False
        }
        
        # Send request to the specific agent
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(agent_url, json=agent_request)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Agent {agent_id} returned error: {response.text}"
                )
            
            agent_response = response.json()
            
            # Convert agent response to our ChatResponse format
            return ChatResponse(
                id=agent_response.get("id", ""),
                created=agent_response.get("created", 0),
                model=agent_response.get("model", chat_request.model or "asi1-mini"),
                choices=agent_response.get("choices", []),
                usage=agent_response.get("usage", {})
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat completion: {str(e)}"
        )


@router.get("/agents", response_model=List[CompanyAgentResponse])
async def list_available_agents(
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service)
):
    """List all available agents for chat completion"""
    return company_agent_service.list_company_agents()


@router.get("/agents/{agent_id}", response_model=CompanyAgentResponse)
async def get_agent_info(
    agent_id: str,
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service)
):
    """Get information about a specific agent"""
    return company_agent_service.get_company_agent(agent_id)
