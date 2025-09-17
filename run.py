#!/usr/bin/env python3
"""
Production runner script for Factory Monitoring Backend.
This script provides different ways to run the application.
"""

import os
import sys
import argparse
import subprocess
from app.config import settings


def run_development():
    """Run the application in development mode with auto-reload."""
    print("🚀 Starting Factory Monitoring Backend in development mode...")
    print(f"📍 Server will be available at: http://{settings.api_host}:{settings.api_port}")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔄 Auto-reload enabled")
    
    os.system(f"python -m uvicorn app.main:app --reload --host {settings.api_host} --port {settings.api_port}")


def run_production():
    """Run the application in production mode with Gunicorn."""
    print("🚀 Starting Factory Monitoring Backend in production mode...")
    print(f"📍 Server will be available at: http://{settings.api_host}:{settings.api_port}")
    print("⚡ Using Gunicorn with Uvicorn workers")
    
    cmd = [
        "gunicorn",
        "app.main:app",
        "-c", "gunicorn.conf.py"
    ]
    
    subprocess.run(cmd)


def run_single_worker():
    """Run the application with a single Uvicorn worker."""
    print("🚀 Starting Factory Monitoring Backend with single worker...")
    print(f"📍 Server will be available at: http://{settings.api_host}:{settings.api_port}")
    
    os.system(f"uvicorn app.main:app --host {settings.api_host} --port {settings.api_port}")


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Factory Monitoring Backend Runner")
    parser.add_argument(
        "mode",
        choices=["dev", "prod", "single"],
        help="Run mode: dev (development with reload), prod (production with gunicorn), single (single worker)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "dev":
        run_development()
    elif args.mode == "prod":
        run_production()
    elif args.mode == "single":
        run_single_worker()


if __name__ == "__main__":
    main()
