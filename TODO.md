# Job Portal - Vercel Deployment Fix

## Issues Fixed

### ✅ 1. Added Vercel WSGI Handler
- Added `handler(event, context)` function in `backend/app.py`
- This is required for Vercel's Python runtime to execute the Flask app

### ✅ 2. Fixed vercel.json Configuration
- Updated Python version from 3.9 to 3.11 (required for Flask 3.0)
- Added static file handling configuration
- Added installCommand for pip

### ✅ 3. Fixed Database Path
- Database now uses `/tmp` directory on Vercel (ephemeral filesystem)
- Falls back to local `backend/database.db` for development

### ✅ 4. Added Error Handling
- All routes wrapped in try/catch blocks
- Returns proper JSON error responses instead of crashing

### ✅ 5. Fixed Python Version
- Updated to Python 3.11 in both vercel.json and pyproject.toml

## Deployment Instructions

### Prerequisites
1. Install Vercel CLI: `npm i -g vercel`
2. Login to Vercel: `vercel login`

### Deploy to Vercel
```bash
# Navigate to project directory
cd c:/Users/DELL/OneDrive/Desktop/JobPortal

# Deploy to Vercel
vercel deploy --prod
```

### Local Testing
```bash
# Run locally
python backend/app.py

# Access at http://127.0.0.1:5000
```

## Root Cause Explanation

### What is FUNCTION_INVOCATION_FAILED?

This error occurs when Vercel's serverless function fails to execute properly. The causes include:

1. **Missing Handler Function**: Vercel Python runtime needs a `handler(event, context)` function as the entry point, not just `app.run()`

2. **Database Path Issues**: SQLite database on Vercel must be in `/tmp` since the main filesystem is ephemeral (read-only)

3. **Python Version Mismatch**: Flask 3.0 requires Python 3.10+, but the config specified 3.9

4. **No Error Handling**: Unhandled exceptions crash the function without meaningful error messages

### How Serverless Functions Work on Vercel

- Each request triggers a new function instance
- The function must return a dict with `statusCode`, `headers`, and `body`
- Filesystem is ephemeral - changes are lost between invocations
- Cold starts can cause delays on first request

## Best Practices Applied

1. ✅ Proper WSGI handler for Vercel
2. ✅ Try/catch error handling on all routes
3. ✅ Database in /tmp for Vercel compatibility
4. ✅ Correct Python version (3.11)
5. ✅ Static file configuration
6. ✅ Environment-based configuration

