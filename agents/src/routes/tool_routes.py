from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from ..services.tool_service import ToolService


class CalculationRequest(BaseModel):
    expression: str


class PDFRequest(BaseModel):
    url: str
    action: str = "read"  # read
    max_length: int = 50000


class RefundRequest(BaseModel):
    user_address: str
    transaction_hash: str
    requested_amount: str
    agent_private_key: str
    refund_chain: str
    company_address: str
    max_refund_amount: Optional[str] = None
    reason: Optional[str] = None


class RefundValidationRequest(BaseModel):
    user_address: str
    transaction_hash: str
    requested_amount: str
    refund_chain: str
    company_address: str
    max_refund_amount: Optional[str] = None


router = APIRouter(prefix="/tools", tags=["tools"])


def get_tool_service() -> ToolService:
    """Dependency to get tool service instance"""
    return ToolService()


@router.get("/capabilities")
async def get_tool_capabilities(
    tool_service: ToolService = Depends(get_tool_service)
):
    """Get information about available tools and their capabilities"""
    return await tool_service.get_tool_capabilities()


# Calculator Endpoints

@router.post("/calculator/calculate")
async def calculate(
    request: CalculationRequest,
    tool_service: ToolService = Depends(get_tool_service)
):
    """Perform mathematical calculations"""
    return await tool_service.process_calculation_request(request.dict())


@router.get("/calculator/calculate")
async def calculate_simple(
    expression: str,
    tool_service: ToolService = Depends(get_tool_service)
):
    """Perform mathematical calculations (simple GET endpoint)"""
    request_data = {
        "expression": expression
    }
    return await tool_service.process_calculation_request(request_data)


# PDF Reader Endpoints

@router.post("/pdf/read")
async def read_pdf(
    request: PDFRequest,
    tool_service: ToolService = Depends(get_tool_service)
):
    """Read content from a PDF URL"""
    return await tool_service.process_pdf_request(request.dict())


@router.get("/pdf/read")
async def read_pdf_simple(
    url: str,
    max_length: int = 50000,
    tool_service: ToolService = Depends(get_tool_service)
):
    """Read content from a PDF URL (simple GET endpoint)"""
    request_data = {
        "url": url,
        "action": "read",
        "max_length": max_length
    }
    return await tool_service.process_pdf_request(request_data)


# Agent Integration Endpoints

@router.post("/agent/calculator")
async def agent_calculation_request(
    request: Dict[str, Any],
    tool_service: ToolService = Depends(get_tool_service)
):
    """Process calculation request from an agent"""
    return await tool_service.process_calculation_request(request)


@router.post("/agent/pdf")
async def agent_pdf_request(
    request: Dict[str, Any],
    tool_service: ToolService = Depends(get_tool_service)
):
    """Process PDF request from an agent"""
    return await tool_service.process_pdf_request(request)


# Refund Processor Endpoints

@router.post("/refund/process")
async def process_refund(
    request: RefundRequest,
    tool_service: ToolService = Depends(get_tool_service)
):
    """Process a refund transaction"""
    return await tool_service.process_refund_request(request.dict())


@router.post("/refund/validate")
async def validate_refund(
    request: RefundValidationRequest,
    tool_service: ToolService = Depends(get_tool_service)
):
    """Validate a refund request without processing"""
    return await tool_service.validate_refund_request(request.dict())


@router.post("/agent/refund")
async def agent_refund_request(
    request: Dict[str, Any],
    tool_service: ToolService = Depends(get_tool_service)
):
    """Process refund request from an agent"""
    return await tool_service.process_refund_request(request)


@router.post("/agent/refund/validate")
async def agent_refund_validation(
    request: Dict[str, Any],
    tool_service: ToolService = Depends(get_tool_service)
):
    """Validate refund request from an agent"""
    return await tool_service.validate_refund_request(request)
