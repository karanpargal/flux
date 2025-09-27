"""
Services package initialization with singleton instances
"""

from .company_agent_service import CompanyAgentService

# Singleton instance of the company agent service
_company_agent_service_instance = None

def get_company_agent_service() -> CompanyAgentService:
    """Get singleton instance of company agent service"""
    global _company_agent_service_instance
    if _company_agent_service_instance is None:
        _company_agent_service_instance = CompanyAgentService()
    return _company_agent_service_instance