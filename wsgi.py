"""
WSGI entry point for production deployment

This module provides the WSGI application callable for production servers
like Gunicorn, uWSGI, or Waitress.

Usage with Gunicorn:
    export SCRIBE_ENV=production
    export SCRIBE_PROJECT_PATH=/var/www/myapp
    export SCRIBE_SECRET_KEY=your-secret-key-here
    gunicorn -w 4 -b 0.0.0.0:8000 wsgi:application

Usage with Waitress (Windows-compatible):
    waitress-serve --port=8000 wsgi:application

Usage with uWSGI:
    uwsgi --http :8000 --wsgi-file wsgi.py --callable application
"""

import os
import sys

# Ensure Scribe Engine directory is in Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import app, set_game_project_path, set_debug_mode
from config import Config, generate_secret_key

# Validate production requirements
if Config.is_production():
    is_valid, error_message = Config.validate_production()
    if not is_valid:
        raise ValueError(f"Production validation failed: {error_message}")

    # Set production secret key
    secret_key = Config.get_secret_key()
    if secret_key:
        app.secret_key = secret_key
    else:
        raise ValueError("SCRIBE_SECRET_KEY must be set in production mode")

    # Disable debug mode in production
    set_debug_mode(False)
    app.debug = False

else:
    # Development mode - use generated secret key
    if not app.secret_key or app.secret_key == 'your-secret-key-here':
        app.secret_key = generate_secret_key()

# Set project path from environment
project_path = Config.get_project_path()
if project_path:
    set_game_project_path(project_path)
    print(f"✓ Loaded project: {project_path}")
else:
    print("⚠ Warning: SCRIBE_PROJECT_PATH not set")

# Print configuration in development mode
if Config.is_development():
    Config.print_config()

# WSGI application callable
application = app

# For backwards compatibility
app = application
