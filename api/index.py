"""
Vercel Python Function Entry Point
===================================
This file serves as the entry point for Vercel's Python runtime.
It imports the Flask app from the backend and exports it.
"""

from backend.app import app

# Export the app for Vercel
app = app

