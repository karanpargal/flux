import os
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import HTTPException, UploadFile
import aiofiles

from ..tools import WebpageReader, PDFReader, read_webpage_content, search_webpage, read_pdf_content, search_pdf


class ToolService:
    """Service for managing tool operations for company agents"""
    
    def __init__(self):
        self.webpage_reader = WebpageReader()
        self.pdf_reader = PDFReader()
        self.upload_directory = "uploads"
        
        # Ensure upload directory exists
        os.makedirs(self.upload_directory, exist_ok=True)
    
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
    
    async def read_pdf(self, file_path: str, max_length: int = 50000) -> Dict[str, Any]:
        """
        Read content from a PDF file
        
        Args:
            file_path: Path to the PDF file
            max_length: Maximum length of extracted text
            
        Returns:
            Dictionary containing PDF content and metadata
        """
        try:
            result = await self.pdf_reader.read_pdf(file_path, max_length)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read PDF: {str(e)}")
    
    async def read_pdf_from_upload(self, file: UploadFile, max_length: int = 50000) -> Dict[str, Any]:
        """
        Read content from an uploaded PDF file
        
        Args:
            file: Uploaded PDF file
            max_length: Maximum length of extracted text
            
        Returns:
            Dictionary containing PDF content and metadata
        """
        try:
            # Validate file type
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="File must be a PDF")
            
            # Save uploaded file temporarily
            file_path = os.path.join(self.upload_directory, f"temp_{file.filename}")
            
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Read PDF content
            result = await self.pdf_reader.read_pdf(file_path, max_length)
            
            # Clean up temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            # Clean up temporary file on error
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Failed to read uploaded PDF: {str(e)}")
    
    async def search_pdf(self, file_path: str, search_terms: List[str], max_length: int = 10000) -> Dict[str, Any]:
        """
        Search for specific terms within a PDF
        
        Args:
            file_path: Path to the PDF file
            search_terms: List of terms to search for
            max_length: Maximum length of extracted text
            
        Returns:
            Dictionary containing search results
        """
        try:
            result = await self.pdf_reader.search_pdf_content(file_path, search_terms, max_length)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to search PDF: {str(e)}")
    
    async def extract_pdf_pages(self, file_path: str, page_numbers: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Extract specific pages from a PDF
        
        Args:
            file_path: Path to the PDF file
            page_numbers: List of page numbers to extract (1-indexed). If None, extracts all pages.
            
        Returns:
            Dictionary containing extracted pages
        """
        try:
            result = await self.pdf_reader.extract_pdf_pages(file_path, page_numbers)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to extract PDF pages: {str(e)}")
    
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
            file_path = request_data.get("file_path")
            if not file_path:
                raise HTTPException(status_code=400, detail="File path is required")
            
            action = request_data.get("action", "read")
            max_length = request_data.get("max_length", 50000)
            
            if action == "read":
                return await self.read_pdf(file_path, max_length)
            elif action == "search":
                search_terms = request_data.get("search_terms", [])
                if not search_terms:
                    raise HTTPException(status_code=400, detail="Search terms are required for search action")
                return await self.search_pdf(file_path, search_terms, max_length)
            elif action == "extract_pages":
                page_numbers = request_data.get("page_numbers")
                return await self.extract_pdf_pages(file_path, page_numbers)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
                
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
                "description": "Read and extract content from PDF files",
                "capabilities": [
                    "read_pdf",
                    "search_pdf_content",
                    "extract_specific_pages"
                ],
                "supported_formats": ["pdf"],
                "max_content_length": 50000
            }
        }
    
    async def close(self):
        """Close tool resources"""
        await self.webpage_reader.close()
