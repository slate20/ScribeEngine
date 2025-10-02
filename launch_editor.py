#!/usr/bin/env python3
"""
Launcher script for Scribe Engine V2 Native Editor.
Shows startup screen for creating/opening projects.
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import and run launcher
from v2_engine.editor.launcher import main

if __name__ == '__main__':
    main()
