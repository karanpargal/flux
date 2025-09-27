import os
import asyncio
import math
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from ..tools import PDFReader, verify_transaction


class ToolService:
    """Service for managing tool operations for company agents"""
    
    def __init__(self):
        self.pdf_reader = PDFReader()
    
    async def calculate(self, expression: str) -> Dict[str, Any]:
        """
        Perform mathematical calculations
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            Dictionary containing calculation result
        """
        try:
            allowed_names = {
                k: v for k, v in math.__dict__.items() if not k.startswith("__")
            }
            allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
            
            if any(dangerous in expression for dangerous in ["import", "exec", "eval", "__", "open", "file"]):
                raise ValueError("Invalid expression: contains forbidden operations")
            
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            
            return {
                "success": True,
                "expression": expression,
                "result": result,
                "type": type(result).__name__
            }
        except Exception as e:
            return {
                "success": False,
                "expression": expression,
                "error": f"Calculation error: {str(e)}"
            }
    
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
    
    async def process_calculation_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a calculation request from an agent
        
        Args:
            request_data: Dictionary containing request parameters
            
        Returns:
            Dictionary containing calculation results
        """
        try:
            expression = request_data.get("expression")
            if not expression:
                raise HTTPException(status_code=400, detail="Expression is required")
            
            return await self.calculate(expression)
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process calculation request: {str(e)}")
    
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
    
    
    async def process_transaction_verification_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a transaction verification request from an agent
        
        Args:
            request_data: Dictionary containing transaction verification parameters
            
        Returns:
            Dictionary containing verification results
        """
        try:
            required_fields = ["tx_hash", "chain_name", "from_address", "to_address", 
                             "token_address", "amount"]
            
            for field in required_fields:
                if field not in request_data:
                    raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
            
            result = await verify_transaction(
                tx_hash=request_data["tx_hash"],
                chain_name=request_data["chain_name"],
                from_address=request_data["from_address"],
                to_address=request_data["to_address"],
                token_address=request_data["token_address"],
                amount=request_data["amount"],
                is_native=request_data.get("is_native", False)
            )
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process transaction verification request: {str(e)}")

    async def get_tool_capabilities(self) -> Dict[str, Any]:
        """
        Get information about available tools and their capabilities
        
        Returns:
            Dictionary containing tool capabilities
        """
        return {
            "calculator": {
                "description": "Perform mathematical calculations and evaluations",
                "capabilities": [
                    "calculate"
                ],
                "supported_operations": ["basic arithmetic", "trigonometry", "logarithms", "constants"],
                "safe_evaluation": True
            },
            "pdf_reader": {
                "description": "Read and extract content from PDF files via URL",
                "capabilities": [
                    "read_pdf_from_url"
                ],
                "supported_formats": ["pdf"],
                "max_content_length": 50000
            },
            "transaction_verifier": {
                "description": "Verify blockchain transactions against expected parameters",
                "capabilities": [
                    "verify_transaction"
                ],
                "supported_chains": ["eth-mainnet", "polygon-mainnet", "bsc-mainnet"],
                "verification_features": [
                    "transaction_status_check",
                    "amount_verification",
                    "address_verification",
                    "token_verification"
                ]
            },
            "refund_processor": {
                "description": "Process blockchain refunds with validation and execution",
                "capabilities": [
                    "process_refund_transaction",
                    "validate_refund_transaction",
                    "process_overpayment_refund_transaction"
                ],
                "supported_chains": ["ethereum", "polygon", "bsc"],
                "security_features": [
                    "private_key_encryption",
                    "transaction_verification",
                    "amount_validation"
                ],
                "note": "Refund processing is handled by individual agent instances with company-specific configuration"
            }
        }
    
    async def close(self):
        """Close tool resources"""
        pass  # No resources to close for current tools
