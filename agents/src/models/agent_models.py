from pydantic import BaseModel
from typing import List, Optional


class AgentCreateRequest(BaseModel):
    """Request model for creating a new agent"""
    name: str
    port: int
    seed_phrase: Optional[str] = None
    mailbox: bool = True
    endpoint: Optional[List[str]] = None


class AgentResponse(BaseModel):
    """Response model for agent information"""
    agent_id: str
    name: str
    port: int
    address: str
    status: str
    created_at: str
    process_id: Optional[int] = None


class AgentStatusResponse(BaseModel):
    """Response model for agent status information"""
    agent_id: str
    name: str
    status: str
    port: int
    address: str
    process_id: Optional[int] = None
    uptime: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    total_agents: int
    active_agents: int
    agents: List[AgentStatusResponse]


class Message(BaseModel):
    """Model for agent messages"""
    message: str
