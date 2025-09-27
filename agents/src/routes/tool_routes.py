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


# Note: Refund processing is handled by individual company agents
# Each agent has its own refund processor configured with company-specific settings
# including the expected_address (company's receiving address)
