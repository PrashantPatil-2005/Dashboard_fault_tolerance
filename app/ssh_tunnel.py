"""
SSH Tunnel management for MongoDB connection.
Handles secure connection to remote MongoDB through SSH tunnel.
"""

import logging
import os
from typing import Optional
from sshtunnel import SSHTunnelForwarder
from app.config import settings

logger = logging.getLogger(__name__)


class SSHTunnelManager:
    """Manages SSH tunnel for MongoDB connection."""
    
    def __init__(self):
        self.tunnel: Optional[SSHTunnelForwarder] = None
        self.tunnel_active = False
    
    def start_tunnel(self) -> bool:
        """Start SSH tunnel to remote MongoDB server."""
        if not settings.use_ssh_tunnel:
            logger.info("SSH tunnel disabled in configuration")
            return True
        
        if not os.path.exists(settings.ssh_key_path):
            logger.error(f"SSH key file not found: {settings.ssh_key_path}")
            logger.error("Please check the SSH_KEY_PATH in your configuration")
            return False
        
        # Check if key file is readable
        if not os.access(settings.ssh_key_path, os.R_OK):
            logger.error(f"SSH key file is not readable: {settings.ssh_key_path}")
            logger.error("Please check file permissions")
            return False
        
        try:
            logger.info(f"Starting SSH tunnel to {settings.ssh_host}:{settings.ssh_port}")
            logger.info(f"Using SSH key: {settings.ssh_key_path}")
            
            self.tunnel = SSHTunnelForwarder(
                (settings.ssh_host, settings.ssh_port),
                ssh_username=settings.ssh_username,
                ssh_pkey=settings.ssh_key_path,
                remote_bind_address=(settings.remote_mongodb_host, settings.remote_mongodb_port),
                local_bind_address=('127.0.0.1', settings.local_mongodb_port),
                ssh_config_file=None,
                allow_agent=False,
                host_pkey_directories=None
            )
            
            self.tunnel.start()
            self.tunnel_active = True
            
            logger.info(f"SSH tunnel established successfully")
            logger.info(f"Local MongoDB available at localhost:{settings.local_mongodb_port}")
            logger.info(f"Remote MongoDB: {settings.remote_mongodb_host}:{settings.remote_mongodb_port}")
            return True
            
        except FileNotFoundError as e:
            logger.error(f"SSH key file not found: {e}")
            return False
        except PermissionError as e:
            logger.error(f"Permission denied accessing SSH key: {e}")
            return False
        except ConnectionError as e:
            logger.error(f"Connection failed to SSH host: {e}")
            logger.error(f"Please check SSH_HOST and SSH_PORT settings")
            return False
        except Exception as e:
            logger.error(f"Failed to start SSH tunnel: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            self.tunnel_active = False
            return False
    
    def stop_tunnel(self):
        """Stop the SSH tunnel."""
        if self.tunnel and self.tunnel_active:
            try:
                self.tunnel.stop()
                self.tunnel_active = False
                logger.info("SSH tunnel stopped")
            except Exception as e:
                logger.error(f"Error stopping SSH tunnel: {e}")
    
    def is_tunnel_active(self) -> bool:
        """Check if tunnel is active."""
        return self.tunnel_active and self.tunnel and self.tunnel.is_active
    
    def get_mongodb_url(self) -> str:
        """Get the appropriate MongoDB URL based on tunnel status."""
        if settings.use_ssh_tunnel and self.is_tunnel_active():
            return f"mongodb://127.0.0.1:{settings.local_mongodb_port}/"
        else:
            return settings.mongodb_url


# Global SSH tunnel manager instance
ssh_tunnel_manager = SSHTunnelManager()
