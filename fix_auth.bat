@echo off
REM GitHub CLI Authentication Fix for Windows
REM This script helps fix gh auth login --with-token issues

echo =========================================
echo GitHub CLI Authentication Fix
echo =========================================
echo.

REM Step 1: Show current directory
echo Step 1: Current Directory
cd
echo.

REM Step 2: Check for local gh.exe (potential conflict)
echo Step 2: Checking for local GitHub CLI...
if exist "bin\gh.exe" (
    echo WARNING: Found local gh.exe in bin\ - this may cause conflicts!
    echo.
    echo Option 1: Rename the folder to avoid conflict
    ren bin bin_old
    echo Renamed bin to bin_old
    echo.
)

if exist "gh\bin\gh.exe" (
    echo WARNING: Found local gh.exe in gh\bin\ - this may cause conflicts!
    echo.
    ren gh gh_old
    echo Renamed gh to gh_old
    echo.
)

REM Step 3: Find system gh.exe
echo Step 3: Finding system GitHub CLI...
where gh >nul 2>&1
if %errorlevel% equ 0 (
    echo Found system gh.exe:
    where gh
    echo.
    gh --version
) else (
    echo GitHub CLI not found in PATH
    echo.
    echo Please install GitHub CLI from: https://cli.github.com
    echo Or run: winget install GitHub.cli
    echo.
    pause
    exit /b 1
)
echo.

REM Step 4: Check authentication status
echo Step 4: Checking authentication status...
gh auth status
echo.

REM Step 5: If not authenticated, offer options
echo =========================================
echo Step 5: Authentication Options
echo =========================================
echo 1. Interactive login (recommended)
echo 2. Token-based login
echo 3. Exit
echo.

set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Starting interactive login...
    gh auth login
) else if "%choice%"=="2" (
    echo.
    echo For token-based login, run:
    echo   echo YOUR_TOKEN ^| gh auth login --with-token
    echo.
    echo Or set GH_TOKEN environment variable:
    echo   setx GH_TOKEN "your_token_here"
    echo.
) else (
    echo Exiting...
    exit /b 0
)

echo.
echo =========================================
echo Final Status:
echo =========================================
gh auth status
echo.
pause

