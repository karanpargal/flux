import os
import uuid
import asyncio
import httpx
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from ..models.agent_models import (
    CompanyAgentCreateRequest, 
    CompanyAgentResponse, 
    CompanyAgentStatusResponse,
    AgentDiscoveryRequest,
    AgentDiscoveryResponse,
    AgentMessageRequest,
    AgentMessageResponse,
    MailboxMessage
)
from .process_service import ProcessService
from ..config import get_settings


class CompanyAgentService:
    """Service for managing company-specific agents"""
    
    def __init__(self):
        self.company_agents_registry: Dict[str, Dict[str, Any]] = {}
        self.process_service = ProcessService()
        self.settings = get_settings()
        self.client = httpx.AsyncClient(timeout=30.0)
        self.port_mapping: Dict[str, int] = {}
        self.next_port = 8001
    
    def get_next_available_port(self) -> int:
        """Get the next available port starting from 8001"""
        port = self.next_port
        self.next_port += 1
        return port
    
    def generate_company_agent_code(self, agent_config: CompanyAgentCreateRequest) -> str:
        """Generate the company agent Python code with chat protocol"""
        webhook_url = agent_config.webhook_url or f"http://localhost:{agent_config.port}/webhook"
        
        code = f'''from datetime import datetime
from uuid import uuid4
import os
import json
import httpx
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
    sender_company_id: str = None
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
COMPANY_ID = "{agent_config.company_id}"
COMPANY_NAME = "{agent_config.company_name}"
AGENT_NAME = "{agent_config.agent_name}"
WEBHOOK_URL = "{webhook_url}"

# Agent configuration
class AgentConfig:
    def __init__(self):
        self.capabilities = {agent_config.capabilities}

agent_config = AgentConfig()

agent = Agent(
    name="{agent_config.agent_name}",
    seed=SEED_PHRASE,
    port={agent_config.port},
    mailbox=True,
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
                {{"role": "system", "content": f"You are a helpful AI assistant for {{COMPANY_NAME}}. You handle {{', '.join(agent_config.capabilities)}} requests. Answer user queries clearly and politely."}},
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

@agent.on_rest_get("/rest/get", RestResponse)
async def handle_rest_get(ctx: Context) -> Dict[str, Any]:
    """Handle GET requests to the agent"""
    ctx.logger.info("Received GET request")
    return {{
        "timestamp": int(time.time()),
        "text": f"Hello from {{AGENT_NAME}} for {{COMPANY_NAME}}!",
        "agent_address": ctx.agent.address,
        "status": "success",
        "metadata": {{
            "company_id": COMPANY_ID,
            "company_name": COMPANY_NAME,
            "agent_name": AGENT_NAME,
            "capabilities": {agent_config.capabilities}
        }}
    }}

@agent.on_rest_post("/rest/post", RestRequest, RestResponse)
async def handle_rest_post(ctx: Context, req: RestRequest) -> RestResponse:
    """Handle POST requests to the agent"""
    ctx.logger.info("Received POST request")
    try:
        # Process the request using ASI1 LLM
        response_text = await process_company_request(req.text, req.sender_company_id)
        
        return RestResponse(
            timestamp=int(time.time()),
            text=response_text,
            agent_address=ctx.agent.address,
            status="success",
            metadata={{
                "company_id": COMPANY_ID,
                "company_name": COMPANY_NAME,
                "agent_name": AGENT_NAME,
                "sender_company_id": req.sender_company_id
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

async def process_company_request(message: str, sender_company_id: str) -> str:
    """Process company-specific requests using ASI1 LLM"""
    try:
        r = client.chat.completions.create(
            model="asi1-mini",
            messages=[
                {{"role": "system", "content": f"You are a helpful AI assistant for {{COMPANY_NAME}}. You handle {{', '.join(agent_config.capabilities)}} requests. Answer user queries clearly and politely."}},
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
        # Add system message for company context
        system_message = {{
            "role": "system", 
            "content": f"You are a helpful AI assistant for {{COMPANY_NAME}}. You handle {{', '.join(agent_config.capabilities)}} requests. Answer user queries clearly and politely."
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

async def send_webhook_notification(response: str, sender_company_id: str):
    """Send webhook notification to company's system"""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(WEBHOOK_URL, json={{
                "response": response,
                "sender_company_id": sender_company_id,
                "company_id": COMPANY_ID,
                "timestamp": datetime.now().isoformat()
            }})
    except Exception as e:
        print(f"Webhook notification failed: {{e}}")

agent.include(protocol, publish_manifest=True)

print(f"Company Agent {{agent.address}} for {{COMPANY_NAME}} is ready")

if __name__ == "__main__":
    agent.run()
'''
        return code
    
    
    
    async def create_company_agent(self, agent_config: CompanyAgentCreateRequest) -> CompanyAgentResponse:
        """Create a new company-specific agent"""
        try:
            agent_id = str(uuid.uuid4())
            
            if agent_config.port is None:
                assigned_port = self.get_next_available_port()
                agent_config.port = assigned_port
            else:
                assigned_port = agent_config.port
            
            self.port_mapping[agent_id] = assigned_port
            
            agent_code = self.generate_company_agent_code(agent_config)
            
            filepath = self.save_company_agent_file(agent_id, agent_code)
            
            process = self.process_service.start_agent_process(agent_id, filepath)
            
            await asyncio.sleep(3)
            
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                raise HTTPException(
                    status_code=500, 
                    detail=f"Company agent failed to start: {stderr}"
                )
            
            agent_address = f"agent_{agent_id}@{agent_config.agent_name}"
            
            
            self.company_agents_registry[agent_id] = {
                "company_id": agent_config.company_id,
                "company_name": agent_config.company_name,
                "agent_name": agent_config.agent_name,
                "port": agent_config.port,
                "address": agent_address,
                "status": "running",
                "created_at": datetime.now().isoformat(),
                "process_id": process.pid,
                "filepath": filepath,
                "seed_phrase": agent_config.seed_phrase,
                "capabilities": agent_config.capabilities,
                "description": agent_config.description,
                "webhook_url": agent_config.webhook_url
            }
            
            return CompanyAgentResponse(
                agent_id=agent_id,
                company_id=agent_config.company_id,
                company_name=agent_config.company_name,
                agent_name=agent_config.agent_name,
                port=agent_config.port,
                address=agent_address,
                status="running",
                created_at=datetime.now().isoformat(),
                process_id=process.pid,
                capabilities=agent_config.capabilities,
                description=agent_config.description,
                webhook_url=agent_config.webhook_url
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create company agent: {str(e)}")
    
    
    def save_company_agent_file(self, agent_id: str, agent_code: str) -> str:
        """Save company agent code to a file in its own folder"""
        agent_folder = os.path.join(os.getcwd(), self.settings.company_agents_directory, f"agent_{agent_id}")
        os.makedirs(agent_folder, exist_ok=True)
        
        filename = f"company_agent_{agent_id}.py"
        filepath = os.path.join(agent_folder, filename)
        
        with open(filepath, 'w') as f:
            f.write(agent_code)
        
        return filepath
    
    
    def list_company_agents(self) -> List[CompanyAgentResponse]:
        """List all company agents"""
        agents = []
        for agent_id, agent_info in self.company_agents_registry.items():
            # Check if process is still running
            if agent_info.get("process_id"):
                if self.process_service.is_process_running(agent_info["process_id"]):
                    agent_info["status"] = "running"
                else:
                    agent_info["status"] = "stopped"
            
            agents.append(CompanyAgentResponse(
                agent_id=agent_id,
                company_id=agent_info["company_id"],
                company_name=agent_info["company_name"],
                agent_name=agent_info["agent_name"],
                port=agent_info["port"],
                address=agent_info["address"],
                status=agent_info["status"],
                created_at=agent_info["created_at"],
                process_id=agent_info.get("process_id"),
                capabilities=agent_info.get("capabilities", []),
                description=agent_info.get("description"),
                webhook_url=agent_info.get("webhook_url")
            ))
        
        return agents
    
    async def discover_agents(self, discovery_request: AgentDiscoveryRequest) -> AgentDiscoveryResponse:
        """Discover agents by capability"""
        try:
            # Search in local registry first
            matching_agents = []
            for agent_id, agent_info in self.company_agents_registry.items():
                if discovery_request.company_id and agent_info["company_id"] != discovery_request.company_id:
                    continue
                
                if discovery_request.capability.lower() in [cap.lower() for cap in agent_info.get("capabilities", [])]:
                    matching_agents.append(CompanyAgentResponse(
                        agent_id=agent_id,
                        company_id=agent_info["company_id"],
                        company_name=agent_info["company_name"],
                        agent_name=agent_info["agent_name"],
                        port=agent_info["port"],
                        address=agent_info["address"],
                        status=agent_info["status"],
                        created_at=agent_info["created_at"],
                        process_id=agent_info.get("process_id"),
                        capabilities=agent_info.get("capabilities", []),
                        description=agent_info.get("description"),
                        webhook_url=agent_info.get("webhook_url")
                    ))
            
            
            return AgentDiscoveryResponse(
                agents=matching_agents,
                total_found=len(matching_agents)
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to discover agents: {str(e)}")
    
    async def send_message_to_agent(self, message_request: AgentMessageRequest) -> AgentMessageResponse:
        """Send a message to a specific agent"""
        try:
            if message_request.agent_id not in self.company_agents_registry:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            agent_info = self.company_agents_registry[message_request.agent_id]
            
            # This would typically involve sending a message through the agent network
            # For now, we'll simulate the response
            response = f"Message received by {agent_info['agent_name']}: {message_request.message}"
            
            return AgentMessageResponse(
                agent_id=message_request.agent_id,
                response=response,
                timestamp=datetime.now().isoformat(),
                status="delivered"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")
    
    def get_company_agent(self, agent_id: str) -> CompanyAgentResponse:
        """Get specific company agent information"""
        if agent_id not in self.company_agents_registry:
            raise HTTPException(status_code=404, detail="Company agent not found")
        
        agent_info = self.company_agents_registry[agent_id]
        
        # Check if process is still running
        if agent_info.get("process_id"):
            if self.process_service.is_process_running(agent_info["process_id"]):
                agent_info["status"] = "running"
            else:
                agent_info["status"] = "stopped"
        
        return CompanyAgentResponse(
            agent_id=agent_id,
            company_id=agent_info["company_id"],
            company_name=agent_info["company_name"],
            agent_name=agent_info["agent_name"],
            port=agent_info["port"],
            address=agent_info["address"],
            status=agent_info["status"],
            created_at=agent_info["created_at"],
            process_id=agent_info.get("process_id"),
            capabilities=agent_info.get("capabilities", []),
            description=agent_info.get("description"),
            webhook_url=agent_info.get("webhook_url")
        )
    
    async def delete_company_agent(self, agent_id: str) -> Dict[str, str]:
        """Delete a company agent"""
        if agent_id not in self.company_agents_registry:
            raise HTTPException(status_code=404, detail="Company agent not found")
        
        agent_info = self.company_agents_registry[agent_id]
        
        # Stop the agent process if running
        if agent_info.get("process_id") and self.process_service.is_process_running(agent_info["process_id"]):
            self.process_service.stop_agent_process(agent_info["process_id"])
        
        if "filepath" in agent_info:
            agent_folder = os.path.dirname(agent_info["filepath"])
            if os.path.exists(agent_folder):
                import shutil
                shutil.rmtree(agent_folder)
        
        if agent_id in self.port_mapping:
            del self.port_mapping[agent_id]
        
        del self.company_agents_registry[agent_id]
        
        return {"message": f"Company agent {agent_id} deleted successfully"}
    
    def get_company_health_status(self) -> Dict[str, Any]:
        """Get health status of all company agents"""
        active_count = 0
        agent_statuses = []
        
        for agent_id, agent_info in self.company_agents_registry.items():
            status = "stopped"
            uptime = None
            
            if agent_info.get("process_id") and self.process_service.is_process_running(agent_info["process_id"]):
                status = "running"
                active_count += 1
                uptime = self.process_service.get_process_uptime(agent_info["process_id"])
            
            agent_statuses.append(CompanyAgentStatusResponse(
                agent_id=agent_id,
                company_id=agent_info["company_id"],
                company_name=agent_info["company_name"],
                agent_name=agent_info["agent_name"],
                status=status,
                port=agent_info["port"],
                address=agent_info["address"],
                process_id=agent_info.get("process_id"),
                uptime=uptime,
                capabilities=agent_info.get("capabilities", [])
            ))
        
        return {
            "status": "healthy",
            "total_agents": len(self.company_agents_registry),
            "active_agents": active_count,
            "agents": agent_statuses
        }
