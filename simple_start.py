#!/usr/bin/env python3
"""
Simple startup script for the backend.
This script starts the FastAPI server with mock data support.
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    print("🚀 Starting Factory Monitoring Backend...")
    print(f"📍 Server will be available at: http://{settings.api_host}:{settings.api_port}")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔄 Auto-reload enabled")
    print("💾 Using mock data (no MongoDB required)")

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
