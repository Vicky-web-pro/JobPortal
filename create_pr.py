#!/usr/bin/env python3
"""
Script to create a pull request on GitHub using PyGithub

Usage:
    python create_pr.py
    
    OR with GH_TOKEN environment variable:
    
    Windows (PowerShell): $env:GH_TOKEN = 'your_token_here'
    Windows (CMD):       set GH_TOKEN=your_token_here
    Linux/Mac:           export GH_TOKEN=your_token_here
    
    Then run: python create_pr.py
"""

from github import Github

# Try to get token from environment
import os
token = os.environ.get('GH_TOKEN')

if not token:
    print("=" * 50)
    print("GH_TOKEN environment variable not set.")
    print("=" * 50)
    print("")
    print("Please set your GitHub Personal Access Token:")
    print("  1. Go to https://github.com/settings/tokens")
    print("  2. Create a new token with 'repo' scope")
    print("")
    print("Windows (PowerShell):")
    print('  $env:GH_TOKEN = "your_token_here"')
    print("")
    print("Windows (CMD):")
    print('  set GH_TOKEN=your_token_here')
    print("")
    print("Linux/Mac:")
    print('  export GH_TOKEN="your_token_here"')
    print("")
    print("Then run: python create_pr.py")
    print("")
    print("Alternative: Use GitHub CLI directly:")
    print("  gh auth login")
    print("")
    print("Or create the pull request manually at:")
    print("https://github.com/Vicky-web-pro/JobPortal/compare/main...blackboxai/fix-vercel-function-invocation-failed")
    print("=" * 50)
    exit(1)

try:
    # Authenticate with GitHub
    g = Github(token)
    
    # Get the repository
    repo = g.get_repo("Vicky-web-pro/JobPortal")
    
    # Create the pull request
    pr = repo.create_pull(
        title="Add Vercel deployment configuration and guide",
        body="""This PR adds Vercel deployment support for the Flask Job Portal:

- Updated requirements.txt with gunicorn for production deployment
- Added comprehensive DEPLOYMENT_GUIDE.md with step-by-step deployment instructions
- Updated TODO.md to reflect project completion status

The changes enable successful deployment to Vercel with proper Python runtime configuration.""",
        base="main",
        head="blackboxai/fix-vercel-function-invocation-failed"
    )
    
    print(f"✅ Pull request created successfully!")
    print(f"PR URL: {pr.html_url}")
    
except Exception as e:
    print(f"Error creating pull request: {e}")
    print("")
    print("You can create the pull request manually at:")
    print("https://github.com/Vicky-web-pro/JobPortal/compare/main...blackboxai/fix-vercel-function-invocation-failed")
    exit(1)

