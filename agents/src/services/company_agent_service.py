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
from .pdf_service import PDFService
from ..config import get_settings
from ..tools.pdf_reader import PDFReader
from ..tools.transaction_verifier import verify_transaction, get_transaction_verification_schema


class CompanyAgentService:
    """Service for managing company-specific agents"""
    
    def __init__(self):
        self.company_agents_registry: Dict[str, Dict[str, Any]] = {}
        self.process_service = ProcessService()
        self.pdf_service = PDFService()
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
        
        print(f"Processing PDF documents from URLs: {pdf_document_urls}")
        pdf_context = ""
        for url in pdf_document_urls:
            try:
                print(f"Processing PDF from URL: {url}")
                # Process PDF from URL
                result = await self.pdf_service.process_pdf_from_url(url, max_length=2000)
                if result.get("success") and result.get("content"):
                    content = result['content']
                    print(f"Successfully extracted {len(content)} characters from {url}")
                    pdf_context += f"\n\nDocument Context from {url}:\n{content}..."
                else:
                    print(f"Failed to extract content from {url}: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"Error processing PDF from URL {url}: {e}")
                continue
        
        print(f"Generated PDF context length: {len(pdf_context)} characters")
        print(f"PDF context preview: {pdf_context[:500]}...")
        return pdf_context
    
    async def generate_company_agent_code(self, agent_config: CompanyAgentCreateRequest) -> str:
        """Generate the company support agent Python code with chat protocol and tools"""
        webhook_url = agent_config.webhook_url or f"http://localhost:{agent_config.port}/webhook"
        
        pdf_context = ""
        if agent_config.pdf_document_urls:
            pdf_context = await self.get_pdf_context(agent_config.pdf_document_urls)
        
        # Generate support agent system prompt
        support_categories = agent_config.support_categories or ["general", "technical", "billing"]
        company_products = agent_config.company_products or ["products and services"]
        
        system_prompt = f"""You are a helpful AI support agent for {agent_config.company_name}. 

Your role is to assist customers with:
- Product information and how our services work
- Technical support and troubleshooting
- Billing and payment questions
- General inquiries about {agent_config.company_name}

You have access to the following tools:
- PDF Document Reference: You can search through company documents to find specific information
- Transaction Verification: You can verify blockchain transactions and payments

Company Products/Services: {', '.join(company_products)}
Support Categories: {', '.join(support_categories)}

CRITICAL INSTRUCTIONS:
1. When users ask ANY question about {agent_config.company_name}, employees, skills, experience, projects, or company information, you MUST ALWAYS call the search_company_documents tool FIRST before responding.
2. Use search terms like: "work experience", "programming languages", "technologies", "education", "projects", "skills", "achievements"
3. Do NOT ask for permission - automatically search the documents and provide the information you find.
4. If you find relevant information, share it with the user. If you don't find anything, then explain what you searched for.

Always be helpful, professional, and accurate. Use the document search tool automatically when users ask about company information."""
        
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
from tools.pdf_reader import PDFReader
from tools.transaction_verifier import verify_transaction, get_transaction_verification_schema

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

# Initialize tools
pdf_reader = PDFReader()

# System prompt for the agent
system_prompt = f"""You are a helpful AI support agent for {agent_config.company_name}. 

Your role is to assist customers with:
- Product information and how our services work
- Technical support and troubleshooting
- Billing and payment questions
- General inquiries about {agent_config.company_name}

You have access to the following tools:
- PDF Document Reference: You can search through company documents to find specific information
- Transaction Verification: You can verify blockchain transactions and payments

Company Products/Services: {', '.join(company_products)}
Support Categories: {', '.join(support_categories)}

Always be helpful, professional, and accurate. If you need to reference company documents or verify transactions, use the appropriate tools."""

# PDF context for document reference
pdf_context = f"""{pdf_context}"""

# Log PDF context for debugging
print(f"Agent PDF context length: {{len(pdf_context)}} characters")
print(f"Agent PDF context preview: {{pdf_context[:500]}}...")

# Define available tools for the support agent following ASI:One format
def get_available_tools():
    return [
        {{
            "type": "function",
            "function": {{
                "name": "search_company_documents",
                "description": "Search through company PDF documents for specific information about products, policies, or procedures",
                "parameters": {{
                    "type": "object",
                    "properties": {{
                        "search_terms": {{
                            "type": "array",
                            "items": {{"type": "string"}},
                            "description": "List of terms to search for in company documents"
                        }},
                        "document_urls": {{
                            "type": "array", 
                            "items": {{"type": "string"}},
                            "description": "Specific document URLs to search in (optional)"
                        }}
                    }},
                    "required": ["search_terms"],
                    "additionalProperties": False
                }},
                "strict": True
            }}
        }},
        {{
            "type": "function",
            "function": {{
                "name": "verify_transaction",
                "description": "Verify if a blockchain transaction matches the expected parameters for payment verification",
                "parameters": {{
                    "type": "object",
                    "properties": {{
                        "tx_hash": {{
                            "type": "string",
                            "description": "The transaction hash to verify"
                        }},
                        "chain_name": {{
                            "type": "string",
                            "description": "The blockchain name (e.g., 'eth-mainnet', 'polygon-mainnet')"
                        }},
                        "from_address": {{
                            "type": "string",
                            "description": "The expected sender address"
                        }},
                        "to_address": {{
                            "type": "string", 
                            "description": "The expected receiver address (for native) or recipient (for ERC-20)"
                        }},
                        "token_address": {{
                            "type": "string",
                            "description": "The token contract address. Use 'native' for native blockchain token"
                        }},
                        "amount": {{
                            "type": "string",
                            "description": "The expected amount (in wei for native, token units for ERC-20)"
                        }},
                        "is_native": {{
                            "type": "boolean",
                            "description": "Whether this is a native token transfer (true) or ERC-20 transfer (false)",
                            "default": False
                        }}
                    }},
                    "required": ["tx_hash", "chain_name", "from_address", "to_address", "token_address", "amount", "is_native"],
                    "additionalProperties": False
                }},
                "strict": True
            }}
        }}
    ]

async def search_company_documents(search_terms: List[str], document_urls: List[str] = None) -> str:
    """Search through company documents for information"""
    print(f"🔍 search_company_documents called with terms: {{search_terms}}, urls: {{document_urls}}")
    try:
        # Initialize PDF reader
        pdf_reader = PDFReader()
        
        # If specific document URLs provided, search only those
        if document_urls:
            search_results = []
            for url in document_urls:
                try:
                    # Process PDF from URL
                    result = await pdf_reader.read_pdf_from_url(url, max_length=10000)
                    if result.get("success") and result.get("content"):
                        content = result.get("content", "").lower()
                        
                        # Search for terms in the document
                        found_terms = []
                        for term in search_terms:
                            if term.lower() in content:
                                found_terms.append(term)
                        
                        if found_terms:
                            search_results.append(f"Document {{url}}: Found terms: {{', '.join(found_terms)}}")
                except Exception as e:
                    search_results.append(f"Error processing {{url}}: {{str(e)}}")
        else:
            # Default document URLs for this company
            default_urls = {agent_config.pdf_document_urls or []}
            search_results = []
            
            for url in default_urls:
                try:
                    result = await pdf_reader.read_pdf_from_url(url, max_length=10000)
                    if result.get("success") and result.get("content"):
                        content = result.get("content", "").lower()
                        found_terms = []
                        for term in search_terms:
                            if term.lower() in content:
                                found_terms.append(term)
                        
                        if found_terms:
                            search_results.append(f"Document {{url}}: Found terms: {{', '.join(found_terms)}}")
                except Exception as e:
                    search_results.append(f"Error processing {{url}}: {{str(e)}}")
        
        if search_results:
            return f"Found relevant information in company documents:\\n" + "\\n".join(search_results)
        else:
            return f"No relevant information found for terms: {{', '.join(search_terms)}}"
            
    except Exception as e:
        return f"Error searching documents: {{str(e)}}"

async def verify_payment_transaction(tx_hash: str, chain_name: str, from_address: str, to_address: str, token_address: str, amount: str, is_native: bool = False) -> str:
    """Verify a blockchain payment transaction"""
    try:
        result = await verify_transaction(tx_hash, chain_name, from_address, to_address, token_address, amount, is_native)
        if result.get("verified"):
            return f"✅ Transaction verified successfully! All parameters match."
        else:
            mismatches = result.get("mismatches", [])
            return f"❌ Transaction verification failed. Mismatches: {{json.dumps(mismatches, indent=2)}}"
    except Exception as e:
        return f"Error verifying transaction: {{str(e)}}"

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
            model="asi1-mini",
            messages=[
                {{"role": "system", "content": system_prompt + pdf_context}},
                {{"role": "user", "content": text}},
            ],
            tools=get_available_tools(),
            tool_choice="auto",
            parallel_tool_calls=True,  # Enable parallel tool execution
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
                            "content": json.dumps(result) if isinstance(result, (dict, list)) else str(result),
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
                            "content": json.dumps(result) if isinstance(result, (dict, list)) else str(result),
                            "tool_call_id": tool_call.id
                        }})
                    else:
                        # Unknown tool
                        tool_results.append({{
                            "role": "tool",
                            "content": json.dumps({{"error": f"Unknown tool: {{function_name}}"}}),
                            "tool_call_id": tool_call.id
                        }})
                        
                except Exception as e:
                    # Handle tool execution errors
                    error_result = {{
                        "error": f"Tool execution failed: {{str(e)}}",
                        "tool_name": function_name,
                        "arguments": function_args
                    }}
                    tool_results.append({{
                        "role": "tool",
                        "content": json.dumps(error_result),
                        "tool_call_id": tool_call.id
                    }})
            
            # Send tool results back to ASI:One for final response
            follow_up_messages = [
                {{"role": "system", "content": system_prompt + pdf_context}},
                {{"role": "user", "content": text}},
                {{
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [tool_call for tool_call in message.tool_calls]
                }},
                *tool_results
            ]
            
            final_response = client.chat.completions.create(
                model="asi1-mini",
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
    print(f"📄 PDF context length: {{len(pdf_context)}} characters")
    try:
        # First request with tools and parallel execution support
        r = client.chat.completions.create(
            model="asi1-mini",
            messages=[
                {{"role": "system", "content": system_prompt + pdf_context}},
                {{"role": "user", "content": message}},
            ],
            tools=get_available_tools(),
            tool_choice="auto",
            parallel_tool_calls=True,  # Enable parallel tool execution
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
                            "content": json.dumps(result) if isinstance(result, (dict, list)) else str(result),
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
                            "content": json.dumps(result) if isinstance(result, (dict, list)) else str(result),
                            "tool_call_id": tool_call.id
                        }})
                    else:
                        # Unknown tool
                        tool_results.append({{
                            "role": "tool",
                            "content": json.dumps({{"error": f"Unknown tool: {{function_name}}"}}),
                            "tool_call_id": tool_call.id
                        }})
                        
                except Exception as e:
                    # Handle tool execution errors
                    error_result = {{
                        "error": f"Tool execution failed: {{str(e)}}",
                        "tool_name": function_name,
                        "arguments": function_args
                    }}
                    tool_results.append({{
                        "role": "tool",
                        "content": json.dumps(error_result),
                        "tool_call_id": tool_call.id
                    }})
            
            # Get final response after tool execution
            follow_up_messages = [
                {{"role": "system", "content": system_prompt + pdf_context}},
                {{"role": "user", "content": message}},
                {{
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [tool_call for tool_call in message_obj.tool_calls]
                }},
                *tool_results
            ]
            
            final_response = client.chat.completions.create(
                model="asi1-mini",
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
            parallel_tool_calls=True,  # Enable parallel tool execution
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
                            "content": json.dumps(result) if isinstance(result, (dict, list)) else str(result),
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
                            "content": json.dumps(result) if isinstance(result, (dict, list)) else str(result),
                            "tool_call_id": tool_call.id
                        }})
                    else:
                        # Unknown tool
                        tool_results.append({{
                            "role": "tool",
                            "content": json.dumps({{"error": f"Unknown tool: {{function_name}}"}}),
                            "tool_call_id": tool_call.id
                        }})
                        
                except Exception as e:
                    # Handle tool execution errors
                    error_result = {{
                        "error": f"Tool execution failed: {{str(e)}}",
                        "tool_name": function_name,
                        "arguments": function_args
                    }}
                    tool_results.append({{
                        "role": "tool",
                        "content": json.dumps(error_result),
                        "tool_call_id": tool_call.id
                    }})
            
            # Get final response after tool execution
            follow_up_messages = all_messages + [
                {{
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [tool_call for tool_call in message_obj.tool_calls]
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
                "company_products": agent_config.company_products or []
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
                webhook_url=agent_config.webhook_url,
                pdf_document_urls=agent_config.pdf_document_urls,
                support_categories=agent_config.support_categories,
                company_products=agent_config.company_products
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
                webhook_url=agent_info.get("webhook_url"),
                pdf_document_urls=agent_info.get("pdf_document_urls", []),
                support_categories=agent_info.get("support_categories", []),
                company_products=agent_info.get("company_products", [])
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
                        company_products=agent_info.get("company_products", [])
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
            webhook_url=agent_info.get("webhook_url"),
            pdf_document_urls=agent_info.get("pdf_document_urls", []),
            support_categories=agent_info.get("support_categories", []),
            company_products=agent_info.get("company_products", [])
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
