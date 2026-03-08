# GitHub Authentication Helper Script (PowerShell)
# This script fixes the gh auth login --with-token issue on Windows

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "GitHub CLI Authentication Helper" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check current directory
Write-Host "Step 1: Current working directory" -ForegroundColor Yellow
Write-Host "Current directory: $(Get-Location)"
Write-Host ""

# Step 2: Check if local gh.exe exists (this may cause issues)
Write-Host "Step 2: Checking for local GitHub CLI in project" -ForegroundColor Yellow
$localGhFound = $false

if (Test-Path ".\bin\gh.exe") {
    Write-Host "⚠️  Found local gh.exe in .\bin\ - this may conflict with system gh" -ForegroundColor Red
    $localGhFound = $true
}

if (Test-Path ".\gh\bin\gh.exe") {
    Write-Host "⚠️  Found local gh.exe in .\gh\bin\ - this may conflict with system gh" -ForegroundColor Red
    $localGhFound = $localGhFound -or $true
}

if ($localGhFound) {
    Write-Host ""
    Write-Host "Recommendation: Remove or rename local gh folders to avoid conflicts" -ForegroundColor Green
    Write-Host "  - Remove: bin\gh.exe" -ForegroundColor Gray
    Write-Host "  - Remove: gh\bin\gh.exe" -ForegroundColor Gray
    Write-Host ""
}
Write-Host ""

# Step 3: Find system gh.exe
Write-Host "Step 3: Finding system GitHub CLI" -ForegroundColor Yellow

# Check common locations for gh
$ghPaths = @(
    "$env:ProgramFiles\GitHub CLI\gh.exe",
    "${env:ProgramFiles(x86)}\GitHub CLI\gh.exe",
    "$env:LOCALAPPDATA\GitHub CLI\gh.exe",
    "$home\AppData\Local\GitHub CLI\gh.exe"
)

$ghExe = $null
foreach ($path in $ghPaths) {
    if (Test-Path $path) {
        $ghExe = $path
        break
    }
}

# Also check if gh is in PATH
$ghFromPath = Get-Command gh -ErrorAction SilentlyContinue
if ($ghFromPath -and -not $ghExe) {
    $ghExe = $ghFromPath.Source
}

if ($ghExe) {
    Write-Host "✅ Found GitHub CLI: $ghExe" -ForegroundColor Green
    & $ghExe --version
} else {
    Write-Host "❌ GitHub CLI not found. Please install from: https://cli.github.com" -ForegroundColor Red
    Write-Host "   Or run: winget install GitHub.cli" -ForegroundColor Gray
    exit 1
}
Write-Host ""

# Step 4: Check current auth status
Write-Host "Step 4: Current authentication status" -ForegroundColor Yellow
& $ghExe auth status 2>&1
$authStatus = $LASTEXITCODE
Write-Host ""

# Step 5: If not logged in, offer to authenticate
if ($authStatus -ne 0) {
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "Not authenticated. Choose method:" -ForegroundColor Yellow
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "1. Interactive login (recommended)"
    Write-Host "2. Token-based login"
    Write-Host ""
    
    $choice = Read-Host "Enter choice (1 or 2)"
    
    switch ($choice) {
        "1" {
            Write-Host ""
            Write-Host "Starting interactive login..." -ForegroundColor Green
            & $ghExe auth login
        }
        "2" {
            Write-Host ""
            Write-Host "Token-based login options:" -ForegroundColor Yellow
            Write-Host "Option A: Set GH_TOKEN environment variable and run:"
            Write-Host "  `$env:GH_TOKEN = 'your_token_here'"
            Write-Host "  Get-Content `$env:GH_TOKEN | gh auth login --with-token"
            Write-Host ""
            Write-Host "Option B: Direct token input (less secure):"
            $token = Read-Host "Enter your GitHub Personal Access Token" -AsSecureString
            $tokenPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($token))
            
            Write-Host "Authenticating..."
            $tokenPlain | & $ghExe auth login --with-token
            
            # Clear the token from memory
            $tokenPlain = $null
        }
        default {
            Write-Host "Invalid choice" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Final Authentication Status:" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
& $ghExe auth status

