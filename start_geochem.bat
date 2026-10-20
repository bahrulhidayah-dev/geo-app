@echo off
title GeoChem App
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Python environment not found in %~dp0.venv
    echo Please create it first: python -m venv .venv
    pause
    exit /b 1
)
echo Starting GeoChem App. Your browser will open shortly.
echo Keep this window open while you use the app. Close it to stop the app.
".venv\Scripts\python.exe" -m streamlit run app.py
pause
