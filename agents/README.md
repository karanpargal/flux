# Multi-Agent Management Server API Documentation

A FastAPI server for creating and managing multiple uAgents with company-specific agents, wallet management, and blockchain integration.

## Server Information
- **Title**: Multi-Agent Management Server
- **Version**: 1.0.0
- **Description**: A FastAPI server for creating and managing multiple uAgents with company-specific agents

## Base URL
```
http://localhost:8000
```

## Table of Contents
1. [Health & Status](#health--status)
2. [Company Agents](#company-agents)
3. [Chat & Messaging](#chat--messaging)
4. [PDF Processing](#pdf-processing)
5. [REST API](#rest-api)
6. [Tools](#tools)
7. [Wallet Management](#wallet-management)
8. [Webhooks](#webhooks)

---

## Health & Status

### GET `/health`
Get health status of all company agents.

**Response Model**: `CompanyHealthResponse`
```json
{
  "status": "healthy",
  "total_agents": 5,
  "active_agents": 3,
  "agents": [
    {
      "agent_id": "agent_123",
      "company_id": "company_abc",
      "company_name": "Example Corp",
      "agent_name": "Support Agent",
      "status": "running",
      "port": 8001,
      "address": "agent123abc",
      "process_id": 1234,
      "uptime": "2h 30m",
      "capabilities": ["customer_support", "technical_support"],
      "company_address": "123 Main St",
      "wallet_info": {
        "address": "0x123...",
        "balance": "1.5",
        "chain": "ethereum",
        "native_token": "ETH"
      }
    }
  ]
}
```

### GET `/`
Root endpoint with API information.

**Response**:
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

---

## Company Agents

### POST `/company-agents`
Create a new company-specific agent with mailbox agent.

**Request Model**: `CompanyAgentCreateRequest`
```json
{
  "company_id": "company_123",
  "company_name": "Acme Corp",
  "agent_name": "Customer Support Agent",
  "port": 8001,
  "seed_phrase": "optional seed phrase",
  "capabilities": [
    "customer_support",
    "product_information",
    "document_reference",
    "transaction_verification",
    "technical_support",
    "billing_support",
    "general_inquiries",
    "refund_processing"
  ],
  "description": "AI-powered customer support agent",
  "webhook_url": "https://example.com/webhook",
  "pdf_document_urls": [
    "https://example.com/manual.pdf",
    "https://example.com/faq.pdf"
  ],
  "support_categories": ["billing", "technical", "general"],
  "company_products": ["Product A", "Product B"],
  "company_address": "123 Main Street, City",
  "refund_config": {
    "max_refund_amount": "1000000000000000000",
    "refund_token_address": "0x123...",
    "refund_chain": "ethereum"
  }
}
```

**Response Model**: `CompanyAgentResponse`
```json
{
  "agent_id": "agent_123",
  "company_id": "company_123",
  "company_name": "Acme Corp",
  "agent_name": "Customer Support Agent",
  "port": 8001,
  "address": "agent123abc",
  "status": "running",
  "created_at": "2023-10-01T10:00:00Z",
  "process_id": 1234,
  "capabilities": ["customer_support", "technical_support"],
  "description": "AI-powered customer support agent",
  "webhook_url": "https://example.com/webhook",
  "pdf_document_urls": ["https://example.com/manual.pdf"],
  "support_categories": ["billing", "technical"],
  "company_products": ["Product A", "Product B"],
  "company_address": "123 Main Street, City",
  "wallet_info": {
    "address": "0x123...",
    "encrypted_private_key": "encrypted_key",
    "chain": "ethereum",
    "chain_id": 1,
    "native_token": "ETH",
    "created_at": "2023-10-01T10:00:00Z",
    "balance": "1.5",
    "ens_name": "agent.eth",
    "ens_registered": true,
    "ens_registration_status": "registered",
    "agent_id": "agent_123",
    "agent_name": "Customer Support Agent",
    "company_name": "Acme Corp",
    "wallet_purpose": "agent_operations"
  }
}
```

### GET `/company-agents`
List all company agents.

**Response**: Array of `CompanyAgentResponse`

### GET `/company-agents/{agent_id}`
Get specific company agent information.

**Response Model**: `CompanyAgentResponse`

### DELETE `/company-agents/{agent_id}`
Delete a company agent and its mailbox agent.

**Response**:
```json
{
  "status": "deleted",
  "agent_id": "agent_123",
  "message": "Agent and associated resources deleted successfully"
}
```

### POST `/company-agents/discover`
Discover agents by capability.

**Request Model**: `AgentDiscoveryRequest`
```json
{
  "capability": "customer_support",
  "company_id": "company_123"
}
```

**Response Model**: `AgentDiscoveryResponse`
```json
{
  "agents": [
    {
      "agent_id": "agent_123",
      "company_id": "company_123",
      "company_name": "Acme Corp",
      "agent_name": "Support Agent",
      "capabilities": ["customer_support", "technical_support"]
    }
  ],
  "total_found": 1
}
```

### POST `/company-agents/send-message`
Send a message to a specific agent.

**Request Model**: `AgentMessageRequest`
```json
{
  "agent_id": "agent_123",
  "message": "Hello, I need help with my order",
  "sender_company_id": "company_456"
}
```

**Response Model**: `AgentMessageResponse`
```json
{
  "agent_id": "agent_123",
  "response": "Hello! I'd be happy to help you with your order. Can you provide your order number?",
  "timestamp": "2023-10-01T10:30:00Z",
  "status": "success"
}
```

### GET `/company-agents/company/{company_id}`
Get all agents for a specific company.

**Response**: Array of `CompanyAgentResponse`

### GET `/company-agents/health/status`
Get health status of all company agents.

**Response**: Same as `/health`

### GET `/company-agents/capabilities`
Get all available capabilities for company agents.

**Response Model**: `AvailableCapabilitiesResponse`
```json
{
  "capabilities": [
    {
      "name": "customer_support",
      "description": "Handle customer inquiries and support requests",
      "tools": [
        {
          "name": "ticket_system",
          "type": "integration"
        }
      ]
    }
  ],
  "total_capabilities": 8
}
```

---

## Chat & Messaging

### POST `/chat/completions?agent_id={agent_id}`
Central chat completion endpoint that routes requests to specific agents.

**Request Model**: `ChatRequest`
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hello, I need help with my account",
      "timestamp": "2023-10-01T10:00:00Z",
      "metadata": {}
    }
  ],
  "model": "asi1-fast",
  "temperature": 0.7,
  "max_tokens": 1000,
  "stream": false
}
```

**Response Model**: `ChatResponse`
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1696156800,
  "model": "asi1-fast",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! I'd be happy to help you with your account. What specific issue are you experiencing?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 25,
    "total_tokens": 40
  }
}
```

### GET `/chat/agents`
List all available agents for chat completion.

**Response**: Array of `CompanyAgentResponse`

### GET `/chat/agents/{agent_id}`
Get information about a specific agent.

**Response Model**: `CompanyAgentResponse`

---

## PDF Processing

### POST `/pdf/process`
Process a PDF document from URL and extract text content.

**Request Model**: `PDFProcessRequest`
```json
{
  "url": "https://example.com/document.pdf",
  "max_length": 50000
}
```

**Response Model**: `PDFProcessResponse`
```json
{
  "success": true,
  "document_id": "doc_123",
  "content": "Extracted PDF text content...",
  "metadata": {
    "title": "Document Title",
    "author": "Author Name"
  },
  "page_count": 10,
  "content_length": 5000,
  "file_size": 1024000,
  "url": "https://example.com/document.pdf",
  "error": null
}
```

### GET `/pdf/documents/{document_id}`
Get processed document content by ID.

**Response**:
```json
{
  "document_id": "doc_123",
  "content": "Full document content...",
  "metadata": {},
  "status": "processed"
}
```

### POST `/pdf/search`
Search for terms within a processed document.

**Request Model**: `PDFSearchRequest`
```json
{
  "document_id": "doc_123",
  "search_terms": ["refund", "policy", "terms"]
}
```

**Response Model**: `PDFSearchResponse`
```json
{
  "success": true,
  "document_id": "doc_123",
  "search_results": {
    "refund": [
      {
        "page": 5,
        "context": "Our refund policy allows..."
      }
    ]
  },
  "total_terms_searched": 3,
  "terms_found": 2,
  "error": null
}
```

### GET `/pdf/documents`
List all processed PDF documents.

**Response Model**: `PDFDocumentsResponse`
```json
{
  "total_documents": 5,
  "documents": [
    {
      "document_id": "doc_123",
      "url": "https://example.com/document.pdf",
      "content_length": 5000,
      "page_count": 10,
      "file_size": 1024000,
      "processed_at": "2023-10-01T10:00:00Z",
      "status": "processed"
    }
  ]
}
```

### DELETE `/pdf/documents/{document_id}`
Delete a processed document.

**Response**:
```json
{
  "status": "deleted",
  "document_id": "doc_123",
  "message": "Document deleted successfully"
}
```

---

## REST API

### GET `/api/rest/agents/{agent_id}/get`
Get information from a specific agent via REST GET.

**Response Model**: `RestResponse`
```json
{
  "timestamp": 1696156800,
  "text": "Agent information response",
  "agent_address": "agent123abc",
  "status": "success",
  "metadata": {}
}
```

### POST `/api/rest/agents/{agent_id}/post`
Send a message to a specific agent via REST POST.

**Request Model**: `RestRequest`
```json
{
  "text": "Hello, I need assistance",
  "sender_company_id": "company_456",
  "metadata": {
    "priority": "high"
  }
}
```

**Response Model**: `RestResponse`
```json
{
  "timestamp": 1696156800,
  "text": "Hello! How can I help you today?",
  "agent_address": "agent123abc",
  "status": "success",
  "metadata": {}
}
```

### POST `/api/rest/agents/{agent_id}/chat/completions`
Chat with a specific agent using ASI1 LLM compatible chat protocol.

**Request Model**: `ChatRequest`
**Response Model**: `ChatResponse`

### GET `/api/rest/agents`
List all agents with their REST API information.

**Response**:
```json
[
  {
    "agent_id": "agent_123",
    "company_id": "company_123",
    "company_name": "Acme Corp",
    "agent_name": "Support Agent",
    "port": 8001,
    "address": "agent123abc",
    "status": "running",
    "capabilities": ["customer_support"],
    "description": "Customer support agent",
    "rest_endpoints": {
      "get": "http://localhost:8001/rest/get",
      "post": "http://localhost:8001/rest/post",
      "chat": "http://localhost:8001/chat/completions"
    }
  }
]
```

### GET `/api/rest/agents/{agent_id}/endpoints`
Get REST API endpoints for a specific agent.

**Response**:
```json
{
  "agent_id": "agent_123",
  "agent_name": "Support Agent",
  "company_name": "Acme Corp",
  "base_url": "http://localhost:8001",
  "endpoints": {
    "get": "http://localhost:8001/rest/get",
    "post": "http://localhost:8001/rest/post",
    "chat": "http://localhost:8001/chat/completions"
  },
  "usage_examples": {
    "get_request": "curl http://localhost:8001/rest/get",
    "post_request": "curl -X POST -H 'Content-Type: application/json' -d '{\"text\": \"Hello\"}' http://localhost:8001/rest/post",
    "chat_request": "curl -X POST -H 'Content-Type: application/json' -d '{\"messages\": [{\"role\": \"user\", \"content\": \"Hello\"}]}' http://localhost:8001/chat/completions"
  }
}
```

---

## Tools

### GET `/tools/capabilities`
Get information about available tools and their capabilities.

**Response**:
```json
{
  "tools": [
    {
      "name": "calculator",
      "description": "Perform mathematical calculations",
      "endpoints": ["/tools/calculator/calculate"]
    },
    {
      "name": "pdf_reader",
      "description": "Read and process PDF documents",
      "endpoints": ["/tools/pdf/read"]
    },
    {
      "name": "refund_processor",
      "description": "Process blockchain refund transactions",
      "endpoints": ["/tools/refund/process", "/tools/refund/validate"]
    }
  ]
}
```

### Calculator Endpoints

#### POST `/tools/calculator/calculate`
Perform mathematical calculations.

**Request**:
```json
{
  "expression": "2 + 2 * 3"
}
```

**Response**:
```json
{
  "expression": "2 + 2 * 3",
  "result": 8,
  "success": true,
  "error": null
}
```

#### GET `/tools/calculator/calculate?expression={expression}`
Perform mathematical calculations (simple GET endpoint).

### PDF Reader Endpoints

#### POST `/tools/pdf/read`
Read content from a PDF URL.

**Request**:
```json
{
  "url": "https://example.com/document.pdf",
  "action": "read",
  "max_length": 50000
}
```

**Response**:
```json
{
  "success": true,
  "content": "Extracted PDF content...",
  "metadata": {
    "pages": 10,
    "title": "Document Title"
  },
  "error": null
}
```

#### GET `/tools/pdf/read?url={url}&max_length={max_length}`
Read content from a PDF URL (simple GET endpoint).

### Refund Processing Endpoints

#### POST `/tools/refund/process`
Process a refund transaction.

**Request**:
```json
{
  "user_address": "0x123...",
  "transaction_hash": "0xabc...",
  "requested_amount": "1000000000000000000",
  "agent_private_key": "encrypted_private_key",
  "refund_chain": "ethereum",
  "company_address": "0x456...",
  "max_refund_amount": "5000000000000000000",
  "reason": "Product defect"
}
```

**Response**:
```json
{
  "success": true,
  "refund_tx_hash": "0xdef...",
  "refund_amount": "1000000000000000000",
  "gas_used": 21000,
  "error_message": null,
  "processing_time": 2.5
}
```

#### POST `/tools/refund/validate`
Validate a refund request without processing.

**Request**:
```json
{
  "user_address": "0x123...",
  "transaction_hash": "0xabc...",
  "requested_amount": "1000000000000000000",
  "refund_chain": "ethereum",
  "company_address": "0x456...",
  "max_refund_amount": "5000000000000000000"
}
```

**Response**:
```json
{
  "is_valid": true,
  "validation_errors": [],
  "transaction_verified": true,
  "criteria_met": true,
  "amount_within_limits": true,
  "time_valid": true,
  "chain_valid": true,
  "token_valid": true
}
```

### Agent Integration Endpoints

#### POST `/tools/agent/calculator`
Process calculation request from an agent.

#### POST `/tools/agent/pdf`
Process PDF request from an agent.

#### POST `/tools/agent/refund`
Process refund request from an agent.

#### POST `/tools/agent/refund/validate`
Validate refund request from an agent.

---

## Wallet Management

### GET `/wallets/agent/{agent_id}`
Get wallet information for a specific agent.

**Response Model**: `AgentWalletInfo`
```json
{
  "address": "0x123...",
  "encrypted_private_key": "encrypted_key",
  "chain": "ethereum",
  "chain_id": 1,
  "native_token": "ETH",
  "created_at": "2023-10-01T10:00:00Z",
  "balance": "1.5",
  "ens_name": "agent.eth",
  "ens_registered": true,
  "ens_registration_status": "registered",
  "agent_id": "agent_123",
  "agent_name": "Support Agent",
  "company_name": "Acme Corp",
  "wallet_purpose": "agent_operations"
}
```

### GET `/wallets/agent/{agent_id}/balance`
Get current balance for an agent's wallet.

**Response Model**: `WalletBalanceResponse`
```json
{
  "agent_id": "agent_123",
  "wallet_address": "0x123...",
  "balance": "1.5",
  "native_token": "ETH",
  "chain": "ethereum",
  "last_updated": "2023-10-01T10:30:00Z"
}
```

### GET `/wallets/agent/{agent_id}/ens`
Get ENS registration information for an agent's wallet.

**Response Model**: `ENSRegistrationResponse`
```json
{
  "agent_id": "agent_123",
  "wallet_address": "0x123...",
  "ens_name": "agent.eth",
  "registration_status": "registered",
  "registration_note": null
}
```

### POST `/wallets/agent/{agent_id}/ens/register`
Register or update ENS name for an agent's wallet.

**Response Model**: `ENSRegistrationResponse`

### GET `/wallets`
List all agent wallets.

**Response**: Array of `AgentWalletInfo`

### GET `/wallets/balances`
Get balances for all agent wallets.

**Response**: Array of `WalletBalanceResponse`

### GET `/wallets/stats`
Get statistics about agent wallets.

**Response**:
```json
{
  "total_agents": 10,
  "agents_with_wallets": 8,
  "agents_with_ens": 5,
  "wallet_coverage_percentage": 80.0,
  "ens_coverage_percentage": 62.5,
  "chains_used": {
    "ethereum": 6,
    "polygon": 2
  },
  "estimated_total_balance_eth": 15.75
}
```

### ENS Testing Endpoints

#### GET `/wallets/ens/test`
Test ENS functionality on Sepolia testnet.

**Response Model**: `ENSTestResponse`
```json
{
  "ens_initialized": true,
  "web3_connected": true,
  "network_info": {
    "chain_id": 11155111,
    "network": "sepolia"
  },
  "test_resolution": {
    "test_name": "test.eth",
    "resolved_address": "0x123..."
  },
  "errors": [],
  "summary": {
    "all_tests_passed": true,
    "total_tests": 3,
    "passed_tests": 3
  }
}
```

#### POST `/wallets/ens/resolve`
Resolve an ENS name to an address on Sepolia testnet.

**Request Model**: `ENSResolveRequest`
```json
{
  "ens_name": "example.eth"
}
```

**Response Model**: `ENSResolveResponse`
```json
{
  "ens_name": "example.eth",
  "address": "0x123...",
  "success": true,
  "error": null
}
```

#### GET `/wallets/ens/reverse/{address}`
Get ENS name for an address (reverse resolution) on Sepolia testnet.

**Response**:
```json
{
  "address": "0x123...",
  "ens_name": "example.eth",
  "success": true,
  "error": null
}
```

#### GET `/wallets/ens/owner/{ens_name}`
Get the owner of an ENS name on Sepolia testnet.

**Response**:
```json
{
  "ens_name": "example.eth",
  "owner": "0x123...",
  "success": true,
  "error": null
}
```

#### GET `/wallets/ens/resolver/{ens_name}`
Get the resolver address for an ENS name on Sepolia testnet.

**Response**:
```json
{
  "ens_name": "example.eth",
  "resolver_address": "0x456...",
  "success": true,
  "error": null
}
```

#### GET `/wallets/ens/text/{ens_name}/{key}`
Get text record for an ENS name on Sepolia testnet.

**Response**:
```json
{
  "ens_name": "example.eth",
  "key": "description",
  "value": "My ENS domain",
  "success": true,
  "error": null
}
```

---

## Webhooks

### POST `/webhooks/agent/{agent_id}`
Webhook endpoint for receiving messages from agents.

**Request**:
```json
{
  "message": "Hello from external system",
  "sender_company_id": "company_456",
  "message_type": "text",
  "metadata": {
    "priority": "high",
    "source": "customer_portal"
  }
}
```

**Response**:
```json
{
  "status": "received",
  "agent_id": "agent_123",
  "timestamp": "2023-10-01T10:30:00Z",
  "message": "Message received by agent agent_123",
  "sender_company_id": "company_456"
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message describing what went wrong",
  "status_code": 400
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request - Invalid input data
- `404`: Not Found - Resource not found
- `500`: Internal Server Error - Server-side error

---

## Authentication

Currently, the API does not require authentication. In production, you should implement proper authentication and authorization mechanisms.

---

## Rate Limiting

No rate limiting is currently implemented. Consider adding rate limiting for production use.

---

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the server:
   ```bash
   python -m src.main
   ```

3. The server will be available at `http://localhost:8000`

4. Access the interactive API documentation at `http://localhost:8000/docs`

---

## Example Usage

### Creating a Company Agent
```bash
curl -X POST "http://localhost:8000/company-agents" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "acme_corp",
    "company_name": "Acme Corporation",
    "agent_name": "Customer Support Bot",
    "capabilities": ["customer_support", "technical_support"],
    "description": "AI-powered customer support agent"
  }'
```

### Sending a Chat Message
```bash
curl -X POST "http://localhost:8000/chat/completions?agent_id=agent_123" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "I need help with my order"
      }
    ]
  }'
```

### Processing a PDF
```bash
curl -X POST "http://localhost:8000/pdf/process" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/manual.pdf",
    "max_length": 50000
  }'
```

---

## Support

For issues and questions, please refer to the project repository or contact the development team.
