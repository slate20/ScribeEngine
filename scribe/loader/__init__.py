"""
Module auto-loader for ScribeEngine.

Automatically loads all Python modules from the project's lib/ directory
and makes them available in templates.
"""

from scribe.loader.module_loader import load_helper_modules

__all__ = ["load_helper_modules"]
