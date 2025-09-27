from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Dict, Any
import json
from datetime import datetime

from ..services import get_company_agent_service
from ..services.company_agent_service import CompanyAgentService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])




@router.post("/agent/{agent_id}")
async def agent_webhook(
    agent_id: str,
    request: Request,
    company_agent_service: CompanyAgentService = Depends(get_company_agent_service)
):
    """Webhook endpoint for receiving messages from agents"""
    try:
        # Parse the incoming request
        body = await request.body()
        data = json.loads(body.decode('utf-8'))
        
        # Extract message information
        message = data.get('message', '')
        sender_company_id = data.get('sender_company_id', '')
        message_type = data.get('message_type', 'text')
        metadata = data.get('metadata', {})
        
        # Process the message (this would typically involve routing to the appropriate agent)
        response = {
            "status": "received",
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "message": f"Message received by agent {agent_id}",
            "sender_company_id": sender_company_id
        }
        
        # Log the message for debugging
        print(f"Webhook received for agent {agent_id}: {message}")
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")




