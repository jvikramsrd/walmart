#!/bin/bash

echo "Walmart Logistics Dashboard Starter"
echo "==================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed or not in PATH"
    echo "Please install Python 3.8 or higher and try again"
    exit 1
fi

# Check if requirements are installed
echo "Checking requirements..."
if ! pip list | grep -q streamlit; then
    echo "Installing required packages..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install requirements"
        exit 1
    fi
fi

# Start the application
echo "Starting Walmart Logistics Dashboard..."
streamlit run app.py
