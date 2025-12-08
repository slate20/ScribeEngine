"""
Database migration system for ScribeEngine.

Applies SQL migration files from the migrations/ directory.
"""

from scribe.migrations.runner import run_migrations, create_migration

__all__ = ["run_migrations", "create_migration"]
