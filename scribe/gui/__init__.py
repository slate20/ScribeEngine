"""
ScribeEngine GUI IDE Module

This module provides a web-based integrated development environment (IDE)
for developing ScribeEngine applications. It includes:
- Code editor with .stpl syntax highlighting (Monaco Editor)
- Live preview panel for real-time template rendering
- Database browser for visual DB exploration
- File management UI
- Route explorer

The GUI is designed to run on localhost only by default for security.
"""

from flask import Blueprint

# Create the GUI blueprint
gui_bp = Blueprint(
    'gui',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/__scribe_gui'
)

# Import routes after blueprint creation to avoid circular imports
from scribe.gui import routes

__all__ = ['gui_bp']
