@echo off
echo ============================================================
echo  Fake LabelMaker License Server - Run as Administrator!
echo ============================================================
echo.

:: Check for admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This script must be run as Administrator!
    echo         Right-click and select "Run as administrator"
    pause
    exit /b 1
)

:: Check if hosts entry exists
findstr /C:"labelmaker.cc" C:\Windows\System32\drivers\etc\hosts >nul 2>&1
if %errorLevel% neq 0 (
    echo [*] Adding labelmaker.cc to hosts file...
    echo 127.0.0.1 labelmaker.cc >> C:\Windows\System32\drivers\etc\hosts
    echo [+] Done!
) else (
    echo [+] Hosts entry already exists
)

echo.
echo [*] Starting fake license server...
echo.
cd /d "%~dp0"
python server.py
pause
