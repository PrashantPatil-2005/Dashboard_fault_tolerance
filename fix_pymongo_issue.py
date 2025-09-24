#!/usr/bin/env python3
"""
Fix PyMongo compatibility issue in setup_database.py
"""

import re

def fix_pymongo_issue():
    """Fix the PyMongo boolean evaluation issue."""

    with open('setup_database.py', 'r') as f:
        content = f.read()

    # Fix the boolean evaluation issue
    # Change: if not self.db:
    # To: if self.db is None:
    content = re.sub(r'if not self\.db:', 'if self.db is None:', content)

    with open('setup_database.py', 'w') as f:
        f.write(content)

    print("✅ Fixed PyMongo compatibility issue")
    print("🔄 Changed 'if not self.db:' to 'if self.db is None:'")
    print("🚀 You can now run: python setup_database.py")

if __name__ == "__main__":
    fix_pymongo_issue()
