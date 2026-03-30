@echo off
chcp 65001 >nul
echo ============================================================
echo   Auto Pipeline: MoneyPrinterTurbo → TikTok Upload
echo ============================================================
echo.

cd /d "%~dp0"

:: Activate venv if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

:: Run pipeline (optional: pass topic as argument)
python auto_pipeline.py %*

echo.
pause
