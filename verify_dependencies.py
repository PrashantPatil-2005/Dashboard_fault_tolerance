#!/usr/bin/env python3
"""
Dependency Verification Script

This script verifies that all required dependencies are installed
and the Factory Monitoring Dashboard can run properly.

Usage:
    python verify_dependencies.py
"""

import sys
import importlib.util
import subprocess
from pathlib import Path

def check_python_package(package_name):
    """Check if a Python package is installed."""
    try:
        spec = importlib.util.find_spec(package_name.replace('-', '_'))
        if spec is None:
            return False, f"{package_name} not found"
        return True, f"{package_name} ✓"
    except Exception as e:
        return False, f"{package_name} error: {e}"

def check_node_package(package_name):
    """Check if a Node.js package is available."""
    try:
        result = subprocess.run(['npm', 'list', package_name, '--depth=0'],
                              capture_output=True, text=True, cwd=Path(__file__).parent / 'frontend')
        if result.returncode == 0:
            return True, f"{package_name} ✓"
        return False, f"{package_name} not found"
    except Exception:
        return False, f"{package_name} check failed"

def main():
    """Main verification function."""
    print("🔍 Factory Monitoring Dashboard - Dependency Verification")
    print("=" * 60)

    all_good = True

    # Essential Python packages
    python_packages = [
        'fastapi', 'uvicorn', 'gunicorn', 'pymongo', 'pydantic',
        'pydantic_settings', 'python-dotenv', 'requests', 'python-multipart',
        'motor', 'pandas', 'numpy', 'matplotlib', 'plotly', 'pytest'
    ]

    print("🐍 Python Dependencies:")
    print("-" * 30)
    for package in python_packages:
        success, message = check_python_package(package)
        status = "✅" if success else "❌"
        print(f"  {status} {message}")
        if not success:
            all_good = False

    # Frontend packages (check if node_modules exists)
    frontend_dir = Path(__file__).parent / 'frontend'
    if frontend_dir.exists():
        print("\n⚛️  Frontend Dependencies:")
        print("-" * 30)

        node_packages = ['react', 'axios', 'primereact', 'chart.js', 'vite']
        for package in node_packages:
            success, message = check_node_package(package)
            status = "✅" if success else "❌"
            print(f"  {status} {message}")
            if not success:
                all_good = False

        # Check if node_modules directory exists
        node_modules = frontend_dir / 'node_modules'
        if node_modules.exists():
            print(f"  ✅ node_modules directory exists")
        else:
            print(f"  ❌ node_modules directory missing")
            all_good = False

    # Check configuration files
    print("\n⚙️  Configuration Files:")
    print("-" * 30)

    config_files = ['requirements.txt', 'start_dashboard.py', 'setup_database.py']
    for config in config_files:
        if Path(config).exists():
            print(f"  ✅ {config}")
        else:
            print(f"  ❌ {config} missing")
            all_good = False

    # Check environment setup
    print("\n🌍 Environment:")
    print("-" * 30)

    env_example = Path('.env.example')
    env_file = Path('.env')

    if env_example.exists():
        print(f"  ✅ {env_example}")
        if not env_file.exists():
            print(f"  ⚠️  .env not found (copy .env.example to .env)")
        else:
            print(f"  ✅ .env")
    else:
        print(f"  ❌ .env.example missing")
        all_good = False

    # Test backend connectivity
    print("\n🔌 Connectivity Test:")
    print("-" * 30)

    try:
        result = subprocess.run([
            'curl', '-s', '-o', '/dev/null', '-w', 'HTTP %{http_code}',
            'http://localhost:8000/health'
        ], capture_output=True, text=True, timeout=5)

        if result.returncode == 0 and '200' in result.stdout:
            print(f"  ✅ Backend API responding (HTTP 200)")
        else:
            print(f"  ⚠️  Backend API not responding")
    except Exception:
        print(f"  ⚠️  Backend API not accessible (this is normal if not running)")

    print("\n" + "=" * 60)

    if all_good:
        print("🎉 All dependencies verified successfully!")
        print("🚀 Your Factory Monitoring Dashboard is ready to run!")
        print("\nTo start the application:")
        print("  python start_dashboard.py dev")
    else:
        print("⚠️  Some dependencies are missing or not properly configured.")
        print("Please check the messages above and ensure all requirements are met.")

    print("=" * 60)

    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
