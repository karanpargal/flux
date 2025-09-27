"""
Capability Service for managing agent capabilities and tool injection
"""

from typing import Dict, List, Any, Optional
from enum import Enum


class CapabilityType(Enum):
    """Available capability types for agents"""
    DOCUMENT_REFERENCE = "document_reference"
    TRANSACTION_VERIFICATION = "transaction_verification"
    CALCULATOR = "calculator"
    REFUND_PROCESSING = "refund_processing"
    CUSTOMER_SUPPORT = "customer_support"
    PRODUCT_INFORMATION = "product_information"
    TECHNICAL_SUPPORT = "technical_support"
    BILLING_SUPPORT = "billing_support"
    GENERAL_INQUIRIES = "general_inquiries"


class CapabilityService:
    """Service for managing agent capabilities and tool injection"""
    
    def __init__(self):
        self.capability_tools_mapping = self._initialize_capability_mapping()
        self.capability_descriptions = self._initialize_capability_descriptions()
    
    def _initialize_capability_mapping(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize the mapping between capabilities and their required tools"""
        return {
            CapabilityType.DOCUMENT_REFERENCE.value: [
                {
                    "type": "function",
                    "function": {
                        "name": "search_company_documents",
                        "description": "Search through company PDF documents for specific information about products, policies, or procedures",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "search_terms": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of terms to search for in company documents"
                                },
                                "document_urls": {
                                    "type": "array", 
                                    "items": {"type": "string"},
                                    "description": "Specific document URLs to search in (optional)"
                                }
                            },
                            "required": ["search_terms"],
                            "additionalProperties": False
                        },
                        "strict": True
                    }
                }
            ],
            CapabilityType.TRANSACTION_VERIFICATION.value: [
                {
                    "type": "function",
                    "function": {
                        "name": "verify_transaction",
                        "description": "Verify if a blockchain transaction matches the expected parameters for payment verification",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "tx_hash": {
                                    "type": "string",
                                    "description": "The transaction hash to verify"
                                },
                                "chain_name": {
                                    "type": "string",
                                    "description": "The blockchain name (e.g., 'eth-mainnet', 'polygon-mainnet')"
                                },
                                "from_address": {
                                    "type": "string",
                                    "description": "The expected sender address"
                                },
                                "to_address": {
                                    "type": "string", 
                                    "description": "The expected receiver address (for native) or recipient (for ERC-20)"
                                },
                                "token_address": {
                                    "type": "string",
                                    "description": "The token contract address. Use 'native' for native blockchain token"
                                },
                                "amount": {
                                    "type": "string",
                                    "description": "The expected amount (in wei for native, token units for ERC-20)"
                                },
                                "is_native": {
                                    "type": "boolean",
                                    "description": "Whether this is a native token transfer (true) or ERC-20 transfer (false)",
                                    "default": False
                                }
                            },
                            "required": ["tx_hash", "chain_name", "from_address", "to_address", "token_address", "amount", "is_native"],
                            "additionalProperties": False
                        },
                        "strict": True
                    }
                }
            ],
            CapabilityType.CALCULATOR.value: [
                {
                    "type": "function",
                    "function": {
                        "name": "calculate",
                        "description": "Perform mathematical calculations and evaluations safely",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "expression": {
                                    "type": "string",
                                    "description": "Mathematical expression to evaluate (supports basic arithmetic, trigonometry, logarithms, and mathematical constants)"
                                }
                            },
                            "required": ["expression"],
                            "additionalProperties": False
                        },
                        "strict": True
                    }
                }
            ],
            CapabilityType.REFUND_PROCESSING.value: [
                {
                    "type": "function",
                    "function": {
                        "name": "process_refund",
                        "description": "Process a refund transaction to a user's wallet address",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_address": {
                                    "type": "string",
                                    "description": "The user's wallet address to send the refund to"
                                },
                                "transaction_hash": {
                                    "type": "string",
                                    "description": "The original transaction hash to verify"
                                },
                                "requested_amount": {
                                    "type": "string",
                                    "description": "The amount to refund (in wei)"
                                },
                                "agent_private_key": {
                                    "type": "string",
                                    "description": "The encrypted private key for the agent's wallet"
                                },
                                "refund_chain": {
                                    "type": "string",
                                    "description": "The blockchain network for the refund (ethereum, polygon, bsc)",
                                    "enum": ["ethereum", "polygon", "bsc"]
                                },
                                "max_refund_amount": {
                                    "type": "string",
                                    "description": "Maximum refund amount allowed (in wei) - overrides company default"
                                },
                                "reason": {
                                    "type": "string",
                                    "description": "Reason for the refund"
                                }
                            },
                            "required": ["user_address", "transaction_hash", "requested_amount", "agent_private_key", "refund_chain"],
                            "additionalProperties": False
                        },
                        "strict": True
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "validate_refund_request",
                        "description": "Validate a refund request without processing the transaction",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_address": {
                                    "type": "string",
                                    "description": "The user's wallet address requesting the refund"
                                },
                                "transaction_hash": {
                                    "type": "string",
                                    "description": "The original transaction hash to verify"
                                },
                                "requested_amount": {
                                    "type": "string",
                                    "description": "The amount requested for refund (in wei)"
                                },
                                "refund_chain": {
                                    "type": "string",
                                    "description": "The blockchain network for the refund (ethereum, polygon, bsc)",
                                    "enum": ["ethereum", "polygon", "bsc"]
                                },
                                "max_refund_amount": {
                                    "type": "string",
                                    "description": "Maximum refund amount allowed (in wei) - overrides company default"
                                }
                            },
                            "required": ["user_address", "transaction_hash", "requested_amount", "refund_chain"],
                            "additionalProperties": False
                        },
                        "strict": True
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "process_overpayment_refund",
                        "description": "Process a refund for overpayment scenarios where user paid more than the expected amount",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_address": {
                                    "type": "string",
                                    "description": "The user's wallet address to send the refund to"
                                },
                                "transaction_hash": {
                                    "type": "string",
                                    "description": "The original transaction hash to verify"
                                },
                                "expected_amount": {
                                    "type": "string",
                                    "description": "The expected/correct amount that should have been paid (in wei)"
                                },
                                "agent_private_key": {
                                    "type": "string",
                                    "description": "The encrypted private key for the agent's wallet"
                                },
                                "refund_chain": {
                                    "type": "string",
                                    "description": "The blockchain network for the refund (ethereum, polygon, bsc)",
                                    "enum": ["ethereum", "polygon", "bsc"]
                                },
                                "max_refund_amount": {
                                    "type": "string",
                                    "description": "Maximum refund amount allowed (in wei) - overrides company default"
                                },
                                "reason": {
                                    "type": "string",
                                    "description": "Reason for the refund"
                                }
                            },
                            "required": ["user_address", "transaction_hash", "expected_amount", "agent_private_key", "refund_chain"],
                            "additionalProperties": False
                        },
                        "strict": True
                    }
                }
            ],
            CapabilityType.CUSTOMER_SUPPORT.value: [],
            CapabilityType.PRODUCT_INFORMATION.value: [],
            CapabilityType.TECHNICAL_SUPPORT.value: [],
            CapabilityType.BILLING_SUPPORT.value: [],
            CapabilityType.GENERAL_INQUIRIES.value: []
        }
    
    def _initialize_capability_descriptions(self) -> Dict[str, str]:
        """Initialize descriptions for each capability"""
        return {
            CapabilityType.DOCUMENT_REFERENCE.value: "Search and reference company documents, PDFs, and knowledge base",
            CapabilityType.TRANSACTION_VERIFICATION.value: "Verify blockchain transactions and payment confirmations",
            CapabilityType.CALCULATOR.value: "Perform mathematical calculations and evaluations",
            CapabilityType.REFUND_PROCESSING.value: "Process refunds and validate refund requests with company-specific limits",
            CapabilityType.CUSTOMER_SUPPORT.value: "Provide customer support and assistance",
            CapabilityType.PRODUCT_INFORMATION.value: "Provide information about company products and services",
            CapabilityType.TECHNICAL_SUPPORT.value: "Provide technical support and troubleshooting",
            CapabilityType.BILLING_SUPPORT.value: "Handle billing inquiries and payment questions",
            CapabilityType.GENERAL_INQUIRIES.value: "Handle general questions and inquiries"
        }
    
    def get_available_capabilities(self) -> List[str]:
        """Get list of all available capabilities"""
        return [cap.value for cap in CapabilityType]
    
    def get_capability_description(self, capability: str) -> Optional[str]:
        """Get description for a specific capability"""
        return self.capability_descriptions.get(capability)
    
    def get_tools_for_capabilities(self, capabilities: List[str]) -> List[Dict[str, Any]]:
        """Get all tools required for the specified capabilities"""
        tools = []
        for capability in capabilities:
            if capability in self.capability_tools_mapping:
                tools.extend(self.capability_tools_mapping[capability])
        return tools
    
    def get_capability_tools_mapping(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get the complete capability to tools mapping"""
        return self.capability_tools_mapping
    
    def validate_capabilities(self, capabilities: List[str]) -> Dict[str, Any]:
        """Validate if the provided capabilities are supported"""
        available_capabilities = self.get_available_capabilities()
        invalid_capabilities = [cap for cap in capabilities if cap not in available_capabilities]
        
        return {
            "valid": len(invalid_capabilities) == 0,
            "invalid_capabilities": invalid_capabilities,
            "available_capabilities": available_capabilities
        }
    
    def get_system_prompt_for_capabilities(self, capabilities: List[str], company_name: str, 
                                         support_categories: List[str] = None, 
                                         company_products: List[str] = None) -> str:
        """Generate system prompt based on selected capabilities"""
        capability_descriptions = []
        for capability in capabilities:
            desc = self.get_capability_description(capability)
            if desc:
                capability_descriptions.append(f"- {desc}")
        
        tools_description = []
        tools = self.get_tools_for_capabilities(capabilities)
        for tool in tools:
            tools_description.append(f"- {tool['function']['name']}: {tool['function']['description']}")
        
        support_categories_str = ', '.join(support_categories) if support_categories else "general, technical, billing"
        company_products_str = ', '.join(company_products) if company_products else "products and services"
        
        system_prompt = f"""You are an expert AI support agent for {company_name}, specializing in crypto payment solutions and blockchain integration.

EXPERTISE AREAS:
- Advanced crypto payment gateway integration
- Blockchain transaction processing and verification
- Multi-chain payment solutions (Ethereum, Polygon, BSC)
- API integration and webhook management
- Payment link generation and management
- Recurring payment subscriptions
- Invoice creation and management
- Refund processing and dispute resolution
- Security best practices for crypto payments

CAPABILITIES:
{chr(10).join(capability_descriptions)}

AVAILABLE TOOLS:
{chr(10).join(tools_description)}

COMPANY PRODUCTS/SERVICES: {company_products_str}
SUPPORT CATEGORIES: {support_categories_str}

ROBUST OPERATIONAL PROTOCOL:
1. AUTOMATIC INFORMATION GATHERING: For ANY question about {company_name}, immediately search company documents and web resources using multiple search strategies:
   - Use search_company_documents with comprehensive search terms: ["integration", "API", "payment", "crypto", "setup", "configuration", "webhook", "authentication", "endpoints", "SDK", "documentation"]
   - Use calculate for mathematical calculations and conversions when needed

2. COMPREHENSIVE RESPONSE STRATEGY:
   - Provide detailed, technical answers with code examples when relevant
   - Include step-by-step integration guides
   - Reference specific API endpoints, parameters, and authentication methods
   - Offer multiple implementation approaches (SDK, REST API, webhooks)
   - Include troubleshooting steps and common issues

3. TECHNICAL DEPTH:
   - Explain blockchain concepts clearly
   - Provide code snippets for popular frameworks (React, Node.js, Python, etc.)
   - Include security considerations and best practices
   - Reference official documentation and examples
   - Offer testing and debugging guidance

4. PROACTIVE SUPPORT:
   - Anticipate follow-up questions and provide comprehensive answers
   - Suggest related features and integrations
   - Offer optimization recommendations
   - Provide migration guides when applicable

5. ESCALATION PROTOCOL:
   - For complex technical issues, provide detailed analysis and multiple solution paths
   - For security concerns, emphasize verification steps and best practices
   - For integration challenges, offer debugging steps and alternative approaches

Always maintain technical accuracy, provide actionable solutions, and ensure users have everything needed for successful implementation."""

        return system_prompt
    
    def get_tool_imports_for_capabilities(self, capabilities: List[str]) -> List[str]:
        """Get the required imports for tools based on capabilities"""
        imports = []
        
        if CapabilityType.DOCUMENT_REFERENCE.value in capabilities:
            imports.append("from tools.pdf_reader import PDFReader")
        
        if CapabilityType.TRANSACTION_VERIFICATION.value in capabilities:
            imports.append("from tools.transaction_verifier import verify_transaction, get_transaction_verification_schema")
        
        if CapabilityType.CALCULATOR.value in capabilities:
            imports.append("import math")
        
        if CapabilityType.REFUND_PROCESSING.value in capabilities:
            imports.append("from tools.refund_processor import create_refund_processor, process_refund, validate_refund_request, process_overpayment_refund")
        
        return imports
    
    def get_tool_functions_for_capabilities(self, capabilities: List[str], pdf_document_urls: List[str] = None) -> str:
        """Generate tool function implementations based on capabilities"""
        functions = []
        
        if CapabilityType.DOCUMENT_REFERENCE.value in capabilities:
            functions.append(self._get_document_search_function(pdf_document_urls))
        
        if CapabilityType.TRANSACTION_VERIFICATION.value in capabilities:
            functions.append(self._get_transaction_verification_function())
        
        if CapabilityType.CALCULATOR.value in capabilities:
            functions.append(self._get_calculator_functions())
        
        if CapabilityType.REFUND_PROCESSING.value in capabilities:
            functions.append(self._get_refund_processing_functions())
        
        return "\n\n".join(functions)
    
    def _get_document_search_function(self, pdf_document_urls: List[str] = None) -> str:
        """Generate robust document search function"""
        default_urls = pdf_document_urls or []
        return f'''async def search_company_documents(search_terms: List[str], document_urls: List[str] = None) -> str:
    """Comprehensive search through company documents with advanced matching"""
    print(f"🔍 Advanced document search with terms: {{search_terms}}, urls: {{document_urls}}")
    try:
        from tools.pdf_reader import PDFReader
        import re
        
        # Initialize readers
        pdf_reader = PDFReader()
        
        # Enhanced search terms with variations
        enhanced_terms = []
        for term in search_terms:
            enhanced_terms.append(term.lower())
            enhanced_terms.append(term.upper())
            enhanced_terms.append(term.title())
            # Add common variations
            if "api" in term.lower():
                enhanced_terms.extend(["API", "api", "Api", "REST", "rest"])
            if "payment" in term.lower():
                enhanced_terms.extend(["Payment", "payments", "transaction", "transactions"])
            if "crypto" in term.lower():
                enhanced_terms.extend(["cryptocurrency", "blockchain", "crypto", "digital currency"])
        
        search_results = []
        urls_to_search = document_urls if document_urls else default_urls
        
        for url in urls_to_search:
            try:
                print(f"📄 Processing document: {{url}}")
                
                # Only process PDF files now
                if url.lower().endswith('.pdf') or 'pdf' in url.lower():
                    result = await pdf_reader.read_pdf_from_url(url, max_length=15000)
                else:
                    # Skip non-PDF files
                    print(f"⚠️ Skipping non-PDF document: {{url}}")
                    continue
                
                if result.get("success") and result.get("content"):
                    content = result.get("content", "")
                    content_lower = content.lower()
                    
                    # Advanced term matching with context
                    found_terms_with_context = []
                    for term in enhanced_terms:
                        if term.lower() in content_lower:
                            # Find context around the term
                            start_idx = content_lower.find(term.lower())
                            if start_idx != -1:
                                context_start = max(0, start_idx - 100)
                                context_end = min(len(content), start_idx + len(term) + 100)
                                context = content[context_start:context_end].strip()
                                found_terms_with_context.append(f"'{{term}}': {{context}}")
                    
                    if found_terms_with_context:
                        doc_type = "PDF"
                        search_results.append(f"📋 {{doc_type}} Document ({{url}}):\\n" + "\\n".join(found_terms_with_context))
                        
            except Exception as e:
                search_results.append(f"❌ Error processing {{url}}: {{str(e)}}")
        
        if search_results:
            return f"📚 COMPREHENSIVE SEARCH RESULTS:\\n\\n" + "\\n\\n".join(search_results)
        else:
            return f"🔍 No relevant information found for terms: {{', '.join(search_terms)}}\\n\\nSearched {{len(urls_to_search)}} documents."
            
    except Exception as e:
        return f"❌ Error in document search: {{str(e)}}"'''
    
    def _get_transaction_verification_function(self) -> str:
        """Generate transaction verification function"""
        return '''async def verify_payment_transaction(tx_hash: str, chain_name: str, from_address: str, to_address: str, token_address: str, amount: str, is_native: bool = False) -> str:
    """Verify a blockchain payment transaction"""
    try:
        result = await verify_transaction(tx_hash, chain_name, from_address, to_address, token_address, amount, is_native)
        if result.get("verified"):
            return f"✅ Transaction verified successfully! All parameters match."
        else:
            mismatches = result.get("mismatches", [])
            return f"❌ Transaction verification failed. Mismatches: {json.dumps(mismatches, indent=2)}"
    except Exception as e:
        return f"Error verifying transaction: {str(e)}"'''
    
    def _get_calculator_functions(self) -> str:
        """Generate calculator functions"""
        return '''async def calculate(expression: str) -> str:
    """Perform mathematical calculations and evaluations safely"""
    try:
        import math
        
        # Safe evaluation of mathematical expressions
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
        
        # Remove any potentially dangerous operations
        if any(dangerous in expression for dangerous in ["import", "exec", "eval", "__", "open", "file"]):
            return f"❌ Invalid expression: contains forbidden operations"
        
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        
        return f"🧮 CALCULATION RESULT:\\n\\nExpression: {expression}\\nResult: {result}\\nType: {type(result).__name__}"
        
    except Exception as e:
        return f"❌ Calculation error for '{expression}': {str(e)}"'''
    
    def _get_refund_processing_functions(self) -> str:
        """Generate refund processing functions"""
        return '''# Initialize refund processor with company configuration
refund_processor = None

def initialize_refund_processor(company_id: str, max_refund_amount: str, expected_address: str,
                               custom_api_url: str = None, custom_api_headers: dict = None,
                               custom_api_field: str = None, escalation_threshold: str = None):
    """Initialize the refund processor with company-specific configuration"""
    global refund_processor
    refund_processor = create_refund_processor(
        company_id=company_id,
        max_refund_amount=max_refund_amount,
        expected_address=expected_address,
        custom_api_url=custom_api_url,
        custom_api_headers=custom_api_headers,
        custom_api_field=custom_api_field,
        escalation_threshold=escalation_threshold
    )

async def process_refund_transaction(user_address: str, transaction_hash: str, requested_amount: str,
                                   agent_private_key: str, refund_chain: str, max_refund_amount: str = None,
                                   reason: str = None) -> str:
    """Process a refund transaction"""
    try:
        if not refund_processor:
            return "Error: Refund processor not initialized. Please configure company refund settings."
        
        result = await process_refund(
            refund_processor,
            user_address=user_address,
            transaction_hash=transaction_hash,
            requested_amount=requested_amount,
            agent_private_key=agent_private_key,
            refund_chain=refund_chain,
            max_refund_amount=max_refund_amount,
            reason=reason
        )
        
        if result.get("success"):
            return f"✅ Refund processed successfully! Transaction hash: {result.get('refund_tx_hash')}"
        else:
            if result.get("escalation_required"):
                return f"⚠️ {result.get('error')} - Human intervention required."
            else:
                return f"❌ Refund failed: {result.get('error')}"
                
    except Exception as e:
        return f"Error processing refund: {str(e)}"

async def validate_refund_transaction(user_address: str, transaction_hash: str, requested_amount: str,
                                   refund_chain: str, max_refund_amount: str = None) -> str:
    """Validate a refund request without processing"""
    try:
        if not refund_processor:
            return "Error: Refund processor not initialized. Please configure company refund settings."
        
        result = await validate_refund_request(
            refund_processor,
            user_address=user_address,
            transaction_hash=transaction_hash,
            requested_amount=requested_amount,
            refund_chain=refund_chain,
            max_refund_amount=max_refund_amount
        )
        
        if result.get("valid"):
            return "✅ Refund request is valid and can be processed."
        else:
            if result.get("escalation_required"):
                return f"⚠️ {result.get('error')} - Human intervention required."
            else:
                return f"❌ Refund validation failed: {result.get('error')}"
                
    except Exception as e:
        return f"Error validating refund: {str(e)}"

async def process_overpayment_refund_transaction(user_address: str, transaction_hash: str, expected_amount: str,
                                               agent_private_key: str, refund_chain: str, max_refund_amount: str = None,
                                               reason: str = None) -> str:
    """Process a refund for overpayment scenarios where user paid more than expected"""
    try:
        if not refund_processor:
            return "Error: Refund processor not initialized. Please configure company refund settings."
        
        result = await process_overpayment_refund(
            refund_processor,
            user_address=user_address,
            transaction_hash=transaction_hash,
            expected_amount=expected_amount,
            agent_private_key=agent_private_key,
            refund_chain=refund_chain,
            max_refund_amount=max_refund_amount,
            reason=reason
        )
        
        if result.get("success"):
            overpayment = result.get("overpayment_amount", "0")
            actual_amount = result.get("actual_amount", "0")
            expected_amount = result.get("expected_amount", "0")
            
            # Convert wei to ETH for display
            overpayment_eth = float(overpayment) / 1e18
            actual_eth = float(actual_amount) / 1e18
            expected_eth = float(expected_amount) / 1e18
            
            return f"""✅ Overpayment refund processed successfully! 
            
💰 Refund Details:
   - Expected payment: {expected_eth:.6f} ETH
   - Actual payment: {actual_eth:.6f} ETH  
   - Overpayment refunded: {overpayment_eth:.6f} ETH
   - Refund transaction hash: {result.get('refund_tx_hash')}
   
The difference has been refunded to your wallet address: {user_address}"""
        else:
            if result.get("escalation_required"):
                return f"⚠️ {result.get('error')} - Human intervention required."
            else:
                return f"❌ Overpayment refund failed: {result.get('error')}"
                
    except Exception as e:
        return f"Error processing overpayment refund: {str(e)}"'''
