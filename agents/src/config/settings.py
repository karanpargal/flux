from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # CORS settings
    cors_origins: List[str] = ["*"]
    cors_credentials: bool = True
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]
    
    # Agent settings
    agents_directory: str = "src/agents"
    default_seed_phrase: str = "default_seed_phrase"
    
    # Process settings
    process_timeout: int = 5
    
    
    # Company agent settings
    company_agents_directory: str = "src/company_agents"
    default_company_agent_port: int = 5000
    
    # Webhook settings
    webhook_base_url: Optional[str] = None
    webhook_timeout: int = 30
    
    # API keys
    agentverse_api_key: Optional[str] = None
    asi_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
_settings: Settings = None


def get_settings() -> Settings:
    """Get application settings"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
