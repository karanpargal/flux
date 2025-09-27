import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
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
    
    async def process_multiple_pdfs(self, urls: List[str], max_length_per_pdf: int = 20000) -> Dict[str, Any]:
        """
        Process multiple PDFs and combine their content for better context
        
        Args:
            urls: List of PDF URLs to process
            max_length_per_pdf: Maximum length per PDF
            
        Returns:
            Dictionary containing combined processing results
        """
        try:
            print(f"🔄 Processing {len(urls)} PDFs for combined context")
            combined_content = ""
            processed_docs = []
            total_pages = 0
            total_size = 0
            
            for i, url in enumerate(urls):
                try:
                    print(f"📄 Processing PDF {i+1}/{len(urls)}: {url}")
                    result = await self.process_pdf_from_url(url, max_length_per_pdf)
                    
                    if result.get("success"):
                        content = result.get("content", "")
                        if content:
                            # Add document separator and metadata
                            doc_header = f"\n\n--- DOCUMENT {i+1}: {url} ---\n"
                            doc_footer = f"\n--- END DOCUMENT {i+1} ---\n"
                            combined_content += doc_header + content + doc_footer
                            
                            processed_docs.append({
                                "url": url,
                                "content_length": len(content),
                                "page_count": result.get("page_count", 0),
                                "file_size": result.get("file_size", 0)
                            })
                            
                            total_pages += result.get("page_count", 0)
                            total_size += result.get("file_size", 0)
                        else:
                            print(f"⚠️ No content extracted from {url}")
                    else:
                        print(f"❌ Failed to process {url}: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"❌ Error processing {url}: {str(e)}")
                    continue
            
            if not combined_content.strip():
                return {
                    "success": False,
                    "error": "No content could be extracted from any of the provided PDFs",
                    "processed_docs": processed_docs
                }
            
            # Create a combined document entry
            combined_doc_id = str(uuid.uuid4())
            self.processed_documents[combined_doc_id] = {
                "document_id": combined_doc_id,
                "url": f"combined_{len(urls)}_documents",
                "content": combined_content,
                "metadata": {
                    "source_urls": urls,
                    "processed_docs": processed_docs,
                    "total_pages": total_pages,
                    "total_size": total_size,
                    "processed_at": datetime.now().isoformat()
                },
                "page_count": total_pages,
                "content_length": len(combined_content),
                "file_size": total_size,
                "processed_at": datetime.now().isoformat(),
                "status": "processed"
            }
            
            print(f"✅ Successfully processed {len(processed_docs)}/{len(urls)} PDFs")
            print(f"📊 Combined content length: {len(combined_content)} characters")
            
            return {
                "success": True,
                "document_id": combined_doc_id,
                "content": combined_content,
                "metadata": {
                    "source_urls": urls,
                    "processed_docs": processed_docs,
                    "total_pages": total_pages,
                    "total_size": total_size,
                    "processed_at": datetime.now().isoformat()
                },
                "page_count": total_pages,
                "content_length": len(combined_content),
                "file_size": total_size,
                "processed_docs_count": len(processed_docs),
                "total_docs_attempted": len(urls)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to process multiple PDFs: {str(e)}"
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
