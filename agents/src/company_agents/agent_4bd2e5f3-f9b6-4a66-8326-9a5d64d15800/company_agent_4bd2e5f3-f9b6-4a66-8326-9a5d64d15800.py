from datetime import datetime
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


load_dotenv()
client = OpenAI(
    base_url='https://api.asi1.ai/v1',
    api_key=os.getenv("ASI_API_KEY"),  
)

# REST API Models
class RestRequest(Model):
    text: str
    sender_company_id: str = None
    metadata: Dict[str, Any] = {}

class RestResponse(Model):
    timestamp: int
    text: str
    agent_address: str
    status: str = "success"
    metadata: Dict[str, Any] = {}

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
    usage: Dict[str, Any] = {}

SEED_PHRASE = "default_seed_phrase"
COMPANY_ID = "deb3676e-1db1-4a93-abcf-bd22be9224ea"
COMPANY_NAME = "Test"
AGENT_NAME = "GoldRush"
WEBHOOK_URL = "http://localhost:8001/webhook"

# Refund configuration
refund_config = None

# Agent configuration
class AgentConfig:
    def __init__(self):
        self.capabilities = []

agent_config = AgentConfig()

# Initialize tools based on capabilities

# Calculator capability available by default

# System prompt for the agent
system_prompt = f"""You are an expert AI support agent for Test, with deep knowledge of their specific products, services, and documentation.

🏢 COMPANY CONTEXT:
- Company: Test
- Products/Services: products and services
- Support Categories: general, technical, billing

📚 DOCUMENT-DRIVEN EXPERTISE:
You have access to Test's complete documentation, product guides, API references, policies, and knowledge base. Your responses MUST be grounded in this company-specific information.

CAPABILITIES:


AVAILABLE TOOLS:


🎯 DOCUMENT-FIRST RESPONSE PROTOCOL:

1. MANDATORY DOCUMENT CONSULTATION:
   - Always reference provided company context and documentation
   - Use comprehensive search terms related to the user's query
   - Search for: product features, API endpoints, configuration steps, troubleshooting guides, policies, pricing, integrations
   - Always extract specific details, examples, and instructions from the documents

2. DOCUMENT-BASED RESPONSES:
   - Quote relevant sections from company documentation
   - Reference specific page numbers, sections, or document names when available
   - Provide exact API endpoints, parameters, and code examples from the docs
   - Use the company's official terminology and naming conventions
   - Include specific version numbers, requirements, and compatibility information

3. COMPREHENSIVE INFORMATION EXTRACTION:
   - Extract step-by-step procedures directly from documentation
   - Identify and explain company-specific features and configurations
   - Reference pricing, limits, and policy information from official docs
   - Provide troubleshooting steps and error codes from support documentation
   - Include links to specific documentation sections when mentioned

4. ACCURACY AND COMPLETENESS:
   - Never make assumptions - only provide information found in the documents
   - If information is not in the documents, clearly state this limitation
   - Cross-reference multiple document sections for comprehensive answers
   - Verify technical details against official documentation
   - Provide alternative solutions if multiple approaches are documented

5. ENHANCED USER EXPERIENCE:
   - Structure responses with clear headings and bullet points
   - Provide code examples exactly as they appear in documentation
   - Include prerequisites and dependencies mentioned in docs
   - Offer related features and integrations documented by the company
   - Suggest next steps based on documented workflows

6. ESCALATION AND LIMITATIONS:
   - If the query requires information not in the documentation, suggest contacting support
   - For complex integrations, reference the most detailed documentation sections
   - When multiple solutions exist, present all documented options
   - Always prioritize official documentation over general knowledge

🔍 SEARCH STRATEGY:
When using search_company_documents, employ multiple search approaches:
- Primary keywords from user query
- Related technical terms and synonyms
- Product names and feature names
- API endpoints and method names
- Error messages and troubleshooting terms
- Configuration and setup keywords

REMEMBER: Your expertise comes from Test's specific documentation. Always ground your responses in their official materials, procedures, and guidelines. You are representing Test and should reflect their specific approach, terminology, and solutions."""

# Document context for reference (PDF)
document_context = f""""""

# Log document context for debugging
print(f"📚 Agent knowledge base loaded: {len(document_context)} characters")
if document_context.strip():
    print(f"📋 Knowledge base preview: {document_context[:500]}...")
    print("✅ Document-driven responses enabled")
else:
    print("⚠️ No document context available - responses will be based on general knowledge only")

# Define available tools for the support agent following ASI:One format
def get_available_tools():
    return []



