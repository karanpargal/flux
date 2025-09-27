from fastapi import APIRouter, Depends, HTTPException
from typing import List

from ..models.agent_models import (
    PDFProcessRequest,
    PDFProcessResponse,
    PDFSearchRequest,
    PDFSearchResponse,
    PDFDocumentsResponse,
    PDFDocumentInfo
)
from ..services.pdf_service import PDFService

router = APIRouter(prefix="/pdf", tags=["pdf-processing"])


def get_pdf_service() -> PDFService:
    """Dependency to get PDF service instance"""
    return PDFService()


@router.post("/process", response_model=PDFProcessResponse)
async def process_pdf(
    request: PDFProcessRequest,
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """Process a PDF document from URL and extract text content"""
    try:
        result = await pdf_service.process_pdf_from_url(
            url=request.url,
            max_length=request.max_length
        )

        print(result["content"])
        
        return PDFProcessResponse(
            success=True,
            document_id=result["document_id"],
            content=result["content"],
            metadata=result["metadata"],
            page_count=result["page_count"],
            content_length=result["content_length"],
            file_size=result["file_size"],
            url=result["url"]
        )
    except HTTPException:
        raise
    except Exception as e:
        return PDFProcessResponse(
            success=False,
            error=f"Failed to process PDF: {str(e)}"
        )


@router.get("/documents/{document_id}")
async def get_document_content(
    document_id: str,
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """Get processed document content by ID"""
    try:
        return await pdf_service.get_document_content(document_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")


@router.post("/search", response_model=PDFSearchResponse)
async def search_document_content(
    request: PDFSearchRequest,
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """Search for terms within a processed document"""
    try:
        result = await pdf_service.search_document_content(
            document_id=request.document_id,
            search_terms=request.search_terms
        )
        
        return PDFSearchResponse(
            success=True,
            document_id=result["document_id"],
            search_results=result["search_results"],
            total_terms_searched=result["total_terms_searched"],
            terms_found=result["terms_found"]
        )
    except HTTPException:
        raise
    except Exception as e:
        return PDFSearchResponse(
            success=False,
            document_id=request.document_id,
            error=f"Failed to search document: {str(e)}"
        )


@router.get("/documents", response_model=PDFDocumentsResponse)
async def list_processed_documents(
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """List all processed PDF documents"""
    try:
        result = pdf_service.get_processed_documents()
        
        documents = []
        for doc in result["documents"]:
            documents.append(PDFDocumentInfo(
                document_id=doc["document_id"],
                url=doc["url"],
                content_length=doc["content_length"],
                page_count=doc["page_count"],
                file_size=doc["file_size"],
                processed_at=doc.get("processed_at", ""),
                status=doc["status"]
            ))
        
        return PDFDocumentsResponse(
            total_documents=result["total_documents"],
            documents=documents
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """Delete a processed document"""
    try:
        return pdf_service.delete_document(document_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
