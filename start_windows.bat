@echo off
echo Factory Monitoring Dashboard Startup
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 16+
    pause
    exit /b 1
)

echo ✅ Dependencies check passed
echo.

REM Install backend dependencies
echo 📦 Installing backend dependencies...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Backend dependencies installation failed, but continuing...
)

REM Install frontend dependencies
echo 📦 Installing frontend dependencies...
cd frontend
npm install >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Frontend dependencies installation failed, but continuing...
)
cd ..

echo.
echo 🚀 Starting servers...
echo.

REM Start backend in background
start "Backend Server" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level info"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in background
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo ====================================
echo 🎉 Dashboard is starting up!
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔌 Backend API: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo 💾 Using mock data (MongoDB not required)
echo ====================================
echo.
echo Press any key to close this window (servers will continue running)
pause >nul
