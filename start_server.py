#!/usr/bin/env python3
"""
Direct server startup script for Factory Monitoring Backend.
This bypasses the uvicorn command line tool and starts the server directly.
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    print("🚀 Starting Factory Monitoring Backend...")
    print(f"📍 Server will be available at: http://{settings.api_host}:{settings.api_port}")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔄 Auto-reload enabled")
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
