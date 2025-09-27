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
    MailboxMessage,
    AgentWalletInfo
)
from .process_service import ProcessService
from .pdf_service import PDFService
from .capability_service import CapabilityService
from .wallet_service import get_wallet_service
from ..config import get_settings
from ..tools.pdf_reader import PDFReader
from ..tools.transaction_verifier import verify_transaction, get_transaction_verification_schema


class CompanyAgentService:
    """Service for managing company-specific agents"""
    
    def __init__(self):
        self.company_agents_registry: Dict[str, Dict[str, Any]] = {}
        self.process_service = ProcessService()
        self.pdf_service = PDFService()
        self.capability_service = CapabilityService()
        self.wallet_service = get_wallet_service()
        self.settings = get_settings()
        self.client = httpx.AsyncClient(timeout=30.0)
        self.port_mapping: Dict[str, int] = {}
        self.next_port = 8001
    
    def get_next_available_port(self) -> int:
        """Get the next available port starting from 8001"""
        import socket
        
        for port in range(self.next_port, self.next_port + 100):  # Try up to 100 ports
            try:
                # Try to bind to the port to check if it's available
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    self.next_port = port + 1
                    return port
            except OSError:
                # Port is in use, try next one
                continue
        
        # If no port found, raise an error
        raise HTTPException(status_code=500, detail="No available ports found")
    
    async def get_pdf_context(self, pdf_document_urls: List[str]) -> str:
        """Get PDF context from document URLs by processing them"""
        if not pdf_document_urls:
            print("No PDF document URLs provided")
            return ""
        
        print(f"Processing {len(pdf_document_urls)} PDF documents from URLs")
        
        try:
            # Use the improved multiple PDF processing
            result = await self.pdf_service.process_multiple_pdfs(pdf_document_urls, max_length_per_pdf=15000)
            
            if result.get("success") and result.get("content"):
                content = result['content']
                processed_count = result.get('processed_docs_count', 0)
                total_attempted = result.get('total_docs_attempted', len(pdf_document_urls))
                
                print(f"✅ Successfully processed {processed_count}/{total_attempted} PDFs")
                print(f"📊 Total content length: {len(content)} characters")
                print(f"📄 Total pages: {result.get('page_count', 0)}")
                
                # Add metadata header to the context
                pdf_context = f"""
=== COMPANY DOCUMENT CONTEXT ===
Processed Documents: {processed_count}/{total_attempted}
Total Pages: {result.get('page_count', 0)}
Total Content Length: {len(content)} characters
Source URLs: {', '.join(pdf_document_urls)}

{content}
=== END COMPANY DOCUMENT CONTEXT ===
"""
                
                print(f"📋 Generated comprehensive PDF context: {len(pdf_context)} characters")
                return pdf_context
            else:
                error_msg = result.get('error', 'Unknown error processing PDFs')
                print(f"❌ Failed to process PDFs: {error_msg}")
                return f"Error processing company documents: {error_msg}"
                
        except Exception as e:
            print(f"❌ Error processing PDF documents: {e}")
            return f"Error processing company documents: {str(e)}"
    
    
    async def generate_company_agent_code(self, agent_config: CompanyAgentCreateRequest) -> str:
        """Generate the company support agent Python code with chat protocol and tools"""
        webhook_url = agent_config.webhook_url or f"http://localhost:{agent_config.port}/webhook"
        
        # Validate capabilities
        validation_result = self.capability_service.validate_capabilities(agent_config.capabilities)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid capabilities: {validation_result['invalid_capabilities']}. Available: {validation_result['available_capabilities']}"
            )
        
        # Get context from PDF documents
        document_context = ""
        if agent_config.pdf_document_urls:
            document_context = await self.get_pdf_context(agent_config.pdf_document_urls)
        
        # Generate support agent system prompt using capability service
        support_categories = agent_config.support_categories or ["general", "technical", "billing"]
        company_products = agent_config.company_products or ["products and services"]
        
        system_prompt = self.capability_service.get_system_prompt_for_capabilities(
            agent_config.capabilities,
            agent_config.company_name,
            support_categories,
            company_products
        )
        
        # Get tool imports and functions based on capabilities
        tool_imports = self.capability_service.get_tool_imports_for_capabilities(agent_config.capabilities)
        tool_functions = self.capability_service.get_tool_functions_for_capabilities(
            agent_config.capabilities, 
            agent_config.pdf_document_urls
        )
        
        # Get available tools for the agent
        available_tools = self.capability_service.get_tools_for_capabilities(agent_config.capabilities)
        
        code = f'''from datetime import datetime
from uuid import uuid4
import os
import json
import httpx
import time
import asyncio
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

# Import tools for company support agent
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
{chr(10).join(tool_imports)}

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
    model: str = "asi1-fast"
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

# Refund configuration
refund_config = {agent_config.refund_config or 'None'}

# Agent configuration
class AgentConfig:
    def __init__(self):
        self.capabilities = {agent_config.capabilities}

agent_config = AgentConfig()

# Initialize tools based on capabilities
{f"pdf_reader = PDFReader()" if "document_reference" in agent_config.capabilities else ""}
# Calculator capability available by default

# Initialize refund processor if refund processing capability is enabled
{f"""
# Initialize refund processor with company configuration
if refund_config:
    initialize_refund_processor(
        company_id=refund_config.get('company_id', COMPANY_ID),
        max_refund_amount=refund_config.get('max_refund_amount', '1000000000000000000'),
        expected_address=refund_config.get('expected_address', ''),
        custom_api_url=refund_config.get('custom_api_url'),
        custom_api_headers=refund_config.get('custom_api_headers'),
        custom_api_field=refund_config.get('custom_api_field'),
        escalation_threshold=refund_config.get('escalation_threshold')
    )
    print(f"✅ Refund processor initialized for company {{COMPANY_NAME}}")
else:
    print("⚠️ Refund processing capability enabled but no refund configuration provided")
""" if "refund_processing" in agent_config.capabilities else ""}

# System prompt for the agent
system_prompt = f"""{system_prompt}"""

# Document context for reference (PDF)
document_context = f"""{document_context}"""

# Log document context for debugging
print(f"Agent document context length: {{len(document_context)}} characters")
print(f"Agent document context preview: {{document_context[:500]}}...")

# Define available tools for the support agent following ASI:One format
def get_available_tools():
    return {available_tools}

{tool_functions}

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
        # Use ASI:One tool calling format with parallel tool calling support
        r = client.chat.completions.create(
            model="asi1-fast",
            messages=[
                {{"role": "system", "content": system_prompt + document_context}},
                {{"role": "user", "content": text}},
            ],
            tools=get_available_tools(),
            tool_choice="auto",
            max_tokens=2048,
        )
        
        message = r.choices[0].message
        
        # Check if the model wants to call a function (ASI:One format)
        if hasattr(message, 'tool_calls') and message.tool_calls:
            # Process tool calls following ASI:One format
            tool_results = []
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Execute the appropriate tool with error handling
                try:
                    if function_name == "search_company_documents":
                        result = await search_company_documents(
                            function_args.get("search_terms", []),
                            function_args.get("document_urls", [])
                        )
                        tool_results.append({{
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        }})
                    
                    elif function_name == "verify_transaction":
                        result = await verify_payment_transaction(
                            function_args.get("tx_hash"),
                            function_args.get("chain_name"), 
                            function_args.get("from_address"),
                            function_args.get("to_address"),
                            function_args.get("token_address"),
                            function_args.get("amount"),
                            function_args.get("is_native", False)
                        )
                        tool_results.append({{
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        }})
                    
                    elif function_name == "calculate":
                        result = await calculate(
                            function_args.get("expression", "")
                        )
                        tool_results.append({{
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        }})
                    elif function_name == "process_refund":
                        result = await process_refund_transaction(
                            function_args.get("user_address"),
                            function_args.get("transaction_hash"),
                            function_args.get("requested_amount"),
                            function_args.get("agent_private_key"),
                            function_args.get("refund_chain"),
                            function_args.get("max_refund_amount"),
                            function_args.get("reason")
                        )
                        tool_results.append({{
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        }})
                    
                    elif function_name == "validate_refund_request":
                        result = await validate_refund_transaction(
                            function_args.get("user_address"),
                            function_args.get("transaction_hash"),
                            function_args.get("requested_amount"),
                            function_args.get("refund_chain"),
                            function_args.get("max_refund_amount")
                        )
                        tool_results.append({{
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        }})
                    else:
                        # Unknown tool
                        tool_results.append({{
                            "role": "tool",
                            "content": f"Error: Unknown tool '{{function_name}}'",
                            "tool_call_id": tool_call.id
                        }})
                        
                except Exception as e:
                    # Handle tool execution errors
                    tool_results.append({{
                        "role": "tool",
                        "content": f"Error executing {{function_name}}: {{str(e)}}",
                        "tool_call_id": tool_call.id
                    }})
            
            # Send tool results back to ASI:One for final response following the exact format
            follow_up_messages = [
                {{"role": "system", "content": system_prompt + document_context}},
                {{"role": "user", "content": text}},
                {{
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [{{
                        "id": tool_call.id,
                        "type": "function", 
                        "function": {{
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }}
                    }} for tool_call in message.tool_calls]
                }},
                *tool_results
            ]
            
            final_response = client.chat.completions.create(
                model="asi1-fast",
                messages=follow_up_messages,
                tools=get_available_tools(),  # Include tools for safety
                max_tokens=2048,
            )
            response = str(final_response.choices[0].message.content)
        else:
            response = str(message.content)
            
    except Exception as e:
        ctx.logger.exception("Error querying model")
        response = f"I encountered an error while processing your request: {{str(e)}}"

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
    """Process company-specific requests using ASI:One with tool calling"""
    print(f"💬 Processing request: {{message}}")
    print(f"📄 Document context length: {{len(document_context)}} characters")
    try:
        # First request with tools and parallel execution support
        r = client.chat.completions.create(
            model="asi1-fast",
            messages=[
                {{"role": "system", "content": system_prompt + document_context}},
                {{"role": "user", "content": message}},
            ],
            tools=get_available_tools(),
            tool_choice="auto",
            max_tokens=2048,
        )
        
        message_obj = r.choices[0].message
        
        # Check if tools were called
        if hasattr(message_obj, 'tool_calls') and message_obj.tool_calls:
            # Process tool calls
            tool_results = []
            for tool_call in message_obj.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                try:
                    if function_name == "search_company_documents":
                        result = await search_company_documents(
                            function_args.get("search_terms", []),
                            function_args.get("document_urls", [])
                        )
                        tool_results.append({{
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        }})
                    
                    elif function_name == "verify_transaction":
                        result = await verify_payment_transaction(
                            function_args.get("tx_hash"),
                            function_args.get("chain_name"), 
                            function_args.get("from_address"),
                            function_args.get("to_address"),
                            function_args.get("token_address"),
                            function_args.get("amount"),
                            function_args.get("is_native", False)
                        )
                        tool_results.append({{
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        }})
                    
                    elif function_name == "calculate":
                        result = await calculate(
                            function_args.get("expression", "")
                        )
                        tool_results.append({{
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        }})
                    elif function_name == "process_refund":
                        result = await process_refund_transaction(
                            function_args.get("user_address"),
                            function_args.get("transaction_hash"),
                            function_args.get("requested_amount"),
                            function_args.get("agent_private_key"),
                            function_args.get("refund_chain"),
                            function_args.get("max_refund_amount"),
                            function_args.get("reason")
                        )
                        tool_results.append({{
                            "role": "tool",
                            "content": result,
                            "tool_call_id": tool_call.id
                        }})
                    
                    elif function_name == "validate_refund_request":
                        result = await validate_refund_transaction(
                            function_args.get("user_address"),
                            function_args.get("transaction_hash"),
                            function_args.get("requested_amount"),
                            function_args.get("refund_chain"),
                            function_args.get("max_refund_amount")
                        )
                        tool_results.append({{
                            "role": "tool",
                            "content": result,
                            "tool_call_id": tool_call.id
                        }})
                    else:
                        # Unknown tool
                        tool_results.append({{
                            "role": "tool",
                            "content": f"Error: Unknown tool '{{function_name}}'",
                            "tool_call_id": tool_call.id
                        }})
                        
                except Exception as e:
                    # Handle tool execution errors
                    tool_results.append({{
                        "role": "tool",
                        "content": f"Error executing {{function_name}}: {{str(e)}}",
                        "tool_call_id": tool_call.id
                    }})
            
            # Get final response after tool execution
            follow_up_messages = [
                {{"role": "system", "content": system_prompt + document_context}},
                {{"role": "user", "content": message}},
                {{
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [{{
                        "id": tool_call.id,
                        "type": "function", 
                        "function": {{
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }}
                    }} for tool_call in message_obj.tool_calls]
                }},
                *tool_results
            ]
            
            final_response = client.chat.completions.create(
                model="asi1-fast",
                messages=follow_up_messages,
                tools=get_available_tools(),
                max_tokens=2048,
            )
            return str(final_response.choices[0].message.content)
        else:
            return str(message_obj.content)
            
    except Exception as e:
        return f"Error processing request: {{str(e)}}"

async def process_chat_messages(messages: List[Dict[str, Any]], model: str) -> str:
    """Process chat messages for ASI:One with tool calling"""
    try:
        # Add system message for company context
        system_message = {{
            "role": "system", 
            "content": system_prompt
        }}
        
        # Combine system message with user messages
        all_messages = [system_message] + messages
        
        # First request with tools and parallel execution support
        r = client.chat.completions.create(
            model=model,
            messages=all_messages,
            tools=get_available_tools(),
            tool_choice="auto",
            max_tokens=2048,
        )
        
        message_obj = r.choices[0].message
        
        # Check if tools were called
        if hasattr(message_obj, 'tool_calls') and message_obj.tool_calls:
            # Process tool calls
            tool_results = []
            for tool_call in message_obj.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                try:
                    if function_name == "search_company_documents":
                        result = await search_company_documents(
                            function_args.get("search_terms", []),
                            function_args.get("document_urls", [])
                        )
                        tool_results.append({{
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        }})
                    
                    elif function_name == "verify_transaction":
                        result = await verify_payment_transaction(
                            function_args.get("tx_hash"),
                            function_args.get("chain_name"), 
                            function_args.get("from_address"),
                            function_args.get("to_address"),
                            function_args.get("token_address"),
                            function_args.get("amount"),
                            function_args.get("is_native", False)
                        )
                        tool_results.append({{
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        }})
                    
                    elif function_name == "calculate":
                        result = await calculate(
                            function_args.get("expression", "")
                        )
                        tool_results.append({{
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        }})
                    elif function_name == "process_refund":
                        result = await process_refund_transaction(
                            function_args.get("user_address"),
                            function_args.get("transaction_hash"),
                            function_args.get("requested_amount"),
                            function_args.get("agent_private_key"),
                            function_args.get("refund_chain"),
                            function_args.get("max_refund_amount"),
                            function_args.get("reason")
                        )
                        tool_results.append({{
                            "role": "tool",
                            "content": result,
                            "tool_call_id": tool_call.id
                        }})
                    
                    elif function_name == "validate_refund_request":
                        result = await validate_refund_transaction(
                            function_args.get("user_address"),
                            function_args.get("transaction_hash"),
                            function_args.get("requested_amount"),
                            function_args.get("refund_chain"),
                            function_args.get("max_refund_amount")
                        )
                        tool_results.append({{
                            "role": "tool",
                            "content": result,
                            "tool_call_id": tool_call.id
                        }})
                    else:
                        # Unknown tool
                        tool_results.append({{
                            "role": "tool",
                            "content": f"Error: Unknown tool '{{function_name}}'",
                            "tool_call_id": tool_call.id
                        }})
                        
                except Exception as e:
                    # Handle tool execution errors
                    tool_results.append({{
                        "role": "tool",
                        "content": f"Error executing {{function_name}}: {{str(e)}}",
                        "tool_call_id": tool_call.id
                    }})
            
            # Get final response after tool execution
            follow_up_messages = all_messages + [
                {{
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [{{
                        "id": tool_call.id,
                        "type": "function", 
                        "function": {{
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }}
                    }} for tool_call in message_obj.tool_calls]
                }},
                *tool_results
            ]
            
            final_response = client.chat.completions.create(
                model=model,
                messages=follow_up_messages,
                tools=get_available_tools(),
                max_tokens=2048,
            )
            return str(final_response.choices[0].message.content)
        else:
            return str(message_obj.content)
            
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
            
            print(f"🔨 Creating wallet for agent: {agent_config.agent_name}")
            try:
                wallet_info = await self.wallet_service.create_agent_wallet(
                    agent_name=agent_config.agent_name,
                    company_name=agent_config.company_name,
                    agent_id=agent_id,
                    chain='ethereum' 
                )
                print(f"✅ Wallet created for agent {agent_config.agent_name}: {wallet_info['address']}")
                if wallet_info.get('ens_name'):
                    print(f"🌐 ENS name: {wallet_info['ens_name']}")
            except Exception as wallet_error:
                print(f"⚠️ Wallet creation failed: {str(wallet_error)}")
                wallet_info = None
            
            agent_code = await self.generate_company_agent_code(agent_config)
            
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
                "webhook_url": agent_config.webhook_url,
                "pdf_document_urls": agent_config.pdf_document_urls or [],
                "support_categories": agent_config.support_categories or [],
                "company_products": agent_config.company_products or [],
                "company_address": agent_config.company_address,
                "wallet_info": wallet_info 
            }
            
            wallet_info_model = None
            if wallet_info:
                wallet_info_model = AgentWalletInfo(**wallet_info)
            
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
                webhook_url=agent_config.webhook_url,
                pdf_document_urls=agent_config.pdf_document_urls,
                support_categories=agent_config.support_categories,
                company_products=agent_config.company_products,
                company_address=agent_config.company_address,
                wallet_info=wallet_info_model
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
            
            wallet_info_model = None
            wallet_info = agent_info.get("wallet_info")
            if wallet_info:
                wallet_info_model = AgentWalletInfo(**wallet_info)
            
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
                webhook_url=agent_info.get("webhook_url"),
                pdf_document_urls=agent_info.get("pdf_document_urls", []),
                support_categories=agent_info.get("support_categories", []),
                company_products=agent_info.get("company_products", []),
                company_address=agent_info.get("company_address"),
                wallet_info=wallet_info_model
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
                        webhook_url=agent_info.get("webhook_url"),
                        pdf_document_urls=agent_info.get("pdf_document_urls", []),
                        support_categories=agent_info.get("support_categories", []),
                        company_products=agent_info.get("company_products", []),
                        company_address=agent_info.get("company_address")
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
        
        # Convert wallet_info to AgentWalletInfo if available
        wallet_info_model = None
        wallet_info = agent_info.get("wallet_info")
        if wallet_info:
            wallet_info_model = AgentWalletInfo(**wallet_info)
        
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
            webhook_url=agent_info.get("webhook_url"),
            pdf_document_urls=agent_info.get("pdf_document_urls", []),
            support_categories=agent_info.get("support_categories", []),
            company_products=agent_info.get("company_products", []),
            company_address=agent_info.get("company_address"),
            wallet_info=wallet_info_model
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
            
            # Convert wallet_info to AgentWalletInfo if available
            wallet_info_model = None
            wallet_info = agent_info.get("wallet_info")
            if wallet_info:
                wallet_info_model = AgentWalletInfo(**wallet_info)
            
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
                capabilities=agent_info.get("capabilities", []),
                company_address=agent_info.get("company_address"),
                wallet_info=wallet_info_model
            ))
        
        return {
            "status": "healthy",
            "total_agents": len(self.company_agents_registry),
            "active_agents": active_count,
            "agents": agent_statuses
        }
    
    def get_available_capabilities(self) -> Dict[str, Any]:
        """Get all available capabilities for company agents"""
        available_capabilities = self.capability_service.get_available_capabilities()
        capability_mapping = self.capability_service.get_capability_tools_mapping()
        
        capabilities = []
        for capability in available_capabilities:
            description = self.capability_service.get_capability_description(capability)
            tools = capability_mapping.get(capability, [])
            
            capabilities.append({
                "name": capability,
                "description": description,
                "tools": tools
            })
        
        return {
            "capabilities": capabilities,
            "total_capabilities": len(capabilities)
        }
