@echo off
chcp 65001 >nul
echo ============================================================
echo   Setup Windows Task Scheduler for Auto Pipeline
echo ============================================================
echo.

set SCRIPT_DIR=%~dp0
set PYTHON_PATH=%SCRIPT_DIR%venv\Scripts\python.exe
set PIPELINE_SCRIPT=%SCRIPT_DIR%auto_pipeline.py

:: Check if python exists
if not exist "%PYTHON_PATH%" (
    echo [ERROR] venv not found. Using system python.
    set PYTHON_PATH=python
)

echo Task Name: AutoVideoPipeline
echo Script: %PIPELINE_SCRIPT%
echo Schedule: Daily at 10:00 AM
echo.

:: Create scheduled task (runs daily at 10:00)
schtasks /create /tn "AutoVideoPipeline" /tr "\"%PYTHON_PATH%\" \"%PIPELINE_SCRIPT%\"" /sc daily /st 10:00 /f

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Scheduled task created!
    echo   - Task: AutoVideoPipeline
    echo   - Runs daily at 10:00 AM
    echo.
    echo To modify: Task Scheduler ^> AutoVideoPipeline
    echo To delete: schtasks /delete /tn "AutoVideoPipeline" /f
) else (
    echo.
    echo [ERROR] Failed to create task. Try running as Administrator.
)

echo.
pause
