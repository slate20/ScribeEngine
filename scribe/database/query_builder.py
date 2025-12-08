"""
Fluent query builder interface for ScribeEngine.

Provides chainable methods for building database queries.
"""

from typing import List, Optional, Any, Dict, Union
from scribe.database.base import Row


class QueryBuilder:
    """
    Fluent query builder for database operations.

    Example:
        posts = db.table('posts')
            .where(published=True)
            .where(user_id=123)
            .order_by('-created_at')
            .limit(10)
            .all()
    """

    def __init__(self, adapter, table_name: str):
        """
        Initialize query builder.

        Args:
            adapter: DatabaseAdapter instance
            table_name: Name of the table to query
        """
        self.adapter = adapter
        self.table_name = table_name

        # Query components
        self._where_conditions: List[tuple] = []  # List of (column, operator, value)
        self._order_by_clauses: List[tuple] = []  # List of (column, direction)
        self._limit_value: Optional[int] = None
        self._offset_value: Optional[int] = None
        self._select_columns: List[str] = ['*']

    def select(self, *columns: str) -> 'QueryBuilder':
        """
        Specify columns to select.

        Args:
            *columns: Column names

        Returns:
            Self for chaining

        Example:
            db.table('users').select('id', 'username', 'email').all()
        """
        self._select_columns = list(columns) if columns else ['*']
        return self

    def where(self, **conditions) -> 'QueryBuilder':
        """
        Add WHERE conditions (AND-ed together).

        Args:
            **conditions: Column=value conditions

        Returns:
            Self for chaining

        Example:
            db.table('posts').where(published=True, user_id=123)
        """
        for column, value in conditions.items():
            self._where_conditions.append((column, '=', value))
        return self

    def where_not(self, **conditions) -> 'QueryBuilder':
        """
        Add WHERE NOT conditions.

        Args:
            **conditions: Column=value conditions

        Returns:
            Self for chaining

        Example:
            db.table('users').where_not(deleted=True)
        """
        for column, value in conditions.items():
            self._where_conditions.append((column, '!=', value))
        return self

    def where_in(self, column: str, values: List[Any]) -> 'QueryBuilder':
        """
        Add WHERE IN condition.

        Args:
            column: Column name
            values: List of values

        Returns:
            Self for chaining

        Example:
            db.table('posts').where_in('status', ['published', 'draft'])
        """
        self._where_conditions.append((column, 'IN', values))
        return self

    def where_like(self, column: str, pattern: str) -> 'QueryBuilder':
        """
        Add WHERE LIKE condition.

        Args:
            column: Column name
            pattern: LIKE pattern (use % for wildcards)

        Returns:
            Self for chaining

        Example:
            db.table('users').where_like('email', '%@example.com')
        """
        self._where_conditions.append((column, 'LIKE', pattern))
        return self

    def where_gt(self, column: str, value: Any) -> 'QueryBuilder':
        """Add WHERE column > value condition."""
        self._where_conditions.append((column, '>', value))
        return self

    def where_gte(self, column: str, value: Any) -> 'QueryBuilder':
        """Add WHERE column >= value condition."""
        self._where_conditions.append((column, '>=', value))
        return self

    def where_lt(self, column: str, value: Any) -> 'QueryBuilder':
        """Add WHERE column < value condition."""
        self._where_conditions.append((column, '<', value))
        return self

    def where_lte(self, column: str, value: Any) -> 'QueryBuilder':
        """Add WHERE column <= value condition."""
        self._where_conditions.append((column, '<=', value))
        return self

    def order_by(self, *columns: str) -> 'QueryBuilder':
        """
        Add ORDER BY clause.

        Args:
            *columns: Column names (prefix with '-' for DESC)

        Returns:
            Self for chaining

        Example:
            db.table('posts').order_by('-created_at', 'title')
            # ORDER BY created_at DESC, title ASC
        """
        for column in columns:
            if column.startswith('-'):
                # Descending order
                self._order_by_clauses.append((column[1:], 'DESC'))
            else:
                # Ascending order
                self._order_by_clauses.append((column, 'ASC'))
        return self

    def limit(self, count: int) -> 'QueryBuilder':
        """
        Add LIMIT clause.

        Args:
            count: Maximum number of rows to return

        Returns:
            Self for chaining

        Example:
            db.table('posts').limit(10)
        """
        self._limit_value = count
        return self

    def offset(self, count: int) -> 'QueryBuilder':
        """
        Add OFFSET clause.

        Args:
            count: Number of rows to skip

        Returns:
            Self for chaining

        Example:
            db.table('posts').limit(10).offset(20)  # Page 3
        """
        self._offset_value = count
        return self

    def _build_query(self) -> tuple[str, tuple]:
        """
        Build the SQL query and parameters.

        Returns:
            Tuple of (sql_string, params_tuple)
        """
        # SELECT clause
        columns_str = ', '.join(self._select_columns)
        sql = f"SELECT {columns_str} FROM {self.table_name}"

        params = []

        # WHERE clause
        if self._where_conditions:
            where_parts = []
            for column, operator, value in self._where_conditions:
                if operator == 'IN':
                    # Handle IN operator specially
                    placeholders = ', '.join(['?' for _ in value])
                    where_parts.append(f"{column} IN ({placeholders})")
                    params.extend(value)
                else:
                    where_parts.append(f"{column} {operator} ?")
                    params.append(value)

            sql += " WHERE " + " AND ".join(where_parts)

        # ORDER BY clause
        if self._order_by_clauses:
            order_parts = [f"{column} {direction}" for column, direction in self._order_by_clauses]
            sql += " ORDER BY " + ", ".join(order_parts)

        # LIMIT clause
        if self._limit_value is not None:
            sql += f" LIMIT {self._limit_value}"

        # OFFSET clause
        if self._offset_value is not None:
            sql += f" OFFSET {self._offset_value}"

        return sql, tuple(params)

    def all(self) -> List[Row]:
        """
        Execute query and return all results.

        Returns:
            List of Row objects

        Example:
            posts = db.table('posts').where(published=True).all()
        """
        sql, params = self._build_query()
        return self.adapter.query(sql, params)

    def first(self) -> Optional[Row]:
        """
        Execute query and return first result.

        Returns:
            Row object or None if no results

        Example:
            post = db.table('posts').where(id=123).first()
        """
        # Add LIMIT 1 if not already set
        original_limit = self._limit_value
        self._limit_value = 1

        sql, params = self._build_query()
        results = self.adapter.query(sql, params)

        # Restore original limit
        self._limit_value = original_limit

        return results[0] if results else None

    def count(self) -> int:
        """
        Count rows matching the query.

        Returns:
            Number of rows

        Example:
            total_posts = db.table('posts').where(published=True).count()
        """
        # Save original select columns
        original_select = self._select_columns

        # Change to COUNT(*)
        self._select_columns = ['COUNT(*) as count']

        sql, params = self._build_query()
        results = self.adapter.query(sql, params)

        # Restore original select
        self._select_columns = original_select

        return results[0]['count'] if results else 0

    def exists(self) -> bool:
        """
        Check if any rows match the query.

        Returns:
            True if at least one row exists

        Example:
            if db.table('users').where(email=email).exists():
                print("Email already taken")
        """
        return self.count() > 0

    def pluck(self, column: str) -> List[Any]:
        """
        Get a list of values from a single column.

        Args:
            column: Column name

        Returns:
            List of values

        Example:
            user_ids = db.table('posts').where(published=True).pluck('user_id')
        """
        # Save original select columns
        original_select = self._select_columns

        # Change to single column
        self._select_columns = [column]

        sql, params = self._build_query()
        results = self.adapter.query(sql, params)

        # Restore original select
        self._select_columns = original_select

        return [row[column] for row in results]
