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
    OpenAI-compatible chat completion endpoint with ASI:One features.
    
    Features:
    - Full OpenAI API compatibility (temperature, top_p, frequency_penalty, etc.)
    - ASI:One model support (asi1-fast, asi1-extended, asi1-agentic, etc.)
    - Session support for agentic models via x-session-id header
    - Web search capabilities via extra_body parameter
    - Enhanced response with executable_data, intermediate_steps, and thought
    
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
        
        agent_request = {
            "messages": messages_data,
            "model": chat_request.model or "asi1-fast",
            "temperature": chat_request.temperature or 0.2,
            "max_tokens": chat_request.max_tokens or 1000,
            "top_p": getattr(chat_request, 'top_p', 1.0),
            "frequency_penalty": getattr(chat_request, 'frequency_penalty', 0.0),
            "presence_penalty": getattr(chat_request, 'presence_penalty', 0.0),
            "stream": chat_request.stream or False,
            "web_search": getattr(chat_request, 'web_search', False),
            "extra_body": getattr(chat_request, 'extra_body', {}),
            "extra_headers": getattr(chat_request, 'extra_headers', {})
        }
        
        request_headers = {"Content-Type": "application/json"}
        
        if hasattr(chat_request, 'extra_headers') and chat_request.extra_headers:
            session_id = chat_request.extra_headers.get("x-session-id")
            if session_id:
                request_headers["x-session-id"] = session_id
        
        # Send request to the specific agent
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(agent_url, json=agent_request, headers=request_headers)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Agent {agent_id} returned error: {response.text}"
                )
            
            agent_response = response.json()
            
            # Convert agent response to our ChatResponse format with ASI:One fields
            return ChatResponse(
                id=agent_response.get("id", ""),
                created=agent_response.get("created", 0),
                model=agent_response.get("model", chat_request.model or "asi1-fast"),
                choices=agent_response.get("choices", []),
                usage=agent_response.get("usage", {}),
                executable_data=agent_response.get("executable_data", {}),
                intermediate_steps=agent_response.get("intermediate_steps", []),
                thought=agent_response.get("thought", "")
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


@router.get("/agents/{agent_id}/models")
async def get_agent_models(
    agent_id: str,
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service)
):
    """Get available models information from a specific agent"""
    try:
        # Get agent information
        agent_info = company_agent_service.get_company_agent(agent_id)
        
        if agent_info.status != "running":
            raise HTTPException(
                status_code=400, 
                detail=f"Agent {agent_id} is not running. Status: {agent_info.status}"
            )
        
        # Get models information from the agent
        agent_url = f"http://localhost:{agent_info.port}/models"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(agent_url)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Agent {agent_id} returned error: {response.text}"
                )
            
            return response.json()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get models from agent {agent_id}: {str(e)}"
        )


@router.get("/models")
async def get_all_available_models(
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service)
):
    """Get available models from all running agents"""
    try:
        agents = company_agent_service.list_company_agents()
        running_agents = [agent for agent in agents if agent.status == "running"]
        
        if not running_agents:
            raise HTTPException(
                status_code=404,
                detail="No running agents available"
            )
        
        # Get models from the first running agent (they should all have the same models)
        first_agent = running_agents[0]
        agent_url = f"http://localhost:{first_agent.port}/models"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(agent_url)
            
            if response.status_code != 200:
                # Fallback to basic model information
                return {
                    "timestamp": int(asyncio.get_event_loop().time()),
                    "text": "Available ASI:One models for OpenAI-compatible API",
                    "status": "success",
                    "metadata": {
                        "models": {
                            "asi1-mini": {"description": "Fast responses, general chat"},
                            "asi1-fast": {"description": "Ultra-low latency"},
                            "asi1-extended": {"description": "Complex reasoning"},
                            "asi1-agentic": {"description": "Agent orchestration"},
                            "asi1-fast-agentic": {"description": "Real-time agents"},
                            "asi1-extended-agentic": {"description": "Complex workflows"},
                            "asi1-graph": {"description": "Data visualization"}
                        },
                        "default_model": "asi1-fast",
                        "available_agents": len(running_agents)
                    }
                }
            
            agent_response = response.json()
            # Add information about available agents
            if "metadata" in agent_response:
                agent_response["metadata"]["available_agents"] = len(running_agents)
                agent_response["metadata"]["running_agents"] = [
                    {
                        "agent_id": agent.agent_id,
                        "company_name": agent.company_name,
                        "agent_name": agent.agent_name,
                        "port": agent.port
                    } for agent in running_agents
                ]
            
            return agent_response
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get available models: {str(e)}"
        )