# Initialize refund processor if refund processing capability is enabled (must be after tool functions are defined)


agent = Agent(
    name="GoldRush",
    seed=SEED_PHRASE,
    port=8001,
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
                {"role": "system", "content": system_prompt + document_context},
                {"role": "user", "content": text},
            ],
            tools=get_available_tools(),
            tool_choice="auto",
            max_tokens=20000,
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
                        tool_results.append({
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        })
                    
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
                        tool_results.append({
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        })
                    
                    elif function_name == "calculate":
                        result = await calculate(
                            function_args.get("expression", "")
                        )
                        tool_results.append({
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        })
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
                        tool_results.append({
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        })
                    
                    elif function_name == "validate_refund_request":
                        result = await validate_refund_transaction(
                            function_args.get("user_address"),
                            function_args.get("transaction_hash"),
                            function_args.get("requested_amount"),
                            function_args.get("refund_chain"),
                            function_args.get("max_refund_amount")
                        )
                        tool_results.append({
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        })
                    else:
                        # Unknown tool
                        tool_results.append({
                            "role": "tool",
                            "content": f"Error: Unknown tool '{function_name}'",
                            "tool_call_id": tool_call.id
                        })
                        
                except Exception as e:
                    # Handle tool execution errors
                    tool_results.append({
                        "role": "tool",
                        "content": f"Error executing {function_name}: {str(e)}",
                        "tool_call_id": tool_call.id
                    })
            
            # Send tool results back to ASI:One for final response following the exact format
            follow_up_messages = [
                {"role": "system", "content": system_prompt + document_context},
                {"role": "user", "content": text},
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [{
                        "id": tool_call.id,
                        "type": "function", 
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    } for tool_call in message.tool_calls]
                },
                *tool_results
            ]
            
            final_response = client.chat.completions.create(
                model="asi1-fast",
                messages=follow_up_messages,
                tools=get_available_tools(),  # Include tools for safety
                max_tokens=20000,
            )
            response = str(final_response.choices[0].message.content)
        else:
            response = str(message.content)
            
    except Exception as e:
        ctx.logger.exception("Error querying model")
        response = f"I encountered an error while processing your request: {str(e)}"

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
    return {
        "timestamp": int(time.time()),
        "text": f"Hello from {AGENT_NAME} for {COMPANY_NAME}!",
        "agent_address": ctx.agent.address,
        "status": "success",
        "metadata": {
            "company_id": COMPANY_ID,
            "company_name": COMPANY_NAME,
            "agent_name": AGENT_NAME,
            "capabilities": []
        }
    }

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
            metadata={
                "company_id": COMPANY_ID,
                "company_name": COMPANY_NAME,
                "agent_name": AGENT_NAME,
                "sender_company_id": req.sender_company_id
            }
        )
    except Exception as e:
        return RestResponse(
            timestamp=int(time.time()),
            text=f"Error processing request: {str(e)}",
            agent_address=ctx.agent.address,
            status="error",
            metadata={"error": str(e)}
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
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_content
                },
                "finish_reason": "stop"
            }],
            usage={
                "prompt_tokens": len(str(req.messages)),
                "completion_tokens": len(response_content),
                "total_tokens": len(str(req.messages)) + len(response_content)
            }
        )
    except Exception as e:
        error_message = f"Error processing chat request: {str(e)}"
        return ChatResponse(
            id=str(uuid4()),
            created=int(time.time()),
            model=req.model,
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": error_message
                },
                "finish_reason": "stop"
            }],
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        )

