from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routes import agent_router, health_router, company_agent_router, webhook_router, tool_router, rest_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title="Multi-Agent Management Server",
        description="A FastAPI server for creating and managing multiple uAgents with company-specific agents",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )
    
    # Include routers
    app.include_router(agent_router)
    app.include_router(company_agent_router)
    app.include_router(webhook_router)
    app.include_router(tool_router)
    app.include_router(rest_router)
    app.include_router(health_router)
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
