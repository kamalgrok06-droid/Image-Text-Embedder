@echo off
title Image Text Embedder v1.0
echo ========================================
echo    Image Text Embedder - Batch Processor
echo ========================================
echo.
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies. Please install Python first.
    pause
    exit /b 1
)
echo.
echo Starting application...
python ImageTextEmbedder.py
echo.
echo ========================================
echo           Processing Complete!
echo ========================================
pause
