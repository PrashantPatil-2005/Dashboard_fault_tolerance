#!/usr/bin/env python3
"""
Helper script to update MongoDB configuration in .env file.
"""

import os
from pathlib import Path

def update_env_file():
    """Update the .env file with local MongoDB configuration."""

    env_file = Path('.env')

    # Read current content
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
    else:
        content = ""

    # Check if MONGODB_URL is already set
    if 'MONGODB_URL' in content:
        print("MONGODB_URL is already configured in .env file")
        return

    # Add local MongoDB configuration
    new_config = "\n# MongoDB Configuration\nMONGODB_URL=mongodb://localhost:27017/\n"

    if content:
        # Append to existing content
        updated_content = content + new_config
    else:
        # Create new content
        updated_content = new_config

    with open(env_file, 'w') as f:
        f.write(updated_content)

    print("✅ Updated .env file with local MongoDB configuration")
    print("📍 MongoDB URL set to: mongodb://localhost:27017/")
    print("🔄 Please restart the server for changes to take effect")

if __name__ == "__main__":
    update_env_file()
