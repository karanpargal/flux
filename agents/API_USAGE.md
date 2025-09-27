# Multi-Agent Management Server API Usage Guide

This API provides comprehensive management of company-specific agents with multiple communication protocols and tools.

## API Overview

The server provides the following main functionalities:
- **Company Agent Management**: Create, manage, and monitor company-specific agents
- **Chat Protocol**: OpenAI-compatible chat completions with specific agents
- **REST API**: Traditional REST endpoints for agent communication
- **PDF Processing**: Document processing and search capabilities
- **Web Tools**: Webpage reading and PDF processing tools
- **Webhooks**: Agent-to-agent communication via webhooks

## API Endpoints

### Company Agent Management

#### Create Company Agent
```bash
POST /company-agents
Content-Type: application/json

{
  "company_id": "company_123",
  "company_name": "Acme Corp",
  "agent_name": "Customer Support Bot",
  "port": 8001,
  "seed_phrase": "optional_seed_phrase",
  "capabilities": ["customer_support", "order_tracking", "document_reference", "transaction_verification"],
  "description": "Handles customer inquiries and order tracking",
  "webhook_url": "https://your-company.com/webhook",
  "pdf_document_urls": ["https://example.com/docs.pdf"],
  "support_categories": ["billing", "technical", "general"],
  "company_products": ["Product A", "Product B"]
}
```

#### List Company Agents
```bash
GET /company-agents
```

#### Get Specific Agent
```bash
GET /company-agents/{agent_id}
```

#### Delete Agent
```bash
DELETE /company-agents/{agent_id}
```

#### Get Agents by Company
```bash
GET /company-agents/company/{company_id}
```

#### Discover Agents by Capability
```bash
POST /company-agents/discover
Content-Type: application/json

{
  "capability": "customer_support",
  "company_id": "optional_company_filter"
}
```

#### Send Message to Agent
```bash
POST /company-agents/send-message
Content-Type: application/json

{
  "agent_id": "agent_123",
  "message": "Hello, I need help",
  "sender_company_id": "company_456"
}
```

#### Get Available Capabilities
```bash
GET /company-agents/capabilities
```

#### Get Company Agents Health Status
```bash
GET /company-agents/health/status
```

### Chat Protocol (OpenAI Compatible)

#### Chat with Specific Agent
```bash
POST /chat/completions?agent_id={agent_id}
Content-Type: application/json

{
  "messages": [
    {
      "role": "user",
      "content": "Hello, I need help with my order"
    }
  ],
  "model": "asi1-mini",
  "temperature": 0.7,
  "max_tokens": 1000,
  "stream": false
}
```

#### List Available Agents for Chat
```bash
GET /chat/agents
```

#### Get Agent Information
```bash
GET /chat/agents/{agent_id}
```

### REST API Protocol

#### Get Agent Information
```bash
GET /api/rest/agents/{agent_id}/get
```

#### Send Message to Agent
```bash
POST /api/rest/agents/{agent_id}/post
Content-Type: application/json

{
  "text": "Hello, I need help",
  "sender_company_id": "company_123",
  "metadata": {"priority": "high"}
}
```

#### Chat with Agent (REST)
```bash
POST /api/rest/agents/{agent_id}/chat/completions
Content-Type: application/json

{
  "messages": [
    {
      "role": "user",
      "content": "Hello"
    }
  ],
  "model": "asi1-mini",
  "temperature": 0.7
}
```

#### List All Agents with REST Info
```bash
GET /api/rest/agents
```

#### Get Agent REST Endpoints
```bash
GET /api/rest/agents/{agent_id}/endpoints
```

### PDF Processing

#### Process PDF Document
```bash
POST /pdf/process
Content-Type: application/json

{
  "url": "https://example.com/document.pdf",
  "max_length": 50000
}
```

#### Get Document Content
```bash
GET /pdf/documents/{document_id}
```

#### Search Document Content
```bash
POST /pdf/search
Content-Type: application/json

{
  "document_id": "doc_123",
  "search_terms": ["keyword1", "keyword2"]
}
```

#### List Processed Documents
```bash
GET /pdf/documents
```

#### Delete Document
```bash
DELETE /pdf/documents/{document_id}
```

### Web Tools

#### Get Tool Capabilities
```bash
GET /tools/capabilities
```

#### Read Webpage
```bash
POST /tools/webpage/read
Content-Type: application/json

{
  "url": "https://example.com",
  "action": "read",
  "max_length": 10000
}
```

#### Search Webpage
```bash
POST /tools/webpage/search
Content-Type: application/json

{
  "url": "https://example.com",
  "search_terms": ["keyword1", "keyword2"],
  "max_length": 5000
}
```

#### Extract Webpage Links
```bash
POST /tools/webpage/extract-links
Content-Type: application/json

{
  "url": "https://example.com",
  "filter_domain": true
}
```

