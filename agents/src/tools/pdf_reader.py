import os
import json
import asyncio
from typing import Any, Dict, List, Optional, Union
import aiofiles
from io import BytesIO
import re


class PDFReader:
    """Tool for reading and extracting content from PDF files"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    async def read_pdf(self, file_path: str, max_length: int = 50000) -> Dict[str, Any]:
        """
        Read and extract content from a PDF file
        
        Args:
            file_path: Path to the PDF file
            max_length: Maximum length of extracted text
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "file_path": file_path
                }
            
            # Check file extension
            if not file_path.lower().endswith('.pdf'):
                return {
                    "success": False,
                    "error": "File is not a PDF",
                    "file_path": file_path
                }
            
            # Try to import PyPDF2 or pypdf
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(file_path)
            except ImportError:
                try:
                    import pypdf
                    pdf_reader = pypdf.PdfReader(file_path)
                except ImportError:
                    return {
                        "success": False,
                        "error": "PDF library not available. Please install PyPDF2 or pypdf",
                        "file_path": file_path
                    }
            
            # Extract text from all pages
            full_text = ""
            page_texts = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        page_texts.append({
                            "page_number": page_num + 1,
                            "text": page_text,
                            "length": len(page_text)
                        })
                        full_text += page_text + "\n"
                except Exception as e:
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
            metadata = self._extract_pdf_metadata(pdf_reader, file_path)
            
            return {
                "success": True,
                "file_path": file_path,
                "content": cleaned_text,
                "metadata": metadata,
                "page_count": len(pdf_reader.pages),
                "page_texts": page_texts,
                "content_length": len(cleaned_text),
                "total_pages_processed": len(page_texts)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read PDF: {str(e)}",
                "file_path": file_path
            }
    
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
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        page_texts.append({
                            "page_number": page_num + 1,
                            "text": page_text,
                            "length": len(page_text)
                        })
                        full_text += page_text + "\n"
                except Exception as e:
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
    
    def _extract_pdf_metadata(self, pdf_reader, file_path: str) -> Dict[str, Any]:
        """Extract metadata from PDF"""
        metadata = {
            "file_path": file_path,
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
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
    
    async def search_pdf_content(self, file_path: str, search_terms: List[str], max_length: int = 10000) -> Dict[str, Any]:
        """
        Search for specific terms within a PDF
        
        Args:
            file_path: Path to the PDF file
            search_terms: List of terms to search for
            max_length: Maximum length of extracted text
            
        Returns:
            Dictionary containing search results and context
        """
        try:
            # Read the PDF first
            pdf_result = await self.read_pdf(file_path, max_length)
            
            if not pdf_result["success"]:
                return pdf_result
            
            content = pdf_result["content"].lower()
            search_results = {}
            
            for term in search_terms:
                term_lower = term.lower()
                if term_lower in content:
                    # Find context around the term
                    start_idx = content.find(term_lower)
                    context_start = max(0, start_idx - 300)
                    context_end = min(len(content), start_idx + len(term) + 300)
                    context = pdf_result["content"][context_start:context_end]
                    
                    search_results[term] = {
                        "found": True,
                        "context": context.strip(),
                        "position": start_idx
                    }
                else:
                    search_results[term] = {
                        "found": False,
                        "context": None,
                        "position": -1
                    }
            
            return {
                "success": True,
                "file_path": file_path,
                "search_results": search_results,
                "total_terms_searched": len(search_terms),
                "terms_found": sum(1 for result in search_results.values() if result["found"]),
                "page_count": pdf_result.get("page_count", 0)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to search PDF: {str(e)}",
                "file_path": file_path
            }
    
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
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "file_path": file_path
                }
            
            # Try to import PyPDF2 or pypdf
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(file_path)
            except ImportError:
                try:
                    import pypdf
                    pdf_reader = pypdf.PdfReader(file_path)
                except ImportError:
                    return {
                        "success": False,
                        "error": "PDF library not available. Please install PyPDF2 or pypdf",
                        "file_path": file_path
                    }
            
            total_pages = len(pdf_reader.pages)
            
            # If no specific pages requested, extract all
            if page_numbers is None:
                page_numbers = list(range(1, total_pages + 1))
            
            # Validate page numbers
            valid_pages = [p for p in page_numbers if 1 <= p <= total_pages]
            invalid_pages = [p for p in page_numbers if p < 1 or p > total_pages]
            
            extracted_pages = []
            
            for page_num in valid_pages:
                try:
                    page = pdf_reader.pages[page_num - 1]  # Convert to 0-indexed
                    page_text = page.extract_text()
                    
                    extracted_pages.append({
                        "page_number": page_num,
                        "text": page_text,
                        "length": len(page_text)
                    })
                except Exception as e:
                    extracted_pages.append({
                        "page_number": page_num,
                        "text": "",
                        "length": 0,
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "file_path": file_path,
                "extracted_pages": extracted_pages,
                "total_pages_in_pdf": total_pages,
                "pages_requested": len(page_numbers),
                "pages_extracted": len(extracted_pages),
                "invalid_pages": invalid_pages
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to extract PDF pages: {str(e)}",
                "file_path": file_path
            }


# Standalone functions for easy integration
async def read_pdf_content(file_path: str, max_length: int = 50000) -> str:
    """Simple function to read PDF content"""
    reader = PDFReader()
    result = await reader.read_pdf(file_path, max_length)
    return result.get("content", "") if result.get("success") else f"Error: {result.get('error', 'Unknown error')}"


async def search_pdf(file_path: str, search_terms: List[str]) -> Dict[str, Any]:
    """Simple function to search PDF content"""
    reader = PDFReader()
    result = await reader.search_pdf_content(file_path, search_terms)
    return result


async def extract_pdf_pages(file_path: str, page_numbers: Optional[List[int]] = None) -> Dict[str, Any]:
    """Simple function to extract specific PDF pages"""
    reader = PDFReader()
    result = await reader.extract_pdf_pages(file_path, page_numbers)
    return result
