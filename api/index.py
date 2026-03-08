"""
Vercel Python Function Entry Point
===================================
This file serves as the entry point for Vercel's Python runtime.
It properly configures the Flask app for Vercel's serverless environment.
"""

import os

# Get the project root directory (parent of api/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Import Flask app
from backend.app import app

# Reconfigure template and static folders for Vercel
# Vercel runs from the project root, so we need absolute paths
app.template_folder = os.path.join(PROJECT_ROOT, 'templates')
app.static_folder = os.path.join(PROJECT_ROOT, 'static')

# Ensure static URL path is correct
app.static_url_path = '/static'

# For Vercel, we need to export the app object
# The handler will be created automatically by Vercel's Python runtime

