@echo off
cd /d "%~dp0"
echo ===========================================
echo  Sync OpenData HDC - Fiscal Year 2569
echo ===========================================
uv run python py-get-hdc.py 2569
echo.
pause
