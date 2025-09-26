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
        self.port_mapping: Dict[str, int] = {}
        self.next_port = 8001
    
    def get_next_available_port(self) -> int:
        """Get the next available port starting from 8001"""
        port = self.next_port
        self.next_port += 1
        return port
    
    def generate_agent_code(self, agent_config: AgentCreateRequest) -> str:
        """Generate the agent Python code dynamically with chat protocol"""
        code = f'''from datetime import datetime
from uuid import uuid4
import os
import time
from typing import Dict, Any, List
from dotenv import load_dotenv
from openai import OpenAI
from uagents import Context, Protocol, Agent, Model
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    TextContent,
    chat_protocol_spec,
)

load_dotenv()
client = OpenAI(
    base_url='https://api.asi1.ai/v1',
    api_key=os.getenv("ASI_API_KEY"),  
)

# REST API Models
class RestRequest(Model):
    text: str
    metadata: Dict[str, Any] = {{}}

class RestResponse(Model):
    timestamp: int
    text: str
    agent_address: str
    status: str = "success"
    metadata: Dict[str, Any] = {{}}

# Chat Protocol Models for ASI1 LLM
class ChatRequest(Model):
    messages: List[Dict[str, Any]]
    model: str = "asi1-mini"
    temperature: float = 0.7
    max_tokens: int = 1000
    stream: bool = False

class ChatResponse(Model):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, Any] = {{}}

SEED_PHRASE = "{agent_config.seed_phrase or 'default_seed_phrase'}"

# Agent configuration
class AgentConfig:
    def __init__(self):
        self.capabilities = ['general_assistance', 'chat', 'information_retrieval']

agent_config = AgentConfig()

agent = Agent(
    name="{agent_config.name}",
    seed=SEED_PHRASE,
    port={agent_config.port},
    mailbox={str(agent_config.mailbox).lower()},
)

protocol = Protocol(spec=chat_protocol_spec)

@protocol.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(), acknowledged_msg_id=msg.msg_id),
    )
    text = ""
    for item in msg.content:
        if isinstance(item, TextContent):
            text += item.text

    response = "Sorry, I wasn't able to process that."
    try:
        r = client.chat.completions.create(
            model="asi1-mini",
            messages=[
                {{"role": "system", "content": "You are a helpful AI assistant. Answer user queries clearly and politely."}},
                {{"role": "user", "content": text}},
            ],
            max_tokens=2048,
        )
        response = str(r.choices[0].message.content)
    except:
        ctx.logger.exception("Error querying model")

    await ctx.send(sender, ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[
            TextContent(type="text", text=response),
            EndSessionContent(type="end-session"),
        ]
    ))

@protocol.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    pass

# REST API Endpoints
@agent.on_rest_get("/rest/get", RestResponse)
async def handle_rest_get(ctx: Context) -> Dict[str, Any]:
    """Handle GET requests to the agent"""
    ctx.logger.info("Received GET request")
    return {{
        "timestamp": int(time.time()),
        "text": f"Hello from {{agent_config.name}}!",
        "agent_address": ctx.agent.address,
        "status": "success",
        "metadata": {{
            "agent_name": "{agent_config.name}"
        }}
    }}

@agent.on_rest_post("/rest/post", RestRequest, RestResponse)
async def handle_rest_post(ctx: Context, req: RestRequest) -> RestResponse:
    """Handle POST requests to the agent"""
    ctx.logger.info("Received POST request")
    try:
        # Process the request using ASI1 LLM
        response_text = await process_request(req.text)
        
        return RestResponse(
            timestamp=int(time.time()),
            text=response_text,
            agent_address=ctx.agent.address,
            status="success",
            metadata={{
                "agent_name": "{agent_config.name}"
            }}
        )
    except Exception as e:
        return RestResponse(
            timestamp=int(time.time()),
            text=f"Error processing request: {{str(e)}}",
            agent_address=ctx.agent.address,
            status="error",
            metadata={{"error": str(e)}}
        )

# Chat Protocol Endpoints for ASI1 LLM
@agent.on_rest_post("/chat/completions", ChatRequest, ChatResponse)
async def handle_chat_completions(ctx: Context, req: ChatRequest) -> ChatResponse:
    """Handle chat completions for ASI1 LLM compatibility"""
    ctx.logger.info("Received chat completion request")
    try:
        # Process the chat messages
        response_content = await process_chat_messages(req.messages, req.model)
        
        return ChatResponse(
            id=str(uuid4()),
            created=int(time.time()),
            model=req.model,
            choices=[{{
                "index": 0,
                "message": {{
                    "role": "assistant",
                    "content": response_content
                }},
                "finish_reason": "stop"
            }}],
            usage={{
                "prompt_tokens": len(str(req.messages)),
                "completion_tokens": len(response_content),
                "total_tokens": len(str(req.messages)) + len(response_content)
            }}
        )
    except Exception as e:
        error_message = f"Error processing chat request: {{str(e)}}"
        return ChatResponse(
            id=str(uuid4()),
            created=int(time.time()),
            model=req.model,
            choices=[{{
                "index": 0,
                "message": {{
                    "role": "assistant",
                    "content": error_message
                }},
                "finish_reason": "stop"
            }}],
            usage={{"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}}
        )

async def process_request(message: str) -> str:
    """Process requests using ASI1 LLM"""
    try:
        r = client.chat.completions.create(
            model="asi1-mini",
            messages=[
                {{"role": "system", "content": "You are a helpful AI assistant. Answer user queries clearly and politely."}},
                {{"role": "user", "content": message}},
            ],
            max_tokens=2048,
        )
        return str(r.choices[0].message.content)
    except Exception as e:
        return f"Error processing request: {{str(e)}}"

async def process_chat_messages(messages: List[Dict[str, Any]], model: str) -> str:
    """Process chat messages for ASI1 LLM compatibility"""
    try:
        # Add system message
        system_message = {{
            "role": "system", 
            "content": "You are a helpful AI assistant. Answer user queries clearly and politely."
        }}
        
        # Combine system message with user messages
        all_messages = [system_message] + messages
        
        r = client.chat.completions.create(
            model=model,
            messages=all_messages,
            max_tokens=2048,
        )
        return str(r.choices[0].message.content)
    except Exception as e:
        return f"Error processing chat request: {{str(e)}}"

agent.include(protocol, publish_manifest=True)

print(f"Your agent's address is: {{agent.address}}")

if __name__ == "__main__":
    agent.run()
'''
        return code
    
    def save_agent_file(self, agent_id: str, agent_code: str) -> str:
        """Save agent code to a file in its own folder"""
        # Create agent-specific folder
        agent_folder = os.path.join(os.getcwd(), "src", "agents", f"agent_{agent_id}")
        os.makedirs(agent_folder, exist_ok=True)
        
        filename = f"agent_{agent_id}.py"
        filepath = os.path.join(agent_folder, filename)
        
        with open(filepath, 'w') as f:
            f.write(agent_code)
        
        return filepath
    
    async def create_agent(self, agent_config: AgentCreateRequest) -> AgentResponse:
        """Create a new agent"""
        try:
            agent_id = str(uuid.uuid4())
            
            # Get next available port (use provided port or assign new one)
            if agent_config.port is None:
                assigned_port = self.get_next_available_port()
                agent_config.port = assigned_port
            else:
                assigned_port = agent_config.port
            
            self.port_mapping[agent_id] = assigned_port
            
            agent_code = self.generate_agent_code(agent_config)
            
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
        
        # Remove agent folder and all files
        if "filepath" in agent_info:
            agent_folder = os.path.dirname(agent_info["filepath"])
            if os.path.exists(agent_folder):
                import shutil
                shutil.rmtree(agent_folder)
        
        # Remove from port mapping
        if agent_id in self.port_mapping:
            del self.port_mapping[agent_id]
        
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
