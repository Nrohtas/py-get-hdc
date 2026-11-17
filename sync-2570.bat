@echo off
cd /d "%~dp0"
echo ===========================================
echo  Sync OpenData HDC - Fiscal Year 2570
echo ===========================================
uv run python py-get-hdc.py 2570
echo.
pause
