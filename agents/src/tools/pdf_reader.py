import os
import json
import asyncio
from typing import Any, Dict, List, Optional, Union
import aiofiles
from io import BytesIO
import re
import httpx


class PDFReader:
    """Tool for reading and extracting content from PDF files"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    
    async def read_pdf_from_bytes(self, pdf_bytes: bytes, max_length: int = 50000) -> Dict[str, Any]:
        """
        Read and extract content from PDF bytes
        
        Args:
            pdf_bytes: PDF file content as bytes
            max_length: Maximum length of extracted text
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        try:
            # Try to import PyPDF2 or pypdf
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
            except ImportError:
                try:
                    import pypdf
                    pdf_reader = pypdf.PdfReader(BytesIO(pdf_bytes))
                except ImportError:
                    return {
                        "success": False,
                        "error": "PDF library not available. Please install PyPDF2 or pypdf"
                    }
            
            # Extract text from all pages
            full_text = ""
            page_texts = []
            
            print(f"📄 Processing {len(pdf_reader.pages)} pages...")
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    print(f"📄 Page {page_num + 1}: {len(page_text)} characters")
                    if page_text:
                        page_texts.append({
                            "page_number": page_num + 1,
                            "text": page_text,
                            "length": len(page_text)
                        })
                        full_text += page_text + "\n"
                    else:
                        print(f"⚠️ Page {page_num + 1}: No text extracted")
                except Exception as e:
                    print(f"❌ Page {page_num + 1} extraction error: {str(e)}")
                    page_texts.append({
                        "page_number": page_num + 1,
                        "text": "",
                        "length": 0,
                        "error": str(e)
                    })
            
            # Clean and truncate text
            cleaned_text = self._clean_text(full_text)
            if len(cleaned_text) > max_length:
                cleaned_text = cleaned_text[:max_length] + "..."
            
            # Extract metadata
            metadata = self._extract_pdf_metadata(pdf_reader, "from_bytes")
            
            return {
                "success": True,
                "content": cleaned_text,
                "metadata": metadata,
                "page_count": len(pdf_reader.pages),
                "page_texts": page_texts,
                "content_length": len(cleaned_text),
                "total_pages_processed": len(page_texts)
            }
            
        except Exception as e:
            print(f"❌ PDF extraction error: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to read PDF from bytes: {str(e)}"
            }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text
    
    def _extract_pdf_metadata(self, pdf_reader, source: str) -> Dict[str, Any]:
        """Extract metadata from PDF"""
        metadata = {
            "source": source,
            "file_size": 0  # Will be set by caller for URL-based PDFs
        }
        
        try:
            # Try to get PDF metadata
            if hasattr(pdf_reader, 'metadata') and pdf_reader.metadata:
                pdf_metadata = pdf_reader.metadata
                if pdf_metadata:
                    metadata.update({
                        "title": str(pdf_metadata.get('/Title', '')),
                        "author": str(pdf_metadata.get('/Author', '')),
                        "subject": str(pdf_metadata.get('/Subject', '')),
                        "creator": str(pdf_metadata.get('/Creator', '')),
                        "producer": str(pdf_metadata.get('/Producer', '')),
                        "creation_date": str(pdf_metadata.get('/CreationDate', '')),
                        "modification_date": str(pdf_metadata.get('/ModDate', ''))
                    })
        except Exception:
            pass  # Metadata extraction is optional
        
        return metadata
    
    
    
    async def read_pdf_from_url(self, url: str, max_length: int = 50000) -> Dict[str, Any]:
        """
        Read and extract content from a PDF URL
        
        Args:
            url: URL to the PDF file
            max_length: Maximum length of extracted text
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        try:
            async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
                print(f"🔗 Fetching PDF from URL: {url}")
                response = await client.get(url)
                response.raise_for_status()
                
                print(f"📄 Response status: {response.status_code}")
                print(f"📄 Content-Type: {response.headers.get('content-type', 'unknown')}")
                print(f"📄 Content-Length: {len(response.content)} bytes")
                
                # Check if content type is PDF
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' not in content_type and not response.content.startswith(b'%PDF'):
                    return {
                        "success": False,
                        "error": f"URL does not point to a PDF file. Content-Type: {content_type}",
                        "url": url
                    }
                
                pdf_bytes = response.content
                
                # Use the existing read_pdf_from_bytes method
                result = await self.read_pdf_from_bytes(pdf_bytes, max_length)
                result["url"] = url
                result["file_size"] = len(pdf_bytes)
                
                # Update metadata with URL source
                if "metadata" in result:
                    result["metadata"]["source"] = url
                    result["metadata"]["file_size"] = len(pdf_bytes)
                
                print(f"✅ Successfully processed PDF: {len(result.get('content', ''))} characters extracted")
                return result
                
        except httpx.TimeoutException:
            print(f"⏰ Timeout while fetching PDF from {url}")
            return {
                "success": False,
                "error": "Request timeout while fetching PDF from URL",
                "url": url
            }
        except httpx.HTTPStatusError as e:
            print(f"🚫 HTTP error {e.response.status_code} while fetching PDF from {url}")
            return {
                "success": False,
                "error": f"HTTP error {e.response.status_code} while fetching PDF from URL",
                "url": url
            }
        except Exception as e:
            print(f"❌ Error fetching PDF from {url}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to fetch PDF from URL: {str(e)}",
                "url": url
            }


# Standalone functions for easy integration
async def read_pdf_from_url(url: str, max_length: int = 50000) -> Dict[str, Any]:
    """Simple function to read PDF content from URL"""
    reader = PDFReader()
    result = await reader.read_pdf_from_url(url, max_length)
    return result
