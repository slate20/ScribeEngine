"""
Database abstraction layer for ScribeEngine.

Provides a unified interface across SQLite, PostgreSQL, MySQL, and MSSQL.
"""

from scribe.database.base import DatabaseAdapter, Row
from scribe.database.sqlite import SQLiteAdapter
from scribe.database.query_builder import QueryBuilder
from scribe.database.manager import DatabaseManager


def create_adapter(config: dict) -> DatabaseAdapter:
    """
    Create a database adapter based on configuration.

    Args:
        config: Database configuration dict
            {
                'type': 'sqlite'|'postgresql'|'mysql'|'mssql',
                'database': 'path/to/db.sqlite' or database name,
                ... other connection parameters ...
            }

    Returns:
        Appropriate DatabaseAdapter instance

    Example:
        config = {'type': 'sqlite', 'database': 'app.db'}
        db = create_adapter(config)
        users = db.query("SELECT * FROM users")
    """
    db_type = config.get('type', 'sqlite').lower()

    if db_type == 'sqlite':
        return SQLiteAdapter(config)
    elif db_type == 'postgresql':
        from scribe.database.postgresql import PostgreSQLAdapter
        return PostgreSQLAdapter(config)
    elif db_type == 'mysql':
        from scribe.database.mysql import MySQLAdapter
        return MySQLAdapter(config)
    elif db_type == 'mssql':
        from scribe.database.mssql import MSSQLAdapter
        return MSSQLAdapter(config)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


__all__ = [
    "DatabaseAdapter",
    "Row",
    "SQLiteAdapter",
    "QueryBuilder",
    "DatabaseManager",
    "create_adapter",
]
