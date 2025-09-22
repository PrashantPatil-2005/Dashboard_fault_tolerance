"""
Production configuration for the Factory Monitoring Backend.
This module provides production-specific settings and overrides.
"""

import os
from app.config import Settings


class ProductionSettings(Settings):
    """Production-specific settings."""
    
    # Override MongoDB URL for production
    mongodb_url: str = "mongodb://localhost:27017/"
    database_name: str = "factory_db"
    
    # Production API settings
    api_host: str = "0.0.0.0"  # Bind to all interfaces
    api_port: int = 8000
    
    # Production logging
    log_level: str = "INFO"
    log_file: str = "/home/ubuntu/Dashboard_fault_tolerance/logs/app.log"
    
    # Environment
    environment: str = "production"
    
    # Security settings
    debug: bool = False
    
    class Config:
        env_file = ".env.production"
        env_file_encoding = "utf-8"


# Use production settings if in production environment
if os.getenv("ENVIRONMENT", "development").lower() == "production":
    settings = ProductionSettings()
else:
    from app.config import settings
