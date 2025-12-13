"""
Database manager for handling multiple database connections.

Provides a unified interface for accessing multiple named database connections.
"""

from typing import Dict, Any, Optional
from scribe.database.base import DatabaseAdapter


class DatabaseManager:
    """
    Manages multiple named database connections.

    This class provides dictionary-style access to multiple database adapters
    while preventing direct method calls to avoid ambiguity.

    Usage:
        # Single database
        config = {'databases': {'default': {'type': 'sqlite', 'database': 'app.db'}}}
        db = DatabaseManager(config)
        users = db['default'].query("SELECT * FROM users")

        # Multiple databases
        config = {
            'databases': {
                'default': {'type': 'sqlite', 'database': 'app.db'},
                'analytics': {'type': 'postgresql', ...}
            }
        }
        db = DatabaseManager(config)
        users = db['default'].query("SELECT * FROM users")
        stats = db['analytics'].query("SELECT * FROM page_views")

    Note:
        Direct method calls like db.query() are intentionally disabled.
        Always use explicit connection names: db['name'].query()
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize database manager with configuration.

        Args:
            config: Configuration dict with 'databases' key containing named connections

        Example:
            config = {
                'databases': {
                    'default': {'type': 'sqlite', 'database': 'app.db'},
                    'analytics': {'type': 'postgresql', 'host': 'localhost', ...}
                }
            }
        """
        self._connections: Dict[str, DatabaseAdapter] = {}
        self._config = config

        # Handle backward compatibility with old 'database' key
        if 'database' in config and 'databases' not in config:
            print("Warning: Using deprecated 'database' config key. Use 'databases' with named connections instead.")
            print("  Old format: {\"database\": {...}}")
            print("  New format: {\"databases\": {\"default\": {...}}}")
            config['databases'] = {'default': config['database']}

        # Get databases config
        databases_config = config.get('databases', {})

        if not databases_config:
            raise ValueError("No databases configured. Add a 'databases' key to scribe.json")

        # Create adapter for each named connection
        # Import here to avoid circular dependency
        from scribe.database import create_adapter

        for name, db_config in databases_config.items():
            self._connections[name] = create_adapter(db_config)

        # Store connection names for helpful error messages
        self._connection_names = list(self._connections.keys())

    def __getitem__(self, name: str) -> DatabaseAdapter:
        """
        Get a database connection by name.

        Args:
            name: Connection name (e.g., 'default', 'analytics')

        Returns:
            DatabaseAdapter instance

        Raises:
            KeyError: If connection name not found

        Example:
            db['default'].query("SELECT * FROM users")
        """
        if name not in self._connections:
            available = ', '.join(f"'{n}'" for n in self._connection_names)
            raise KeyError(
                f"Database connection '{name}' not found.\n"
                f"Available connections: {available}\n"
                f"Check your scribe.json configuration."
            )

        return self._connections[name]

    def __contains__(self, name: str) -> bool:
        """Check if a connection name exists"""
        return name in self._connections

    def keys(self):
        """Get all connection names"""
        return self._connections.keys()

    def values(self):
        """Get all connection adapters"""
        return self._connections.values()

    def items(self):
        """Get all (name, adapter) pairs"""
        return self._connections.items()

    def get(self, name: str, default: Optional[DatabaseAdapter] = None) -> Optional[DatabaseAdapter]:
        """
        Get a connection by name with optional default.

        Args:
            name: Connection name
            default: Default value if not found

        Returns:
            DatabaseAdapter or default value
        """
        return self._connections.get(name, default)

    def close_all(self):
        """Close all database connections"""
        for adapter in self._connections.values():
            try:
                adapter.close()
            except Exception as e:
                print(f"Warning: Error closing database connection: {e}")

    # Prevent direct method calls - require explicit connection names
    def __getattr__(self, name: str):
        """
        Prevent direct method calls to avoid ambiguity.

        This ensures users must explicitly specify which database connection
        they want to use, even with a single database.

        Raises helpful error message directing to correct usage.
        """
        # Allow access to private attributes
        if name.startswith('_'):
            return object.__getattribute__(self, name)

        # For any other attribute access, raise helpful error
        connection_list = ', '.join(f"'{n}'" for n in self._connection_names)

        raise AttributeError(
            f"Cannot call db.{name}() directly.\n"
            f"Database connections must be accessed explicitly by name.\n"
            f"\n"
            f"Available connections: {connection_list}\n"
            f"\n"
            f"Use: db['default'].{name}(...)\n"
            f"Not: db.{name}(...)\n"
            f"\n"
            f"This ensures clarity when working with multiple databases."
        )

    def __repr__(self):
        """String representation showing available connections"""
        connections = ', '.join(f"'{name}'" for name in self._connection_names)
        return f"DatabaseManager({connections})"
