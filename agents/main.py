#!/usr/bin/env python3
"""
Main entry point for the Multi-Agent Management Server
"""

import uvicorn
from src.main import app
from src.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
