@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo Starting DAH 2026 drone attack-defense simulation...
echo.
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py
) else (
    python main.py
)
echo.
echo ============================================================
echo  Done. Results are also saved in results.txt
echo  Press any key to close this window.
echo ============================================================
pause >nul
