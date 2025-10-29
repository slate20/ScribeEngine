"""
SQLite database module for Scribe Framework

Provides thread-safe database access with a simple query interface and fluent query builder.
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional, Tuple
from threading import Lock


class Database:
    """Thread-safe SQLite wrapper for Scribe Framework"""

    def __init__(self, project_path: str, config: Dict[str, Any]):
        """
        Initialize database connection.

        Args:
            project_path: Path to the project directory
            config: Project configuration dictionary
        """
        db_config = config.get('database', {})
        db_path = db_config.get('path', 'data/app.db')
        self.db_path = os.path.join(project_path, db_path)

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # Create connection with Row factory for dict-like access
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        # Thread safety lock
        self.lock = Lock()

        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")

    def query(self, sql: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as list of dictionaries.

        Args:
            sql: SQL query string
            params: Query parameters (use ? placeholders)

        Returns:
            List of dictionaries with column names as keys

        Example:
            users = db.query("SELECT * FROM users WHERE active = ?", (True,))
        """
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

    def execute(self, sql: str, params: Tuple = ()) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.

        Args:
            sql: SQL query string
            params: Query parameters (use ? placeholders)

        Returns:
            Last inserted row ID (for INSERT) or number of affected rows

        Example:
            user_id = db.execute("INSERT INTO users (name, email) VALUES (?, ?)",
                                ("Alice", "alice@example.com"))
        """
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            self.conn.commit()
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

    def execute_many(self, sql: str, params_list: List[Tuple]) -> int:
        """
        Execute the same query multiple times with different parameters.

        Args:
            sql: SQL query string
            params_list: List of parameter tuples

        Returns:
            Number of affected rows

        Example:
            db.execute_many("INSERT INTO users (name) VALUES (?)",
                          [("Alice",), ("Bob",), ("Charlie",)])
        """
        with self.lock:
            cursor = self.conn.cursor()
            cursor.executemany(sql, params_list)
            self.conn.commit()
            return cursor.rowcount

    def table(self, name: str) -> 'QueryBuilder':
        """
        Get a query builder for the specified table.

        Args:
            name: Table name

        Returns:
            QueryBuilder instance for fluent queries

        Example:
            users = db.table('users').where(active=True).order_by('name').all()
        """
        return QueryBuilder(self, name)

    def transaction(self):
        """
        Context manager for database transactions.

        Example:
            with db.transaction():
                db.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
                db.execute("INSERT INTO posts (author) VALUES (?)", ("Alice",))
        """
        return TransactionContext(self)

    def close(self):
        """Close the database connection."""
        self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class QueryBuilder:
    """Fluent query builder for simplified database queries"""

    def __init__(self, db: Database, table_name: str):
        """
        Initialize query builder.

        Args:
            db: Database instance
            table_name: Name of the table to query
        """
        self.db = db
        self.table_name = table_name
        self._select_cols = ['*']
        self._where_conditions = {}
        self._where_sql = None
        self._where_params = None
        self._order = None
        self._limit_val = None
        self._offset_val = None
        self._join_clauses = []

    def select(self, *columns: str) -> 'QueryBuilder':
        """
        Specify columns to select.

        Args:
            *columns: Column names to select

        Returns:
            Self for chaining

        Example:
            db.table('users').select('id', 'name', 'email').all()
        """
        self._select_cols = list(columns)
        return self

    def where(self, **conditions) -> 'QueryBuilder':
        """
        Add WHERE conditions using keyword arguments.

        Args:
            **conditions: Column-value pairs for equality conditions

        Returns:
            Self for chaining

        Example:
            db.table('users').where(active=True, role='admin').all()
        """
        self._where_conditions.update(conditions)
        return self

    def where_raw(self, sql: str, params: Tuple = ()) -> 'QueryBuilder':
        """
        Add raw WHERE clause for complex conditions.

        Args:
            sql: Raw SQL WHERE clause (without the WHERE keyword)
            params: Parameters for the SQL clause

        Returns:
            Self for chaining

        Example:
            db.table('users').where_raw("age > ? AND status = ?", (18, 'active')).all()
        """
        self._where_sql = sql
        self._where_params = params
        return self

    def order_by(self, column: str, direction: str = 'ASC') -> 'QueryBuilder':
        """
        Add ORDER BY clause.

        Args:
            column: Column name to order by
            direction: 'ASC' or 'DESC'

        Returns:
            Self for chaining

        Example:
            db.table('users').order_by('created_at', 'DESC').all()
        """
        self._order = (column, direction.upper())
        return self

    def limit(self, n: int) -> 'QueryBuilder':
        """
        Add LIMIT clause.

        Args:
            n: Maximum number of results

        Returns:
            Self for chaining

        Example:
            db.table('users').limit(10).all()
        """
        self._limit_val = n
        return self

    def offset(self, n: int) -> 'QueryBuilder':
        """
        Add OFFSET clause (use with limit for pagination).

        Args:
            n: Number of results to skip

        Returns:
            Self for chaining

        Example:
            db.table('users').limit(10).offset(20).all()  # Page 3
        """
        self._offset_val = n
        return self

    def join(self, table: str, on: str) -> 'QueryBuilder':
        """
        Add INNER JOIN clause.

        Args:
            table: Table name to join
            on: JOIN condition

        Returns:
            Self for chaining

        Example:
            db.table('posts').join('users', 'posts.user_id = users.id').all()
        """
        self._join_clauses.append(f"INNER JOIN {table} ON {on}")
        return self

    def left_join(self, table: str, on: str) -> 'QueryBuilder':
        """
        Add LEFT JOIN clause.

        Args:
            table: Table name to join
            on: JOIN condition

        Returns:
            Self for chaining
        """
        self._join_clauses.append(f"LEFT JOIN {table} ON {on}")
        return self

    def all(self) -> List[Dict[str, Any]]:
        """
        Execute query and return all results.

        Returns:
            List of dictionaries with query results

        Example:
            users = db.table('users').where(active=True).all()
        """
        sql, params = self._build_query()
        return self.db.query(sql, params)

    def first(self) -> Optional[Dict[str, Any]]:
        """
        Execute query and return first result.

        Returns:
            Dictionary with first result or None if no results

        Example:
            user = db.table('users').where(email='alice@example.com').first()
        """
        results = self.limit(1).all()
        return results[0] if results else None

    def get(self) -> List[Dict[str, Any]]:
        """Alias for all() for better readability."""
        return self.all()

    def count(self) -> int:
        """
        Get count of matching records.

        Returns:
            Number of matching records

        Example:
            user_count = db.table('users').where(active=True).count()
        """
        # Save current select columns and replace with COUNT(*)
        original_cols = self._select_cols
        self._select_cols = ['COUNT(*) as count']

        sql, params = self._build_query()
        result = self.db.query(sql, params)

        # Restore original columns
        self._select_cols = original_cols

        return result[0]['count'] if result else 0

    def exists(self) -> bool:
        """
        Check if any matching records exist.

        Returns:
            True if at least one record exists, False otherwise

        Example:
            has_admins = db.table('users').where(role='admin').exists()
        """
        return self.count() > 0

    def _build_query(self) -> Tuple[str, Tuple]:
        """
        Build the final SQL query and parameters.

        Returns:
            Tuple of (sql_string, parameters_tuple)
        """
        # SELECT clause
        cols = ', '.join(self._select_cols)
        sql = f"SELECT {cols} FROM {self.table_name}"

        # JOIN clauses
        if self._join_clauses:
            sql += " " + " ".join(self._join_clauses)

        # WHERE clause
        params = []
        where_parts = []

        # Add simple conditions
        if self._where_conditions:
            for key, value in self._where_conditions.items():
                where_parts.append(f"{key} = ?")
                params.append(value)

        # Add raw SQL conditions
        if self._where_sql:
            where_parts.append(self._where_sql)
            if self._where_params:
                params.extend(self._where_params)

        if where_parts:
            sql += " WHERE " + " AND ".join(where_parts)

        # ORDER BY clause
        if self._order:
            sql += f" ORDER BY {self._order[0]} {self._order[1]}"

        # LIMIT clause
        if self._limit_val is not None:
            sql += f" LIMIT {self._limit_val}"

        # OFFSET clause
        if self._offset_val is not None:
            sql += f" OFFSET {self._offset_val}"

        return sql, tuple(params)


class TransactionContext:
    """Context manager for database transactions"""

    def __init__(self, db: Database):
        self.db = db

    def __enter__(self):
        """Begin transaction."""
        self.db.conn.execute("BEGIN TRANSACTION")
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Commit or rollback transaction based on exceptions."""
        if exc_type is None:
            # No exception - commit
            self.db.conn.commit()
        else:
            # Exception occurred - rollback
            self.db.conn.rollback()
        return False  # Don't suppress exceptions
