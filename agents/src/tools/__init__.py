"""
Tools package for company agents
"""

from .webpage_reader import WebpageReader, read_webpage_content, search_webpage
from .pdf_reader import PDFReader, read_pdf_content, search_pdf, extract_pdf_pages

__all__ = [
    'WebpageReader',
    'read_webpage_content', 
    'search_webpage',
    'PDFReader',
    'read_pdf_content',
    'search_pdf',
    'extract_pdf_pages'
]
