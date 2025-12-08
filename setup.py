"""
ScribeEngine setup configuration for pip installation.
"""

from setuptools import setup, find_packages
import os

# Read version from scribe/__init__.py
version = {}
with open(os.path.join("scribe", "__init__.py")) as f:
    for line in f:
        if line.startswith("__version__"):
            exec(line, version)
            break

# Read long description from README if it exists
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="scribe-engine",
    version=version.get("__version__", "2.0.0-alpha"),
    author="ScribeEngine Team",
    author_email="",  # TBD
    description="A Python web framework where you write Python directly in templates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/scribe-engine",  # TBD
    packages=find_packages(exclude=["tests", "examples", "new-architecture"]),
    include_package_data=True,
    package_data={
        "scribe": [
            "templates/new_project/**/*",
            "templates/new_project/**/.gitkeep",
        ],
    },
    install_requires=[
        "Flask>=3.0.0,<4.0.0",
        "Jinja2>=3.1.0,<4.0.0",
        "Werkzeug>=3.0.0,<4.0.0",
        "Click>=8.1.0,<9.0.0",
        "Flask-WTF>=1.2.0,<2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0,<8.0.0",
            "pytest-flask>=1.3.0,<2.0.0",
            "pytest-cov>=4.1.0,<5.0.0",
        ],
        "postgresql": ["SQLAlchemy>=2.0.0,<3.0.0", "psycopg2-binary>=2.9.0"],
        "mysql": ["SQLAlchemy>=2.0.0,<3.0.0", "pymysql>=1.1.0"],
        "mssql": ["SQLAlchemy>=2.0.0,<3.0.0", "pymssql>=2.2.0"],
        "all_databases": [
            "SQLAlchemy>=2.0.0,<3.0.0",
            "psycopg2-binary>=2.9.0",
            "pymysql>=1.1.0",
            "pymssql>=2.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "scribe=scribe.cli:cli",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",  # TBD
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Flask",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    keywords="web framework flask templates python",
    project_urls={
        "Documentation": "https://scribe-engine.readthedocs.io",  # TBD
        "Source": "https://github.com/yourusername/scribe-engine",  # TBD
        "Tracker": "https://github.com/yourusername/scribe-engine/issues",  # TBD
    },
)
