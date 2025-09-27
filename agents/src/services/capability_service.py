"""
Capability Service for managing agent capabilities and tool injection
"""

from typing import Dict, List, Any, Optional
from enum import Enum


class CapabilityType(Enum):
    """Available capability types for agents"""
    DOCUMENT_REFERENCE = "document_reference"
    TRANSACTION_VERIFICATION = "transaction_verification"
    WEBPAGE_READING = "webpage_reading"
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
            ],
            CapabilityType.TRANSACTION_VERIFICATION.value: [
                {
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
            ],
            CapabilityType.WEBPAGE_READING.value: [
                {
                    "name": "read_webpage_content",
                    "description": "Read and extract content from web pages for information gathering",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL of the webpage to read"
                            },
                            "max_length": {
                                "type": "integer",
                                "description": "Maximum length of content to extract",
                                "default": 10000
                            }
                        },
                        "required": ["url"],
                        "additionalProperties": False
                    },
                    "strict": True
                },
                {
                    "name": "search_webpage_content",
                    "description": "Search for specific terms within a webpage",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL of the webpage to search"
                            },
                            "search_terms": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of terms to search for in the webpage"
                            }
                        },
                        "required": ["url", "search_terms"],
                        "additionalProperties": False
                    },
                    "strict": True
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
            CapabilityType.WEBPAGE_READING.value: "Read and extract information from web pages",
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
            tools_description.append(f"- {tool['name']}: {tool['description']}")
        
        support_categories_str = ', '.join(support_categories) if support_categories else "general, technical, billing"
        company_products_str = ', '.join(company_products) if company_products else "products and services"
        
        system_prompt = f"""You are a helpful AI support agent for {company_name}.

Your role is to assist customers with:
- Product information and how our services work
- Technical support and troubleshooting
- Billing and payment questions
- General inquiries about {company_name}

You have the following capabilities:
{chr(10).join(capability_descriptions)}

You have access to the following tools:
{chr(10).join(tools_description)}

Company Products/Services: {company_products_str}
Support Categories: {support_categories_str}

CRITICAL INSTRUCTIONS:
1. When users ask ANY question about {company_name}, employees, skills, experience, projects, or company information, you MUST ALWAYS call the search_company_documents tool FIRST before responding (if document reference capability is enabled).
2. Use search terms like: "work experience", "programming languages", "technologies", "education", "projects", "skills", "achievements"
3. Do NOT ask for permission - automatically search the documents and provide the information you find.
4. If you find relevant information, share it with the user. If you don't find anything, then explain what you searched for.

Always be helpful, professional, and accurate. Use the available tools when appropriate to provide the best assistance."""

        return system_prompt
    
    def get_tool_imports_for_capabilities(self, capabilities: List[str]) -> List[str]:
        """Get the required imports for tools based on capabilities"""
        imports = []
        
        if CapabilityType.DOCUMENT_REFERENCE.value in capabilities:
            imports.append("from tools.pdf_reader import PDFReader")
        
        if CapabilityType.TRANSACTION_VERIFICATION.value in capabilities:
            imports.append("from tools.transaction_verifier import verify_transaction, get_transaction_verification_schema")
        
        if CapabilityType.WEBPAGE_READING.value in capabilities:
            imports.append("from tools.webpage_reader import WebpageReader, read_webpage_content, search_webpage")
        
        return imports
    
    def get_tool_functions_for_capabilities(self, capabilities: List[str], pdf_document_urls: List[str] = None) -> str:
        """Generate tool function implementations based on capabilities"""
        functions = []
        
        if CapabilityType.DOCUMENT_REFERENCE.value in capabilities:
            functions.append(self._get_document_search_function(pdf_document_urls))
        
        if CapabilityType.TRANSACTION_VERIFICATION.value in capabilities:
            functions.append(self._get_transaction_verification_function())
        
        if CapabilityType.WEBPAGE_READING.value in capabilities:
            functions.append(self._get_webpage_reading_functions())
        
        return "\n\n".join(functions)
    
    def _get_document_search_function(self, pdf_document_urls: List[str] = None) -> str:
        """Generate document search function"""
        default_urls = pdf_document_urls or []
        return f'''async def search_company_documents(search_terms: List[str], document_urls: List[str] = None) -> str:
    """Search through company documents for information"""
    print(f"🔍 search_company_documents called with terms: {{search_terms}}, urls: {{document_urls}}")
    try:
        # Initialize PDF reader
        pdf_reader = PDFReader()
        
        # If specific document URLs provided, search only those
        if document_urls:
            search_results = []
            for url in document_urls:
                try:
                    # Process PDF from URL
                    result = await pdf_reader.read_pdf_from_url(url, max_length=10000)
                    if result.get("success") and result.get("content"):
                        content = result.get("content", "").lower()
                        
                        # Search for terms in the document
                        found_terms = []
                        for term in search_terms:
                            if term.lower() in content:
                                found_terms.append(term)
                        
                        if found_terms:
                            search_results.append(f"Document {{url}}: Found terms: {{', '.join(found_terms)}}")
                except Exception as e:
                    search_results.append(f"Error processing {{url}}: {{str(e)}}")
        else:
            # Default document URLs for this company
            default_urls = {default_urls}
            search_results = []
            
            for url in default_urls:
                try:
                    result = await pdf_reader.read_pdf_from_url(url, max_length=10000)
                    if result.get("success") and result.get("content"):
                        content = result.get("content", "").lower()
                        found_terms = []
                        for term in search_terms:
                            if term.lower() in content:
                                found_terms.append(term)
                        
                        if found_terms:
                            search_results.append(f"Document {{url}}: Found terms: {{', '.join(found_terms)}}")
                except Exception as e:
                    search_results.append(f"Error processing {{url}}: {{str(e)}}")
        
        if search_results:
            return f"Found relevant information in company documents:\\n" + "\\n".join(search_results)
        else:
            return f"No relevant information found for terms: {{', '.join(search_terms)}}"
            
    except Exception as e:
        return f"Error searching documents: {{str(e)}}"'''
    
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
    
    def _get_webpage_reading_functions(self) -> str:
        """Generate webpage reading functions"""
        return '''async def read_webpage_content(url: str, max_length: int = 10000) -> str:
    """Read content from a webpage"""
    try:
        result = await read_webpage_content(url, max_length)
        return result if result else f"Error reading webpage: {url}"
    except Exception as e:
        return f"Error reading webpage: {str(e)}"

async def search_webpage_content(url: str, search_terms: List[str]) -> str:
    """Search for terms within a webpage"""
    try:
        result = await search_webpage(url, search_terms)
        if result.get("success"):
            search_results = result.get("search_results", {})
            found_terms = [term for term, data in search_results.items() if data.get("found")]
            if found_terms:
                return f"Found terms in webpage: {', '.join(found_terms)}"
            else:
                return f"No terms found in webpage: {', '.join(search_terms)}"
        else:
            return f"Error searching webpage: {result.get('error', 'Unknown error')}"
    except Exception as e:
        return f"Error searching webpage: {str(e)}"'''
