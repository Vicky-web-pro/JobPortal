#!/bin/bash
# GitHub Authentication Helper Script
# This script fixes the gh auth login --with-token issue

echo "========================================="
echo "GitHub CLI Authentication Helper"
echo "========================================="
echo ""

# Step 1: Check current directory
echo "Step 1: Current working directory"
pwd
echo ""

# Step 2: Check which gh is being used
echo "Step 2: Checking GitHub CLI location"
which gh || echo "gh not found in PATH"
echo ""

# Step 3: Check if local gh.exe exists (this may cause issues)
echo "Step 3: Checking for local GitHub CLI in project"
if [ -f "./bin/gh.exe" ]; then
    echo "⚠️  Found local gh.exe in ./bin/ - this may conflict with system gh"
fi
if [ -f "./gh/bin/gh.exe" ]; then
    echo "⚠️  Found local gh.exe in ./gh/bin/ - this may conflict with system gh"
fi
echo ""

# Step 4: Use system gh (not local)
echo "Step 4: Using system GitHub CLI"
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
hash -r
echo ""

# Step 5: Check if gh is available now
echo "Step 5: Verifying GitHub CLI"
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI found: $(which gh)"
    gh --version
else
    echo "❌ GitHub CLI not found. Please install from: https://cli.github.com"
    exit 1
fi
echo ""

# Step 6: Check current auth status
echo "Step 6: Current authentication status"
gh auth status
echo ""

# Step 7: If not logged in, prompt for login
if ! gh auth status &> /dev/null; then
    echo "========================================="
    echo "Not authenticated. Choose authentication method:"
    echo "========================================="
    echo "1. Interactive login (recommended)"
    echo "2. Token-based login (--with-token)"
    echo ""
    read -p "Enter choice (1 or 2): " choice
    
    case $choice in
        1)
            echo ""
            echo "Starting interactive login..."
            gh auth login
            ;;
        2)
            echo ""
            echo "For token-based login, run:"
            echo "  echo YOUR_TOKEN | gh auth login --with-token"
            echo ""
            echo "Or set GH_TOKEN environment variable and run this script again."
            ;;
        *)
            echo "Invalid choice"
            exit 1
            ;;
    esac
fi

echo ""
echo "========================================="
echo "Authentication complete!"
echo "========================================="
gh auth status

