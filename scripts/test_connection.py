"""
Test script to verify MongoDB connection through SSH tunnel.
"""

import sys
import os
import logging

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db_manager
from app.ssh_tunnel import ssh_tunnel_manager
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_connection():
    """Test MongoDB connection through SSH tunnel."""
    try:
        logger.info("Testing MongoDB connection...")
        logger.info(f"SSH Tunnel: {'Enabled' if settings.use_ssh_tunnel else 'Disabled'}")
        
        if settings.use_ssh_tunnel:
            logger.info(f"SSH Host: {settings.ssh_host}")
            logger.info(f"SSH Key: {settings.ssh_key_path}")
            logger.info(f"Local MongoDB URL: {ssh_tunnel_manager.get_mongodb_url()}")
        
        # Test database connection
        if db_manager.connected:
            logger.info("✅ Database connection successful!")
            
            # Test collections
            collections = ["machines", "bearings", "data"]
            for collection_name in collections:
                collection = db_manager.get_collection(collection_name)
                if collection is not None:
                    count = collection.count_documents({})
                    logger.info(f"✅ Collection '{collection_name}': {count} documents")
                else:
                    logger.warning(f"⚠️  Collection '{collection_name}': Not accessible")
            
            return True
        else:
            logger.error("❌ Database connection failed!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False
    
    finally:
        # Clean up
        if settings.use_ssh_tunnel:
            ssh_tunnel_manager.stop_tunnel()


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
