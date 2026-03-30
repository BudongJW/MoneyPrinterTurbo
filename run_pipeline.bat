@echo off
chcp 65001 >nul 2>&1
title Auto Video Pipeline
cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    set "PYTHON=venv\Scripts\python.exe"
) else (
    set "PYTHON=python"
)

%PYTHON% auto_pipeline.py %* 2>nul

exit /b %errorlevel%