async def process_company_request(message: str, sender_company_id: str) -> str:
    """Process company-specific requests using ASI:One with tool calling"""
    print(f"💬 Processing request: {message}")
    print(f"📄 Document context length: {len(document_context)} characters")
    try:
        # First request with tools and parallel execution support
        r = client.chat.completions.create(
            model="asi1-fast",
            messages=[
                {"role": "system", "content": system_prompt + document_context},
                {"role": "user", "content": message},
            ],
            tools=get_available_tools(),
            tool_choice="auto",
            max_tokens=20000,
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
                        tool_results.append({
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        })
                    
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
                        tool_results.append({
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        })
                    
                    elif function_name == "calculate":
                        result = await calculate(
                            function_args.get("expression", "")
                        )
                        tool_results.append({
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        })
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
                        tool_results.append({
                            "role": "tool",
                            "content": result,
                            "tool_call_id": tool_call.id
                        })
                    
                    elif function_name == "validate_refund_request":
                        result = await validate_refund_transaction(
                            function_args.get("user_address"),
                            function_args.get("transaction_hash"),
                            function_args.get("requested_amount"),
                            function_args.get("refund_chain"),
                            function_args.get("max_refund_amount")
                        )
                        tool_results.append({
                            "role": "tool",
                            "content": result,
                            "tool_call_id": tool_call.id
                        })
                    else:
                        # Unknown tool
                        tool_results.append({
                            "role": "tool",
                            "content": f"Error: Unknown tool '{function_name}'",
                            "tool_call_id": tool_call.id
                        })
                        
                except Exception as e:
                    # Handle tool execution errors
                    tool_results.append({
                        "role": "tool",
                        "content": f"Error executing {function_name}: {str(e)}",
                        "tool_call_id": tool_call.id
                    })
            
            # Get final response after tool execution
            follow_up_messages = [
                {"role": "system", "content": system_prompt + document_context},
                {"role": "user", "content": message},
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [{
                        "id": tool_call.id,
                        "type": "function", 
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    } for tool_call in message_obj.tool_calls]
                },
                *tool_results
            ]
            
            final_response = client.chat.completions.create(
                model="asi1-fast",
                messages=follow_up_messages,
                tools=get_available_tools(),
                max_tokens=20000,
            )
            return str(final_response.choices[0].message.content)
        else:
            return str(message_obj.content)
            
    except Exception as e:
        return f"Error processing request: {str(e)}"

async def process_chat_messages(messages: List[Dict[str, Any]], model: str) -> str:
    """Process chat messages for ASI:One with tool calling"""
    try:
        # Add system message for company context
        system_message = {
            "role": "system", 
            "content": system_prompt
        }
        
        # Combine system message with user messages
        all_messages = [system_message] + messages
        
        # First request with tools and parallel execution support
        r = client.chat.completions.create(
            model=model,
            messages=all_messages,
            tools=get_available_tools(),
            tool_choice="auto",
            max_tokens=20000,
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
                        tool_results.append({
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        })
                    
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
                        tool_results.append({
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        })
                    
                    elif function_name == "calculate":
                        result = await calculate(
                            function_args.get("expression", "")
                        )
                        tool_results.append({
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.id
                        })
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
                        tool_results.append({
                            "role": "tool",
                            "content": result,
                            "tool_call_id": tool_call.id
                        })
                    
                    elif function_name == "validate_refund_request":
                        result = await validate_refund_transaction(
                            function_args.get("user_address"),
                            function_args.get("transaction_hash"),
                            function_args.get("requested_amount"),
                            function_args.get("refund_chain"),
                            function_args.get("max_refund_amount")
                        )
                        tool_results.append({
                            "role": "tool",
                            "content": result,
                            "tool_call_id": tool_call.id
                        })
                    else:
                        # Unknown tool
                        tool_results.append({
                            "role": "tool",
                            "content": f"Error: Unknown tool '{function_name}'",
                            "tool_call_id": tool_call.id
                        })
                        
                except Exception as e:
                    # Handle tool execution errors
                    tool_results.append({
                        "role": "tool",
                        "content": f"Error executing {function_name}: {str(e)}",
                        "tool_call_id": tool_call.id
                    })
            
            # Get final response after tool execution
            follow_up_messages = all_messages + [
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [{
                        "id": tool_call.id,
                        "type": "function", 
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    } for tool_call in message_obj.tool_calls]
                },
                *tool_results
            ]
            
            final_response = client.chat.completions.create(
                model=model,
                messages=follow_up_messages,
                tools=get_available_tools(),
                max_tokens=20000,
            )
            return str(final_response.choices[0].message.content)
        else:
            return str(message_obj.content)
            
    except Exception as e:
        return f"Error processing chat request: {str(e)}"

async def send_webhook_notification(response: str, sender_company_id: str):
    """Send webhook notification to company's system"""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(WEBHOOK_URL, json={
                "response": response,
                "sender_company_id": sender_company_id,
                "company_id": COMPANY_ID,
                "timestamp": datetime.now().isoformat()
            })
    except Exception as e:
        print(f"Webhook notification failed: {e}")

agent.include(protocol, publish_manifest=True)

print(f"Company Agent {agent.address} for {COMPANY_NAME} is ready")

# Write the agent address to a file for the service to read
import os
agent_address_file = os.path.join(os.path.dirname(__file__), "agent_address.txt")
with open(agent_address_file, "w") as f:
    f.write(agent.address)

if __name__ == "__main__":
    agent.run()
