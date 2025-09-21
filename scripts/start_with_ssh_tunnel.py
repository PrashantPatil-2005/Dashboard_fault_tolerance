"""
Startup script to run the application with SSH tunnel enabled.
This script sets the USE_SSH_TUNNEL environment variable and starts the application.
"""

import os
import sys
import subprocess
from pathlib import Path

# Set environment variable to enable SSH tunnel
os.environ["USE_SSH_TUNNEL"] = "true"

# Add the parent directory to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import and start the application
try:
    from app.main import app
    import uvicorn
    from app.config import settings
    
    print("Starting Factory Monitoring Backend with SSH Tunnel...")
    print(f"SSH Host: {settings.ssh_host}")
    print(f"SSH Key: {settings.ssh_key_path}")
    print(f"API will be available at: http://{settings.api_host}:{settings.api_port}")
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower()
    )
    
except KeyboardInterrupt:
    print("\nShutting down application...")
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)
