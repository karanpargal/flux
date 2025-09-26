# Company Agent API Usage Guide

This API now focuses on company-specific agents with a central chat completion endpoint.

## Key Changes

- **Removed**: Regular agent service and routes
- **Kept**: Company agent service and routes  
- **Added**: Central chat completion endpoint

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
  "capabilities": ["customer_support", "order_tracking"],
  "description": "Handles customer inquiries and order tracking",
  "webhook_url": "https://your-company.com/webhook"
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

### Central Chat Completion

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
  "max_tokens": 1000
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

## Usage Examples

### 1. Create a Company Agent

```bash
curl -X POST "http://localhost:8000/company-agents" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "acme_123",
    "company_name": "Acme Corporation",
    "agent_name": "Support Bot",
    "capabilities": ["customer_support", "order_help"],
    "description": "Customer support agent"
  }'
```

### 2. Get Available Agents

```bash
curl -X GET "http://localhost:8000/chat/agents"
```

### 3. Chat with an Agent

```bash
curl -X POST "http://localhost:8000/chat/completions?agent_id=your_agent_id" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user", 
        "content": "I need help with my order #12345"
      }
    ]
  }'
```

## Response Format

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

## Health Check

```bash
GET /health
```

Returns the status of all company agents and their health information.
