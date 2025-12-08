"""
ScribeEngine - A Python web framework where you write Python directly in templates.

Version: 2.0.0-alpha
Author: ScribeEngine Team
License: MIT (TBD)
"""

__version__ = "2.0.0-alpha"
__author__ = "ScribeEngine Team"

from scribe.app import create_app

__all__ = ["create_app", "__version__"]
