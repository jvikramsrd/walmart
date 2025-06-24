@echo off
echo Walmart Logistics Dashboard Starter
echo ===================================

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8 or higher and try again
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking requirements...
pip list | findstr streamlit >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing required packages...
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo Failed to install requirements
        pause
        exit /b 1
    )
)

REM Start the application
echo Starting Walmart Logistics Dashboard...
streamlit run app.py

pause
