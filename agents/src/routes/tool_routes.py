from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from ..services.tool_service import ToolService


class WebpageRequest(BaseModel):
    url: str
    action: str = "read"  # read, search, extract_links
    max_length: int = 10000
    search_terms: Optional[List[str]] = None
    filter_domain: bool = True


class PDFRequest(BaseModel):
    file_path: str
    action: str = "read"  # read, search, extract_pages
    max_length: int = 50000
    search_terms: Optional[List[str]] = None
    page_numbers: Optional[List[int]] = None


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


# Webpage Reader Endpoints

@router.post("/webpage/read")
async def read_webpage(
    request: WebpageRequest,
    tool_service: ToolService = Depends(get_tool_service)
):
    """Read content from a webpage"""
    return await tool_service.process_webpage_request(request.dict())


@router.get("/webpage/read")
async def read_webpage_simple(
    url: str,
    max_length: int = 10000,
    tool_service: ToolService = Depends(get_tool_service)
):
    """Read content from a webpage (simple GET endpoint)"""
    request_data = {
        "url": url,
        "action": "read",
        "max_length": max_length
    }
    return await tool_service.process_webpage_request(request_data)


@router.post("/webpage/search")
async def search_webpage(
    url: str,
    search_terms: List[str],
    max_length: int = 5000,
    tool_service: ToolService = Depends(get_tool_service)
):
    """Search for specific terms within a webpage"""
    request_data = {
        "url": url,
        "action": "search",
        "search_terms": search_terms,
        "max_length": max_length
    }
    return await tool_service.process_webpage_request(request_data)


@router.post("/webpage/extract-links")
async def extract_webpage_links(
    url: str,
    filter_domain: bool = True,
    tool_service: ToolService = Depends(get_tool_service)
):
    """Extract all links from a webpage"""
    request_data = {
        "url": url,
        "action": "extract_links",
        "filter_domain": filter_domain
    }
    return await tool_service.process_webpage_request(request_data)


# PDF Reader Endpoints

@router.post("/pdf/read")
async def read_pdf(
    request: PDFRequest,
    tool_service: ToolService = Depends(get_tool_service)
):
    """Read content from a PDF file"""
    return await tool_service.process_pdf_request(request.dict())


@router.post("/pdf/upload")
async def read_pdf_upload(
    file: UploadFile = File(...),
    max_length: int = 50000,
    tool_service: ToolService = Depends(get_tool_service)
):
    """Read content from an uploaded PDF file"""
    return await tool_service.read_pdf_from_upload(file, max_length)


@router.post("/pdf/search")
async def search_pdf(
    file_path: str,
    search_terms: List[str],
    max_length: int = 10000,
    tool_service: ToolService = Depends(get_tool_service)
):
    """Search for specific terms within a PDF"""
    request_data = {
        "file_path": file_path,
        "action": "search",
        "search_terms": search_terms,
        "max_length": max_length
    }
    return await tool_service.process_pdf_request(request_data)


@router.post("/pdf/extract-pages")
async def extract_pdf_pages(
    file_path: str,
    page_numbers: Optional[List[int]] = None,
    tool_service: ToolService = Depends(get_tool_service)
):
    """Extract specific pages from a PDF"""
    request_data = {
        "file_path": file_path,
        "action": "extract_pages",
        "page_numbers": page_numbers
    }
    return await tool_service.process_pdf_request(request_data)


# Agent Integration Endpoints

@router.post("/agent/webpage")
async def agent_webpage_request(
    request: Dict[str, Any],
    tool_service: ToolService = Depends(get_tool_service)
):
    """Process webpage request from an agent"""
    return await tool_service.process_webpage_request(request)


@router.post("/agent/pdf")
async def agent_pdf_request(
    request: Dict[str, Any],
    tool_service: ToolService = Depends(get_tool_service)
):
    """Process PDF request from an agent"""
    return await tool_service.process_pdf_request(request)
