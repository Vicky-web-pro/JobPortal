# GitHub CLI Authentication Fix Guide

This document explains how to fix the `gh auth login --with-token` issue when deploying your project to Vercel.

---

## The Problem

When running `gh auth login --with-token`, you may encounter issues because:

1. **Wrong working directory** - The command runs in a different terminal path
2. **Local GitHub CLI conflict** - Your project has local `gh.exe` files that conflict with the system-installed version
3. **Environment path issues** - Terminal is using the wrong GitHub CLI executable

---

## Solution 1: Use the Helper Script (Recommended)

We've created a PowerShell helper script to diagnose and fix the issue:

```powershell
# Run the authentication helper
.\auth_helper.ps1
```

This script will:
- ✅ Detect if local `gh.exe` files are causing conflicts
- ✅ Find the system-installed GitHub CLI
- ✅ Check current authentication status
- ✅ Guide you through authentication

---

## Solution 2: Manual Fix Steps

### Step 1: Remove/Ignore Local GitHub CLI

Your project contains local GitHub CLI executables that may conflict:

```
bin/gh.exe        ⚠️ Remove or rename this folder
gh/bin/gh.exe     ⚠️ Remove or rename this folder
```

**Quick fix - rename the folders:**
```powershell
Rename-Item bin bin_old
Rename-Item gh gh_old
```

### Step 2: Verify System GitHub CLI

Check which `gh` executable is being used:

```powershell
where gh
```

Expected output (should show system installation):
```
C:\Program Files\GitHub CLI\gh.exe
```

### Step 3: Authenticate Properly

**Option A: Interactive Login (Recommended)**
```powershell
gh auth login
```

Follow the prompts:
- GitHub.com → HTTPS → Login with browser

**Option B: Token-Based Login**
```powershell
# Set token as environment variable
$env:GH_TOKEN = "your_personal_access_token"

# Then authenticate
Get-Content $env:GH_TOKEN | gh auth login --with-token
```

Or directly:
```powershell
echo YOUR_TOKEN | gh auth login --with-token
```

### Step 4: Verify Authentication

```powershell
gh auth status
```

Expected output:
```
Logged in to github.com as <username>
```

---

## Solution 3: For Vercel Deployment

If you're deploying to Vercel and need GitHub authentication:

### Option A: Use GitHub Integration (Recommended)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Add New → Project
3. Import from GitHub
4. Authorize Vercel to access your repositories

### Option B: Use Personal Access Token

1. Generate a token: https://github.com/settings/tokens
2. Required scopes: `repo`
3. Set as Vercel environment variable:
   - Go to Project Settings → Environment Variables
   - Add: `GH_TOKEN` = your_token

### Option C: Use create_pr.py Script

Our project includes a Python script to create PRs:

```powershell
# Set the token
$env:GH_TOKEN = "your_personal_access_token"

# Run the script
python create_pr.py
```

---

## Troubleshooting

### "gh: command not found"

**Cause:** GitHub CLI not installed or not in PATH

**Solution:**
```powershell
# Install GitHub CLI
winget install GitHub.cli

# Or download from: https://cli.github.com
```

### "Not authenticated"

**Cause:** No valid authentication token

**Solution:**
```powershell
gh auth login
```

### Authentication loops or doesn't persist

**Cause:** May be using wrong `gh` executable

**Solution:**
1. Check `where gh` - should show `C:\Program Files\GitHub CLI\gh.exe`
2. Remove/rename local `gh.exe` in project folder
3. Restart terminal and try again

### Token authentication fails with "Bad credentials"

**Cause:** Invalid or expired token

**Solution:**
1. Generate new token at: https://github.com/settings/tokens
2. Ensure token has `repo` scope
3. Try interactive login instead

---

## Quick Reference Commands

```powershell
# Check current directory
pwd

# Check which gh is being used
where gh

# Check authentication status
gh auth status

# Login interactively
gh auth login

# Login with token
echo TOKEN | gh auth login --with-token

# Logout
gh auth logout

# List configured accounts
gh auth list
```

---

## For Vercel + GitHub Integration

If your goal is to deploy to Vercel with GitHub:

1. **Don't need `gh` CLI** - Vercel uses OAuth integration
2. **Just push to GitHub:**
```powershell
git add .
git commit -m "Your message"
git push origin main
```

3. **Connect in Vercel:**
   - Dashboard → Add Project → Import from GitHub
   - Vercel will automatically deploy on push

---

**Need more help?**
- GitHub CLI Docs: https://cli.github.com/manual
- Vercel Docs: https://vercel.com/docs

