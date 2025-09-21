"""
Configuration management for the Factory Monitoring Backend.
Loads environment variables and provides application settings.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017/"
    database_name: str = "factory_db"
    
    # SSH Tunnel Configuration for MongoDB
    use_ssh_tunnel: bool = False
    ssh_host: str = "43.205.241.141"
    ssh_port: int = 22
    ssh_username: str = "ubuntu"
    ssh_key_path: str = r"c:\Users\Prash\Desktop\abas\ssh.pem"
    remote_mongodb_host: str = "localhost"
    remote_mongodb_port: int = 27017
    local_mongodb_port: int = 27017
    
    # Development Settings
    debug: bool = False
    reload: bool = True
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # External API Configuration
    external_api_base_url: str = "https://srcapiv2.aams.io/AAMS/AI"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "app.log"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
