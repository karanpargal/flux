import os
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from ..tools import WebpageReader, PDFReader, read_webpage_content, search_webpage


class ToolService:
    """Service for managing tool operations for company agents"""
    
    def __init__(self):
        self.webpage_reader = WebpageReader()
        self.pdf_reader = PDFReader()
    
    async def read_webpage(self, url: str, max_length: int = 10000) -> Dict[str, Any]:
        """
        Read content from a webpage
        
        Args:
            url: The URL to read
            max_length: Maximum length of extracted text
            
        Returns:
            Dictionary containing webpage content and metadata
        """
        try:
            result = await self.webpage_reader.read_webpage(url, max_length)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read webpage: {str(e)}")
    
    async def search_webpage(self, url: str, search_terms: List[str], max_length: int = 5000) -> Dict[str, Any]:
        """
        Search for specific terms within a webpage
        
        Args:
            url: The URL to search
            search_terms: List of terms to search for
            max_length: Maximum length of extracted text
            
        Returns:
            Dictionary containing search results
        """
        try:
            result = await self.webpage_reader.search_webpage_content(url, search_terms, max_length)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to search webpage: {str(e)}")
    
    async def extract_webpage_links(self, url: str, filter_domain: bool = True) -> Dict[str, Any]:
        """
        Extract all links from a webpage
        
        Args:
            url: The URL to extract links from
            filter_domain: Whether to filter links to the same domain
            
        Returns:
            Dictionary containing extracted links
        """
        try:
            result = await self.webpage_reader.extract_links(url, filter_domain)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to extract links: {str(e)}")
    
    async def read_pdf_from_url(self, url: str, max_length: int = 50000) -> Dict[str, Any]:
        """
        Read content from a PDF URL
        
        Args:
            url: URL to the PDF file
            max_length: Maximum length of extracted text
            
        Returns:
            Dictionary containing PDF content and metadata
        """
        try:
            result = await self.pdf_reader.read_pdf_from_url(url, max_length)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read PDF from URL: {str(e)}")
    
    async def process_webpage_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a webpage reading request from an agent
        
        Args:
            request_data: Dictionary containing request parameters
            
        Returns:
            Dictionary containing processed results
        """
        try:
            url = request_data.get("url")
            if not url:
                raise HTTPException(status_code=400, detail="URL is required")
            
            action = request_data.get("action", "read")
            max_length = request_data.get("max_length", 10000)
            
            if action == "read":
                return await self.read_webpage(url, max_length)
            elif action == "search":
                search_terms = request_data.get("search_terms", [])
                if not search_terms:
                    raise HTTPException(status_code=400, detail="Search terms are required for search action")
                return await self.search_webpage(url, search_terms, max_length)
            elif action == "extract_links":
                filter_domain = request_data.get("filter_domain", True)
                return await self.extract_webpage_links(url, filter_domain)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process webpage request: {str(e)}")
    
    async def process_pdf_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a PDF reading request from an agent
        
        Args:
            request_data: Dictionary containing request parameters
            
        Returns:
            Dictionary containing processed results
        """
        try:
            url = request_data.get("url")
            if not url:
                raise HTTPException(status_code=400, detail="URL is required")
            
            action = request_data.get("action", "read")
            max_length = request_data.get("max_length", 50000)
            
            if action == "read":
                return await self.read_pdf_from_url(url, max_length)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown action: {action}. Only 'read' is supported for URL-based PDFs")
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process PDF request: {str(e)}")
    
    async def get_tool_capabilities(self) -> Dict[str, Any]:
        """
        Get information about available tools and their capabilities
        
        Returns:
            Dictionary containing tool capabilities
        """
        return {
            "webpage_reader": {
                "description": "Read and extract content from web pages",
                "capabilities": [
                    "read_webpage",
                    "search_webpage_content", 
                    "extract_links"
                ],
                "supported_formats": ["html", "text"],
                "max_content_length": 10000
            },
            "pdf_reader": {
                "description": "Read and extract content from PDF files via URL",
                "capabilities": [
                    "read_pdf_from_url"
                ],
                "supported_formats": ["pdf"],
                "max_content_length": 50000
            }
        }
    
    async def close(self):
        """Close tool resources"""
        await self.webpage_reader.close()
