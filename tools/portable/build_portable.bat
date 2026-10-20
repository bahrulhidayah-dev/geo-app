@echo off
title Build GeoChem App portable
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_portable.ps1"
echo.
pause
