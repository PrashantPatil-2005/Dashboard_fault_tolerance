"""
App package for the Factory Monitoring Backend.

This package exposes commonly used objects for convenience and
documents the package version. Importing from `app` continues to work
as expected, e.g. `from app.config import settings`.
"""

from .config import settings

# Optional: re-export the FastAPI app instance for integrations/tools
# that prefer importing from the package root. This keeps normal
# `uvicorn app.main:app` usage unchanged.
from .main import app as fastapi_app  # noqa: F401

__all__ = [
    "settings",
    "fastapi_app",
]

__version__ = "1.0.0"

