@echo off
cd /d "%~dp0"
echo ===========================================
echo  Sync OpenData HDC - All Years (2570, 2569)
echo ===========================================
uv run python py-get-hdc.py
echo.
pause
