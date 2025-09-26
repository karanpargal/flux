from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import subprocess
import os
import signal
import psutil
import json
import sys
from datetime import datetime
import uuid

app = FastAPI(
    title="Multi-Agent Management Server",
    description="A FastAPI server for creating and managing multiple uAgents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for agent information
agents_registry: Dict[str, Dict[str, Any]] = {}

class AgentCreateRequest(BaseModel):
    name: str
    port: int
    seed_phrase: Optional[str] = None
    mailbox: bool = True
    endpoint: Optional[List[str]] = None

class AgentResponse(BaseModel):
    agent_id: str
    name: str
    port: int
    address: str
    status: str
    created_at: str
    process_id: Optional[int] = None

class AgentStatusResponse(BaseModel):
    agent_id: str
    name: str
    status: str
    port: int
    address: str
    process_id: Optional[int] = None
    uptime: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    total_agents: int
    active_agents: int
    agents: List[AgentStatusResponse]

def generate_agent_code(agent_config: AgentCreateRequest) -> str:
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

def save_agent_file(agent_id: str, agent_code: str) -> str:
    """Save agent code to a file"""
    filename = f"agent_{agent_id}.py"
    filepath = os.path.join(os.getcwd(), "agents", filename)
    
    # Ensure agents directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w') as f:
        f.write(agent_code)
    
    return filepath

def start_agent_process(agent_id: str, filepath: str) -> subprocess.Popen:
    """Start the agent process"""
    try:
        process = subprocess.Popen(
            [sys.executable, filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return process
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start agent: {str(e)}")

def stop_agent_process(process_id: int) -> bool:
    """Stop the agent process"""
    try:
        if psutil.pid_exists(process_id):
            process = psutil.Process(process_id)
            process.terminate()
            process.wait(timeout=5)
            return True
        return False
    except Exception:
        return False

@app.post("/agents", response_model=AgentResponse)
async def create_agent(agent_config: AgentCreateRequest, background_tasks: BackgroundTasks):
    """Create a new agent"""
    try:
        # Check if port is already in use
        for agent_info in agents_registry.values():
            if agent_info["port"] == agent_config.port:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Port {agent_config.port} is already in use"
                )
        
        # Generate unique agent ID
        agent_id = str(uuid.uuid4())
        
        # Generate agent code
        agent_code = generate_agent_code(agent_config)
        
        # Save agent file
        filepath = save_agent_file(agent_id, agent_code)
        
        # Start agent process
        process = start_agent_process(agent_id, filepath)
        
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
        agents_registry[agent_id] = {
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

@app.get("/agents", response_model=List[AgentResponse])
async def list_agents():
    """List all agents"""
    agents = []
    for agent_id, agent_info in agents_registry.items():
        # Check if process is still running
        if agent_info.get("process_id"):
            if psutil.pid_exists(agent_info["process_id"]):
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

@app.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get specific agent information"""
    if agent_id not in agents_registry:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent_info = agents_registry[agent_id]
    
    # Check if process is still running
    if agent_info.get("process_id"):
        if psutil.pid_exists(agent_info["process_id"]):
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

@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent"""
    if agent_id not in agents_registry:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent_info = agents_registry[agent_id]
    
    # Stop the agent process if running
    if agent_info.get("process_id") and psutil.pid_exists(agent_info["process_id"]):
        stop_agent_process(agent_info["process_id"])
    
    # Remove agent file
    if "filepath" in agent_info and os.path.exists(agent_info["filepath"]):
        os.remove(agent_info["filepath"])
    
    # Remove from registry
    del agents_registry[agent_id]
    
    return {"message": f"Agent {agent_id} deleted successfully"}

@app.post("/agents/{agent_id}/start")
async def start_agent(agent_id: str):
    """Start a stopped agent"""
    if agent_id not in agents_registry:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent_info = agents_registry[agent_id]
    
    # Check if already running
    if agent_info.get("process_id") and psutil.pid_exists(agent_info["process_id"]):
        raise HTTPException(status_code=400, detail="Agent is already running")
    
    try:
        # Start agent process
        process = start_agent_process(agent_id, agent_info["filepath"])
        
        # Update registry
        agent_info["process_id"] = process.pid
        agent_info["status"] = "running"
        
        return {"message": f"Agent {agent_id} started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start agent: {str(e)}")

@app.post("/agents/{agent_id}/stop")
async def stop_agent(agent_id: str):
    """Stop a running agent"""
    if agent_id not in agents_registry:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent_info = agents_registry[agent_id]
    
    if not agent_info.get("process_id") or not psutil.pid_exists(agent_info["process_id"]):
        raise HTTPException(status_code=400, detail="Agent is not running")
    
    try:
        # Stop agent process
        success = stop_agent_process(agent_info["process_id"])
        
        if success:
            agent_info["status"] = "stopped"
            agent_info["process_id"] = None
            return {"message": f"Agent {agent_id} stopped successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to stop agent")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop agent: {str(e)}")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Get health status of all agents"""
    active_count = 0
    agent_statuses = []
    
    for agent_id, agent_info in agents_registry.items():
        status = "stopped"
        uptime = None
        
        if agent_info.get("process_id") and psutil.pid_exists(agent_info["process_id"]):
            status = "running"
            active_count += 1
            # Calculate uptime
            try:
                process = psutil.Process(agent_info["process_id"])
                uptime_seconds = datetime.now().timestamp() - process.create_time()
                uptime = f"{int(uptime_seconds)}s"
            except:
                uptime = "unknown"
        
        agent_statuses.append(AgentStatusResponse(
            agent_id=agent_id,
            name=agent_info["name"],
            status=status,
            port=agent_info["port"],
            address=agent_info["address"],
            process_id=agent_info.get("process_id"),
            uptime=uptime
        ))
    
    return HealthResponse(
        status="healthy",
        total_agents=len(agents_registry),
        active_agents=active_count,
        agents=agent_statuses
    )

@app.get("/")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
