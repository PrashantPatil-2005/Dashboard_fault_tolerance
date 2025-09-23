@echo off
echo MongoDB Installation Script for Windows
echo ======================================
echo.

REM Check if MongoDB is already installed
mongod --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ MongoDB is already installed
    echo Version: 
    mongod --version
    goto :start_service
)

echo 📦 Installing MongoDB Community Edition...
echo.

REM Check if we have internet connection
ping -n 1 google.com >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ No internet connection detected.
    echo Please connect to the internet and run this script again.
    pause
    exit /b 1
)

echo 🔄 Downloading MongoDB installer...
echo.

REM Create temp directory
if not exist "%TEMP%\mongodb_install" mkdir "%TEMP%\mongodb_install"

REM Download MongoDB installer (you may need to update this URL)
echo 📥 Note: Please download MongoDB from https://www.mongodb.com/try/download/community
echo and run the installer manually, then run this script again.
echo.
echo Alternatively, you can:
echo 1. Go to https://www.mongodb.com/try/download/community
echo 2. Download the latest MongoDB Community Server MSI installer
echo 3. Run the installer
echo 4. Choose "Complete" installation
echo 5. Ensure "Install MongoDB as a Service" is checked
echo 6. Run this script again to configure it
echo.

REM For now, let's try to use a direct download approach
echo 🔄 Attempting to download MongoDB automatically...
powershell -Command "Invoke-WebRequest -Uri 'https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-7.0.0-signed.msi' -OutFile '%TEMP%\mongodb_install\mongodb.msi'"

if %errorlevel% neq 0 (
    echo ❌ Failed to download MongoDB automatically.
    echo.
    echo Please manually download and install MongoDB:
    echo 1. Visit: https://www.mongodb.com/try/download/community
    echo 2. Download the latest MongoDB Community Server
    echo 3. Run the installer
    echo 4. Choose "Complete" installation
    echo 5. Make sure "Install MongoDB as a Service" is checked
    echo.
    pause
    exit /b 1
)

echo ✅ MongoDB downloaded successfully
echo.

:start_service
echo 🚀 Starting MongoDB service...
echo.

REM Try to start MongoDB service
net start MongoDB >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  MongoDB service not found or failed to start
    echo Trying to start MongoDB manually...
    echo.

    REM Look for mongod.exe in common locations
    set "MONGOD_PATH="
    if exist "C:\Program Files\MongoDB\Server\*\bin\mongod.exe" (
        for /d %%i in ("C:\Program Files\MongoDB\Server\*") do (
            if exist "%%i\bin\mongod.exe" (
                set "MONGOD_PATH=%%i\bin\mongod.exe"
                goto :found_mongod
            )
        )
    )

    if exist "%ProgramFiles(x86)%\MongoDB\Server\*\bin\mongod.exe" (
        for /d %%i in ("%ProgramFiles(x86)%\MongoDB\Server\*") do (
            if exist "%%i\bin\mongod.exe" (
                set "MONGOD_PATH=%%i\bin\mongod.exe"
                goto :found_mongod
            )
        )
    )

    echo ❌ MongoDB executable not found in standard locations
    echo Please ensure MongoDB is properly installed and try again.
    echo.
    echo Alternative: Run the database setup with mock data:
    echo python setup_database.py
    echo.
    pause
    exit /b 1

    :found_mongod
    echo ✅ Found MongoDB at: %MONGOD_PATH%
    echo Starting MongoDB...
    start "MongoDB" "%MONGOD_PATH%" --dbpath "C:\data\db" --logpath "C:\data\log\mongod.log" --service
    echo ✅ MongoDB started manually
    goto :setup_complete
)

echo ✅ MongoDB service started successfully

:setup_complete
echo.
echo ====================================
echo ✅ MongoDB is now running!
echo.
echo Next steps:
echo 1. Run the database setup script:
echo    python setup_database.py
echo.
echo 2. Start the dashboard:
echo    python start_dashboard.py dev
echo.
echo ====================================
echo.
pause
