"""
Scribe Engine Version Information

This module contains the current version of the Scribe Engine.
It serves as the definitive source of version information that persists
regardless of executable naming or other external factors.

This file is automatically updated during the build process and should
be the primary source of truth for version checking.
"""

# Current version of Scribe Engine
__version__ = "1.3.2"

# Version metadata
VERSION_INFO = {
    "major": 1,
    "minor": 3,
    "patch": 2,
    "version": "1.3.2",
    "build_date": None,
    "commit_hash": None,
}

def get_version() -> str:
    """
    Get the current version string.

    Returns:
        Version string in format "major.minor.patch"
    """
    return __version__

def get_version_info() -> dict:
    """
    Get detailed version information.

    Returns:
        Dictionary containing version components and metadata
    """
    return VERSION_INFO.copy()

def set_version(version: str):
    """
    Set the current version (used during build process).

    Args:
        version: Version string in format "major.minor.patch"
    """
    global __version__, VERSION_INFO
    __version__ = version
    parts = version.split('.')
    if len(parts) >= 3:
        VERSION_INFO.update({
            "major": int(parts[0]),
            "minor": int(parts[1]),
            "patch": int(parts[2]),
            "version": version
        })

def set_build_metadata(build_date: str = None, commit_hash: str = None):
    """
    Set build metadata (used during build process).

    Args:
        build_date: ISO format date string
        commit_hash: Git commit hash
    """
    global VERSION_INFO
    if build_date:
        VERSION_INFO["build_date"] = build_date
    if commit_hash:
        VERSION_INFO["commit_hash"] = commit_hash