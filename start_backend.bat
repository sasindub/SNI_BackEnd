@echo off
echo ================================================
echo Starting SNI Laptops Backend Server
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Python version:
python --version
echo.

REM Check if requirements are installed
echo Checking dependencies...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

echo Dependencies OK
echo.

REM Test MongoDB connection
echo Testing MongoDB connection...
python test_mongodb.py
if errorlevel 1 (
    echo.
    echo ERROR: MongoDB connection failed
    echo Please check your internet connection and MongoDB credentials
    pause
    exit /b 1
)

echo.
echo ================================================
echo Starting Flask server...
echo ================================================
echo Server will be available at: http://localhost:5000
echo Admin API: http://localhost:5000/api/admin/login
echo.
echo Press Ctrl+C to stop the server
echo ================================================
echo.

python app.py




