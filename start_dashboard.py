#!/usr/bin/env python3
"""
Factory Monitoring Dashboard Startup Script

This script starts both the FastAPI backend and React frontend for the
Factory Monitoring Dashboard. It handles dependency checking and provides
options for development and production modes.

Usage:
    python start_dashboard.py [dev|prod]
    - dev: Start in development mode with hot reload (default)
    - prod: Start in production mode

Requirements:
    - Python 3.8+
    - Node.js 16+
    - MongoDB (optional - will use mock data if not available)
"""

import os
import sys
import time
import subprocess
import signal
import argparse
from pathlib import Path

# Configuration
BACKEND_DIR = Path(__file__).parent
FRONTEND_DIR = BACKEND_DIR / "frontend"
BACKEND_PORT = 8000
FRONTEND_PORT = 3000

# Process storage for graceful shutdown
processes = []

def check_mongodb_connection():
    """Check if MongoDB is running and accessible."""
    try:
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        print("✅ MongoDB is running and accessible")
        return True
    except Exception as e:
        print(f"⚠️  MongoDB not available: {e}")
        print("💡 The application will use realistic mock data")
        return False

def setup_database():
    """Setup database with sample data if MongoDB is available."""
    if not check_mongodb_connection():
        return False

    print("🗄️  Setting up database with sample data...")
    try:
        result = subprocess.run([
            sys.executable, "setup_database.py"
        ], cwd=BACKEND_DIR, check=True, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Database setup completed successfully")
            return True
        else:
            print(f"⚠️  Database setup failed: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Database setup encountered issues: {e}")
        return False
    except FileNotFoundError:
        print("⚠️  setup_database.py not found, skipping database setup")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")

    # Check Python
    try:
        result = subprocess.run([sys.executable, "--version"],
                              capture_output=True, text=True, check=True)
        print(f"✅ Python: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Python not found. Please install Python 3.8+")
        return False

    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"],
                              capture_output=True, text=True, check=True)
        print(f"✅ Node.js: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js not found. Please install Node.js 16+")
        return False

    # Check npm
    try:
        result = subprocess.run(["npm", "--version"],
                              capture_output=True, text=True, check=True)
        print(f"✅ npm: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm not found. Please install npm")
        return False

    return True

def install_backend_deps():
    """Install Python backend dependencies."""
    print("📦 Installing backend dependencies...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install",
            "-r", "requirements.txt"
        ], cwd=BACKEND_DIR, check=True, capture_output=True, text=True)
        print("✅ Backend dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install backend dependencies: {e.stderr}")
        return False

def install_frontend_deps():
    """Install Node.js frontend dependencies."""
    print("📦 Installing frontend dependencies...")
    try:
        result = subprocess.run(["npm", "install"],
                              cwd=FRONTEND_DIR, check=True, capture_output=True, text=True)
        print("✅ Frontend dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install frontend dependencies: {e.stderr}")
        return False

def start_backend(dev_mode=True):
    """Start the FastAPI backend server."""
    print("🚀 Starting backend server...")

    if dev_mode:
        # Development mode with auto-reload
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", str(BACKEND_PORT),
            "--log-level", "info"
        ]
    else:
        # Production mode with gunicorn
        cmd = [
            "gunicorn",
            "app.main:app",
            "-c", "gunicorn.conf.py",
            "--log-level", "info"
        ]

    try:
        process = subprocess.Popen(
            cmd,
            cwd=BACKEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        processes.append(process)
        print(f"✅ Backend started on http://localhost:{BACKEND_PORT}")

        # Wait a moment for the server to start
        time.sleep(2)

        # Check if the server is responding
        try:
            result = subprocess.run([
                "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                f"http://localhost:{BACKEND_PORT}/health"
            ], capture_output=True, text=True, timeout=10)

            if result.stdout.strip() == "200":
                print("✅ Backend health check passed")
                return True
            else:
                print("⚠️  Backend health check failed, but continuing...")
                return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            print("⚠️  Backend health check failed, but continuing...")
            return True

    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def start_frontend():
    """Start the React frontend development server."""
    print("🚀 Starting frontend server...")

    try:
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=FRONTEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        processes.append(process)
        print(f"✅ Frontend started on http://localhost:{FRONTEND_PORT}")
        print("📚 Frontend will be available at: http://localhost:3000")

        # Wait a moment for the server to start
        time.sleep(3)

        return True

    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("\n🛑 Shutting down servers...")
    for process in processes:
        if process.poll() is None:  # Process is still running
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
    sys.exit(0)

def main():
    """Main startup function."""
    parser = argparse.ArgumentParser(description="Factory Monitoring Dashboard Startup Script")
    parser.add_argument(
        "mode",
        nargs="?",
        choices=["dev", "prod"],
        default="dev",
        help="Startup mode: dev (development) or prod (production)"
    )
    parser.add_argument(
        "--skip-db-setup",
        action="store_true",
        help="Skip database setup (use mock data only)"
    )
    args = parser.parse_args()

    print("🏭 Factory Monitoring Dashboard Startup")
    print("=" * 50)

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Please install required dependencies.")
        sys.exit(1)

    # Install dependencies if needed
    if not install_backend_deps():
        sys.exit(1)

    if not install_frontend_deps():
        sys.exit(1)

    # Setup database if available and not skipped
    if not args.skip_db_setup:
        setup_database()
    else:
        print("💡 Skipping database setup (using mock data only)")

    # Start servers
    backend_started = start_backend(dev_mode=(args.mode == "dev"))
    if not backend_started:
        print("❌ Failed to start backend. Exiting...")
        sys.exit(1)

    frontend_started = start_frontend()
    if not frontend_started:
        print("⚠️  Frontend failed to start, but backend is running.")
        print(f"   Backend API: http://localhost:{BACKEND_PORT}")
        print("   API Documentation: http://localhost:8000/docs")

    print("\n" + "=" * 50)
    if frontend_started:
        print("🎉 Dashboard is ready!")
        print(f"🌐 Frontend: http://localhost:{FRONTEND_PORT}")
        print(f"🔌 Backend API: http://localhost:{BACKEND_PORT}")
        print("📚 API Documentation: http://localhost:8000/docs")
        if check_mongodb_connection():
            print("🗄️  Using real MongoDB database")
        else:
            print("💾 Using realistic mock data (no MongoDB required)")
    else:
        print("🎉 Backend API is ready!")
        print(f"🔌 Backend API: http://localhost:{BACKEND_PORT}")
        print("📚 API Documentation: http://localhost:8000/docs")
        if check_mongodb_connection():
            print("🗄️  Using real MongoDB database")
        else:
            print("💾 Using realistic mock data (no MongoDB required)")
    print("=" * 50)
    print("Press Ctrl+C to stop all servers")

    # Monitor processes
    try:
        while True:
            time.sleep(1)
            # Check if any processes have died
            for i, process in enumerate(processes[:]):  # Use slice copy
                if process.poll() is not None:
                    print(f"⚠️  Process {i} exited with code {process.returncode}")
                    processes.remove(process)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()
