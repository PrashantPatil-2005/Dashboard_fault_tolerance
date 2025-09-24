"""
Configuration management for the Factory Monitoring Backend.
Loads environment variables and provides application settings.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv, find_dotenv

# Load environment variables from the nearest .env file (searching upward)
# This ensures the app picks up the root project's .env even when run from a subdirectory
load_dotenv(find_dotenv())

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017/"
    database_name: str = "factory_db"

    # Environment detection
    environment: str = "development"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # External API Configuration
    external_api_base_url: str = "https://srcapiv2.aams.io/AAMS/AI"

    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "app.log"

    # Frontend Configuration
    frontend_url: str = "http://localhost:3000"

    # Optional SSH Tunnel Configuration
    ssh_tunnel_enable: bool = Field(False, env="SSH_TUNNEL_ENABLE")
    ssh_host: Optional[str] = Field(None, env="SSH_HOST")
    ssh_port: int = Field(22, env="SSH_PORT")
    ssh_username: Optional[str] = Field(None, env="SSH_USERNAME")
    ssh_pkey_path: Optional[str] = Field(None, env="SSH_PKEY_PATH")
    ssh_pkey_password: Optional[str] = Field(None, env="SSH_PKEY_PASSWORD")
    ssh_bind_host: str = Field("localhost", env="SSH_BIND_HOST")
    ssh_bind_port: int = Field(27017, env="SSH_BIND_PORT")
    ssh_local_bind_host: str = Field("127.0.0.1", env="SSH_LOCAL_BIND_HOST")
    ssh_local_bind_port: int = Field(27017, env="SSH_LOCAL_BIND_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # Allow extra fields in environment variables

# Global settings instance
settings = Settings()
