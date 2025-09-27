from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class AgentCreateRequest(BaseModel):
    """Request model for creating a new agent"""
    name: str
    port: Optional[int] = None 
    seed_phrase: Optional[str] = None
    mailbox: bool = True
    endpoint: Optional[List[str]] = None


class CompanyAgentCreateRequest(BaseModel):
    """Request model for creating a company support agent"""
    company_id: str
    company_name: str
    agent_name: str
    port: Optional[int] = None  
    seed_phrase: Optional[str] = None
    capabilities: List[str] = ["customer_support", "product_information", "document_reference", "transaction_verification", "technical_support", "billing_support", "general_inquiries"]
    description: Optional[str] = None
    webhook_url: Optional[str] = None
    pdf_document_urls: Optional[List[str]] = None
    support_categories: Optional[List[str]] = None  # e.g., ["billing", "technical", "general"]
    company_products: Optional[List[str]] = None  # List of company products/services


class AgentResponse(BaseModel):
    """Response model for agent information"""
    agent_id: str
    name: str
    port: int
    address: str
    status: str
    created_at: str
    process_id: Optional[int] = None


class CompanyAgentResponse(BaseModel):
    """Response model for company support agent information"""
    agent_id: str
    company_id: str
    company_name: str
    agent_name: str
    port: int
    address: str
    status: str
    created_at: str
    process_id: Optional[int] = None
    capabilities: List[str] = []
    description: Optional[str] = None
    webhook_url: Optional[str] = None
    pdf_document_urls: Optional[List[str]] = None
    support_categories: Optional[List[str]] = None
    company_products: Optional[List[str]] = None


class AgentStatusResponse(BaseModel):
    """Response model for agent status information"""
    agent_id: str
    name: str
    status: str
    port: int
    address: str
    process_id: Optional[int] = None
    uptime: Optional[str] = None


class CompanyAgentStatusResponse(BaseModel):
    """Response model for company agent status information"""
    agent_id: str
    company_id: str
    company_name: str
    agent_name: str
    status: str
    port: int
    address: str
    process_id: Optional[int] = None
    uptime: Optional[str] = None
    capabilities: List[str] = []


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    total_agents: int
    active_agents: int
    agents: List[AgentStatusResponse]


class CompanyHealthResponse(BaseModel):
    """Response model for company agents health check"""
    status: str
    total_agents: int
    active_agents: int
    agents: List[CompanyAgentStatusResponse]


class Message(BaseModel):
    """Model for agent messages"""
    message: str


class AgentDiscoveryRequest(BaseModel):
    """Request model for discovering agents by capability"""
    capability: str
    company_id: Optional[str] = None


class AgentDiscoveryResponse(BaseModel):
    """Response model for agent discovery"""
    agents: List[CompanyAgentResponse]
    total_found: int


class AgentMessageRequest(BaseModel):
    """Request model for sending messages to agents"""
    agent_id: str
    message: str
    sender_company_id: Optional[str] = None


class AgentMessageResponse(BaseModel):
    """Response model for agent message responses"""
    agent_id: str
    response: str
    timestamp: str
    status: str


class MailboxMessage(BaseModel):
    """Model for mailbox messages"""
    from_agent: str
    to_agent: str
    message: str
    timestamp: datetime
    message_type: str = "text"
    metadata: Optional[Dict[str, Any]] = None


# REST API Models
class RestRequest(BaseModel):
    """Request model for REST API endpoints"""
    text: str
    sender_company_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class RestResponse(BaseModel):
    """Response model for REST API endpoints"""
    timestamp: int
    text: str
    agent_address: str
    status: str = "success"
    metadata: Optional[Dict[str, Any]] = {}


# Chat Protocol Models for ASI1 LLM
class ChatMessage(BaseModel):
    """Model for chat protocol messages"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = {}


class ChatRequest(BaseModel):
    """Request model for chat protocol"""
    messages: List[ChatMessage]
    model: Optional[str] = "gpt-3.5-turbo"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    stream: Optional[bool] = False


class ChatResponse(BaseModel):
    """Response model for chat protocol"""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Optional[Dict[str, Any]] = None


class ChatChoice(BaseModel):
    """Model for chat response choices"""
    index: int
    message: ChatMessage
    finish_reason: str = "stop"


class ChatUsage(BaseModel):
    """Model for chat usage statistics"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


# PDF Processing Models
class PDFProcessRequest(BaseModel):
    """Request model for processing PDF documents"""
    url: str
    max_length: Optional[int] = 50000


class PDFProcessResponse(BaseModel):
    """Response model for PDF processing"""
    success: bool
    document_id: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    page_count: Optional[int] = None
    content_length: Optional[int] = None
    file_size: Optional[int] = None
    url: Optional[str] = None
    error: Optional[str] = None


class PDFSearchRequest(BaseModel):
    """Request model for searching PDF content"""
    document_id: str
    search_terms: List[str]


class PDFSearchResponse(BaseModel):
    """Response model for PDF search results"""
    success: bool
    document_id: str
    search_results: Optional[Dict[str, Any]] = None
    total_terms_searched: Optional[int] = None
    terms_found: Optional[int] = None
    error: Optional[str] = None


class PDFDocumentInfo(BaseModel):
    """Model for PDF document information"""
    document_id: str
    url: str
    content_length: int
    page_count: int
    file_size: int
    processed_at: str
    status: str


class PDFDocumentsResponse(BaseModel):
    """Response model for listing PDF documents"""
    total_documents: int
    documents: List[PDFDocumentInfo]
