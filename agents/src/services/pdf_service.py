import os
import uuid
from typing import Dict, Any, Optional
from fastapi import HTTPException
from ..tools.pdf_reader import PDFReader, read_pdf_from_url
from ..config import get_settings


class PDFService:
    """Service for processing PDF documents"""
    
    def __init__(self):
        self.pdf_reader = PDFReader()
        self.settings = get_settings()
        self.processed_documents: Dict[str, Dict[str, Any]] = {}
    
    async def process_pdf_from_url(self, url: str, max_length: int = 50000) -> Dict[str, Any]:
        """
        Process a PDF from URL and extract text content
        
        Args:
            url: URL to the PDF file
            max_length: Maximum length of extracted text
            
        Returns:
            Dictionary containing processing results
        """
        try:
            print(f"🔄 Processing PDF from URL: {url}")
            result = await self.pdf_reader.read_pdf_from_url(url, max_length)
            
            if not result.get("success"):
                error_msg = result.get('error', 'Unknown error')
                print(f"❌ PDF processing failed: {error_msg}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to process PDF: {error_msg}"
                )
            
            document_id = str(uuid.uuid4())
            
            self.processed_documents[document_id] = {
                "document_id": document_id,
                "url": url,
                "content": result.get("content", ""),
                "metadata": result.get("metadata", {}),
                "page_count": result.get("page_count", 0),
                "content_length": result.get("content_length", 0),
                "file_size": result.get("file_size", 0),
                "processed_at": result.get("metadata", {}).get("processed_at", ""),
                "status": "processed"
            }
            
            return {
                "success": True,
                "document_id": document_id,
                "content": result.get("content", ""),
                "metadata": result.get("metadata", {}),
                "page_count": result.get("page_count", 0),
                "content_length": result.get("content_length", 0),
                "file_size": result.get("file_size", 0),
                "url": url
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to process PDF from URL: {str(e)}"
            )
    
    async def get_document_content(self, document_id: str) -> Dict[str, Any]:
        """
        Get processed document content by ID
        
        Args:
            document_id: ID of the processed document
            
        Returns:
            Dictionary containing document content
        """
        if document_id not in self.processed_documents:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return self.processed_documents[document_id]
    
    async def search_document_content(self, document_id: str, search_terms: list) -> Dict[str, Any]:
        """
        Search for terms within a processed document
        
        Args:
            document_id: ID of the processed document
            search_terms: List of terms to search for
            
        Returns:
            Dictionary containing search results
        """
        if document_id not in self.processed_documents:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document = self.processed_documents[document_id]
        content = document.get("content", "").lower()
        search_results = {}
        
        for term in search_terms:
            term_lower = term.lower()
            if term_lower in content:
                # Find context around the term
                start_idx = content.find(term_lower)
                context_start = max(0, start_idx - 300)
                context_end = min(len(content), start_idx + len(term) + 300)
                context = document.get("content", "")[context_start:context_end]
                
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
            "document_id": document_id,
            "search_results": search_results,
            "total_terms_searched": len(search_terms),
            "terms_found": sum(1 for result in search_results.values() if result["found"])
        }
    
    def get_processed_documents(self) -> Dict[str, Any]:
        """Get all processed documents"""
        return {
            "total_documents": len(self.processed_documents),
            "documents": list(self.processed_documents.values())
        }
    
    def delete_document(self, document_id: str) -> Dict[str, str]:
        """Delete a processed document"""
        if document_id not in self.processed_documents:
            raise HTTPException(status_code=404, detail="Document not found")
        
        del self.processed_documents[document_id]
        return {"message": f"Document {document_id} deleted successfully"}
