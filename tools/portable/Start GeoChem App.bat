@echo off
title GeoChem App
cd /d "%~dp0"
if not exist "%~dp0python\python.exe" (
  echo Python was not found in this folder. Extract the whole ZIP file first.
  pause
  exit /b 1
)
"%~dp0python\python.exe" "%~dp0launcher.py"
if errorlevel 1 pause
