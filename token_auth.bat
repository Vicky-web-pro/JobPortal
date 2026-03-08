@echo off
REM This script helps authenticate with GitHub CLI using a token
REM Usage: Run this script and enter your token when prompted

echo GitHub CLI Token Authentication
echo =================================
echo.
echo This script will authenticate gh.exe with your GitHub token.
echo NOTE: The token will be visible on screen while typing.
echo.
echo Press Enter to continue or Ctrl+C to cancel...
pause >nul

echo.
echo Enter your GitHub Personal Access Token:
set /p TOKEN=

echo.
echo Authenticating...
echo %TOKEN% | bin\gh.exe auth login --with-token

echo.
echo Checking auth status...
bin\gh.exe auth status

echo.
pause