#### Read PDF via Tools
```bash
POST /tools/pdf/read
Content-Type: application/json

{
  "url": "https://example.com/document.pdf",
  "action": "read",
  "max_length": 50000
}
```

### Webhooks

#### Agent Webhook
```bash
POST /webhooks/agent/{agent_id}
Content-Type: application/json

{
  "message": "Hello from another agent",
  "sender_company_id": "company_123",
  "message_type": "text",
  "metadata": {"priority": "high"}
}
```

## Usage Examples

### 1. Create a Company Agent

```bash
curl -X POST "http://localhost:8000/company-agents" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "acme_123",
    "company_name": "Acme Corporation",
    "agent_name": "Support Bot",
    "capabilities": ["customer_support", "order_help", "document_reference"],
    "description": "Customer support agent",
    "pdf_document_urls": ["https://acme.com/docs.pdf"],
    "support_categories": ["billing", "technical"],
    "company_products": ["Product A", "Product B"]
  }'
```

### 2. Get Available Agents

```bash
curl -X GET "http://localhost:8000/chat/agents"
```

### 3. Chat with an Agent (OpenAI Compatible)

```bash
curl -X POST "http://localhost:8000/chat/completions?agent_id=your_agent_id" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user", 
        "content": "I need help with my order #12345"
      }
    ],
    "model": "asi1-mini",
    "temperature": 0.7,
    "max_tokens": 1000
  }'
```

### 4. Send Message via REST API

```bash
curl -X POST "http://localhost:8000/api/rest/agents/your_agent_id/post" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, I need help with billing",
    "sender_company_id": "customer_456",
    "metadata": {"priority": "high"}
  }'
```

### 5. Process PDF Document

```bash
curl -X POST "http://localhost:8000/pdf/process" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/manual.pdf",
    "max_length": 50000
  }'
```

### 6. Read Webpage Content

```bash
curl -X POST "http://localhost:8000/tools/webpage/read" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "action": "read",
    "max_length": 10000
  }'
```

### 7. Discover Agents by Capability

```bash
curl -X POST "http://localhost:8000/company-agents/discover" \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "customer_support",
    "company_id": "acme_123"
  }'
```

## Response Formats

### Chat Completion Response
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "asi1-mini",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "I'd be happy to help you with order #12345..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 50,
    "total_tokens": 70
  }
}
```

### Company Agent Response
```json
{
  "agent_id": "agent_123",
  "company_id": "acme_123",
  "company_name": "Acme Corporation",
  "agent_name": "Support Bot",
  "port": 8001,
  "address": "http://localhost:8001",
  "status": "running",
  "created_at": "2024-01-15T10:30:00Z",
  "process_id": 12345,
  "capabilities": ["customer_support", "order_help"],
  "description": "Customer support agent",
  "webhook_url": "https://acme.com/webhook",
  "pdf_document_urls": ["https://acme.com/docs.pdf"],
  "support_categories": ["billing", "technical"],
  "company_products": ["Product A", "Product B"]
}
```

### PDF Process Response
```json
{
  "success": true,
  "document_id": "doc_123",
  "content": "Extracted PDF content...",
  "metadata": {
    "title": "Document Title",
    "author": "Author Name"
  },
  "page_count": 10,
  "content_length": 5000,
  "file_size": 1024000,
  "url": "https://example.com/document.pdf"
}
```

### Tool Response
```json
{
  "success": true,
  "content": "Webpage content...",
  "metadata": {
    "title": "Page Title",
    "url": "https://example.com",
    "content_length": 5000
  },
  "links": ["https://example.com/link1", "https://example.com/link2"]
}
```

## Health Check

```bash
GET /health
```

Returns the status of all company agents and their health information:

```json
{
  "status": "healthy",
  "total_agents": 3,
  "active_agents": 2,
  "agents": [
    {
      "agent_id": "agent_123",
      "company_id": "acme_123",
      "company_name": "Acme Corporation",
      "agent_name": "Support Bot",
      "status": "running",
      "port": 8001,
      "address": "http://localhost:8001",
      "process_id": 12345,
      "uptime": "2h 30m",
      "capabilities": ["customer_support", "order_help"]
    }
  ]
}
```

## Root Endpoint

```bash
GET /
```

Returns API information and available endpoints:

```json
{
  "message": "Company Agent Management Server",
  "version": "1.0.0",
  "endpoints": {
    "create_company_agent": "POST /company-agents",
    "list_company_agents": "GET /company-agents",
    "get_company_agent": "GET /company-agents/{agent_id}",
    "delete_company_agent": "DELETE /company-agents/{agent_id}",
    "discover_agents": "POST /company-agents/discover",
    "send_message": "POST /company-agents/send-message",
    "chat_completion": "POST /chat/completions?agent_id={agent_id}",
    "list_available_agents": "GET /chat/agents",
    "get_agent_info": "GET /chat/agents/{agent_id}",
    "health_check": "GET /health"
  }
}
```
