import os
import json
import asyncio
from typing import Any, Dict, Optional
import httpx
from bs4 import BeautifulSoup
import aiofiles
from urllib.parse import urlparse, urljoin
import re


class WebpageReader:
    """Tool for reading and extracting content from web pages"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
    
    async def read_webpage(self, url: str, max_length: int = 10000) -> Dict[str, Any]:
        """
        Read and extract content from a webpage
        
        Args:
            url: The URL to read
            max_length: Maximum length of extracted text
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {
                    "success": False,
                    "error": "Invalid URL format",
                    "url": url
                }
            
            # Fetch the webpage
            response = await self.client.get(url)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No title found"
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract main content
            content = self._extract_main_content(soup)
            
            # Clean and truncate content
            cleaned_content = self._clean_text(content)
            if len(cleaned_content) > max_length:
                cleaned_content = cleaned_content[:max_length] + "..."
            
            # Extract metadata
            metadata = self._extract_metadata(soup, url)
            
            return {
                "success": True,
                "url": url,
                "title": title_text,
                "content": cleaned_content,
                "metadata": metadata,
                "content_length": len(cleaned_content),
                "status_code": response.status_code
            }
            
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request timeout - the webpage took too long to load",
                "url": url
            }
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP error {e.response.status_code}: {e.response.reason_phrase}",
                "url": url
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read webpage: {str(e)}",
                "url": url
            }
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from the webpage"""
        # Try to find main content areas
        main_selectors = [
            'main',
            'article',
            '[role="main"]',
            '.content',
            '.main-content',
            '.post-content',
            '.entry-content'
        ]
        
        for selector in main_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                return main_content.get_text()
        
        # Fallback to body content
        body = soup.find('body')
        if body:
            return body.get_text()
        
        return soup.get_text()
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract metadata from the webpage"""
        metadata = {
            "url": url,
            "domain": urlparse(url).netloc
        }
        
        # Extract meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                metadata[name] = content
        
        # Extract links
        links = soup.find_all('a', href=True)
        metadata["link_count"] = len(links)
        
        # Extract images
        images = soup.find_all('img')
        metadata["image_count"] = len(images)
        
        return metadata
    
    async def search_webpage_content(self, url: str, search_terms: list, max_length: int = 5000) -> Dict[str, Any]:
        """
        Search for specific terms within a webpage
        
        Args:
            url: The URL to search
            search_terms: List of terms to search for
            max_length: Maximum length of extracted text
            
        Returns:
            Dictionary containing search results and context
        """
        try:
            # Read the webpage first
            webpage_result = await self.read_webpage(url, max_length)
            
            if not webpage_result["success"]:
                return webpage_result
            
            content = webpage_result["content"].lower()
            search_results = {}
            
            for term in search_terms:
                term_lower = term.lower()
                if term_lower in content:
                    # Find context around the term
                    start_idx = content.find(term_lower)
                    context_start = max(0, start_idx - 200)
                    context_end = min(len(content), start_idx + len(term) + 200)
                    context = webpage_result["content"][context_start:context_end]
                    
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
                "url": url,
                "title": webpage_result["title"],
                "search_results": search_results,
                "total_terms_searched": len(search_terms),
                "terms_found": sum(1 for result in search_results.values() if result["found"])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to search webpage: {str(e)}",
                "url": url
            }
    
    async def extract_links(self, url: str, filter_domain: bool = True) -> Dict[str, Any]:
        """
        Extract all links from a webpage
        
        Args:
            url: The URL to extract links from
            filter_domain: Whether to filter links to the same domain
            
        Returns:
            Dictionary containing extracted links
        """
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            base_domain = urlparse(url).netloc
            
            links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text().strip()
                
                # Convert relative URLs to absolute
                absolute_url = urljoin(url, href)
                parsed_href = urlparse(absolute_url)
                
                # Filter by domain if requested
                if filter_domain and parsed_href.netloc != base_domain:
                    continue
                
                links.append({
                    "url": absolute_url,
                    "text": text,
                    "domain": parsed_href.netloc
                })
            
            return {
                "success": True,
                "url": url,
                "links": links,
                "total_links": len(links),
                "filtered_by_domain": filter_domain
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to extract links: {str(e)}",
                "url": url
            }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Standalone functions for easy integration
async def read_webpage_content(url: str, max_length: int = 10000) -> str:
    """Simple function to read webpage content"""
    reader = WebpageReader()
    try:
        result = await reader.read_webpage(url, max_length)
        await reader.close()
        return result.get("content", "") if result.get("success") else f"Error: {result.get('error', 'Unknown error')}"
    except Exception as e:
        await reader.close()
        return f"Error reading webpage: {str(e)}"


async def search_webpage(url: str, search_terms: list) -> Dict[str, Any]:
    """Simple function to search webpage content"""
    reader = WebpageReader()
    try:
        result = await reader.search_webpage_content(url, search_terms)
        await reader.close()
        return result
    except Exception as e:
        await reader.close()
        return {"success": False, "error": str(e)}
