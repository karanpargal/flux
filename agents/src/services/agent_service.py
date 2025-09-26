import os
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from ..models.agent_models import AgentCreateRequest, AgentResponse, AgentStatusResponse
from .process_service import ProcessService


class AgentService:
    """Service for managing agent lifecycle and operations"""
    
    def __init__(self):
        self.agents_registry: Dict[str, Dict[str, Any]] = {}
        self.process_service = ProcessService()
    
    def generate_agent_code(self, agent_config: AgentCreateRequest) -> str:
        """Generate the agent Python code dynamically"""
        code = f'''from uagents import Agent, Context, Model
import sys
import os

class Message(Model):
    message: str

SEED_PHRASE = "{agent_config.seed_phrase or 'default_seed_phrase'}"

agent = Agent(
    name="{agent_config.name}",
    port={agent_config.port},
    mailbox={str(agent_config.mailbox).lower()}
)

print(f"Your agent's address is: {{agent.address}}")

if __name__ == "__main__":
    agent.run()
'''
        return code
    
    def save_agent_file(self, agent_id: str, agent_code: str) -> str:
        """Save agent code to a file"""
        filename = f"agent_{agent_id}.py"
        filepath = os.path.join(os.getcwd(), "src", "agents", filename)
        
        # Ensure agents directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            f.write(agent_code)
        
        return filepath
    
    async def create_agent(self, agent_config: AgentCreateRequest) -> AgentResponse:
        """Create a new agent"""
        try:
            # Check if port is already in use
            for agent_info in self.agents_registry.values():
                if agent_info["port"] == agent_config.port:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Port {agent_config.port} is already in use"
                    )
            
            # Generate unique agent ID
            agent_id = str(uuid.uuid4())
            
            # Generate agent code
            agent_code = self.generate_agent_code(agent_config)
            
            # Save agent file
            filepath = self.save_agent_file(agent_id, agent_code)
            
            # Start agent process
            process = self.process_service.start_agent_process(agent_id, filepath)
            
            # Wait a moment for agent to initialize
            await asyncio.sleep(2)
            
            # Check if process is still running
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                raise HTTPException(
                    status_code=500, 
                    detail=f"Agent failed to start: {stderr}"
                )
            
            # Extract agent address from output (this is a simplified approach)
            agent_address = f"agent_{agent_id}@{agent_config.name}"
            
            # Store agent information
            self.agents_registry[agent_id] = {
                "name": agent_config.name,
                "port": agent_config.port,
                "address": agent_address,
                "status": "running",
                "created_at": datetime.now().isoformat(),
                "process_id": process.pid,
                "filepath": filepath,
                "seed_phrase": agent_config.seed_phrase,
                "mailbox": agent_config.mailbox
            }
            
            return AgentResponse(
                agent_id=agent_id,
                name=agent_config.name,
                port=agent_config.port,
                address=agent_address,
                status="running",
                created_at=datetime.now().isoformat(),
                process_id=process.pid
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")
    
    def list_agents(self) -> List[AgentResponse]:
        """List all agents"""
        agents = []
        for agent_id, agent_info in self.agents_registry.items():
            # Check if process is still running
            if agent_info.get("process_id"):
                if self.process_service.is_process_running(agent_info["process_id"]):
                    agent_info["status"] = "running"
                else:
                    agent_info["status"] = "stopped"
            
            agents.append(AgentResponse(
                agent_id=agent_id,
                name=agent_info["name"],
                port=agent_info["port"],
                address=agent_info["address"],
                status=agent_info["status"],
                created_at=agent_info["created_at"],
                process_id=agent_info.get("process_id")
            ))
        
        return agents
    
    def get_agent(self, agent_id: str) -> AgentResponse:
        """Get specific agent information"""
        if agent_id not in self.agents_registry:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent_info = self.agents_registry[agent_id]
        
        # Check if process is still running
        if agent_info.get("process_id"):
            if self.process_service.is_process_running(agent_info["process_id"]):
                agent_info["status"] = "running"
            else:
                agent_info["status"] = "stopped"
        
        return AgentResponse(
            agent_id=agent_id,
            name=agent_info["name"],
            port=agent_info["port"],
            address=agent_info["address"],
            status=agent_info["status"],
            created_at=agent_info["created_at"],
            process_id=agent_info.get("process_id")
        )
    
    def delete_agent(self, agent_id: str) -> Dict[str, str]:
        """Delete an agent"""
        if agent_id not in self.agents_registry:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent_info = self.agents_registry[agent_id]
        
        # Stop the agent process if running
        if agent_info.get("process_id") and self.process_service.is_process_running(agent_info["process_id"]):
            self.process_service.stop_agent_process(agent_info["process_id"])
        
        # Remove agent file
        if "filepath" in agent_info and os.path.exists(agent_info["filepath"]):
            os.remove(agent_info["filepath"])
        
        # Remove from registry
        del self.agents_registry[agent_id]
        
        return {"message": f"Agent {agent_id} deleted successfully"}
    
    async def start_agent(self, agent_id: str) -> Dict[str, str]:
        """Start a stopped agent"""
        if agent_id not in self.agents_registry:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent_info = self.agents_registry[agent_id]
        
        # Check if already running
        if agent_info.get("process_id") and self.process_service.is_process_running(agent_info["process_id"]):
            raise HTTPException(status_code=400, detail="Agent is already running")
        
        try:
            # Start agent process
            process = self.process_service.start_agent_process(agent_id, agent_info["filepath"])
            
            # Update registry
            agent_info["process_id"] = process.pid
            agent_info["status"] = "running"
            
            return {"message": f"Agent {agent_id} started successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to start agent: {str(e)}")
    
    def stop_agent(self, agent_id: str) -> Dict[str, str]:
        """Stop a running agent"""
        if agent_id not in self.agents_registry:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent_info = self.agents_registry[agent_id]
        
        if not agent_info.get("process_id") or not self.process_service.is_process_running(agent_info["process_id"]):
            raise HTTPException(status_code=400, detail="Agent is not running")
        
        try:
            # Stop agent process
            success = self.process_service.stop_agent_process(agent_info["process_id"])
            
            if success:
                agent_info["status"] = "stopped"
                agent_info["process_id"] = None
                return {"message": f"Agent {agent_id} stopped successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to stop agent")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to stop agent: {str(e)}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all agents"""
        active_count = 0
        agent_statuses = []
        
        for agent_id, agent_info in self.agents_registry.items():
            status = "stopped"
            uptime = None
            
            if agent_info.get("process_id") and self.process_service.is_process_running(agent_info["process_id"]):
                status = "running"
                active_count += 1
                uptime = self.process_service.get_process_uptime(agent_info["process_id"])
            
            agent_statuses.append(AgentStatusResponse(
                agent_id=agent_id,
                name=agent_info["name"],
                status=status,
                port=agent_info["port"],
                address=agent_info["address"],
                process_id=agent_info.get("process_id"),
                uptime=uptime
            ))
        
        return {
            "status": "healthy",
            "total_agents": len(self.agents_registry),
            "active_agents": active_count,
            "agents": agent_statuses
        }
