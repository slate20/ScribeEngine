"""
Microsoft SQL Server database adapter implementation.
"""

import pymssql
from typing import List, Optional, Dict, Any, Union
from scribe.database.base import DatabaseAdapter, Row


class MSSQLAdapter(DatabaseAdapter):
    """
    Microsoft SQL Server implementation of DatabaseAdapter.

    Configuration:
        {
            'type': 'mssql',
            'host': 'localhost',
            'port': 1433,
            'user': 'username',
            'password': 'password',
            'database': 'dbname'
        }

    Example:
        config = {
            'type': 'mssql',
            'host': 'localhost',
            'port': 1433,
            'user': 'sa',
            'password': 'MyPassword123',
            'database': 'mydb'
        }
        db = MSSQLAdapter(config)
        users = db.query("SELECT * FROM users")
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.connect()

    def connect(self):
        """Establish MSSQL connection"""
        # Extract connection parameters
        host = self.config.get('host', 'localhost')
        port = self.config.get('port', 1433)
        user = self.config.get('user')
        password = self.config.get('password')
        database = self.config.get('database')

        if not user or not database:
            raise ValueError("MSSQL requires 'user' and 'database' in config")

        # Connect using pymssql
        self.connection = pymssql.connect(
            server=host,
            port=port,
            user=user,
            password=password,
            database=database,
            as_dict=True  # Return rows as dictionaries
        )
        self.connection.autocommit(False)  # Manual transaction control

    def close(self):
        """Close MSSQL connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def _convert_placeholders(self, sql: str) -> str:
        """
        Convert SQLite-style ? placeholders to MSSQL %s placeholders.

        Args:
            sql: SQL query with ? placeholders

        Returns:
            SQL query with %s placeholders
        """
        return sql.replace('?', '%s')

    def query(self, sql: str, params: Optional[tuple] = None) -> List[Row]:
        """
        Execute SELECT query and return results.

        Args:
            sql: SQL query with ? placeholders (will be converted to %s)
            params: Parameter values

        Returns:
            List of Row objects
        """
        # Convert placeholders
        sql = self._convert_placeholders(sql)

        cursor = self.connection.cursor(as_dict=True)

        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            # Fetch all rows and convert to Row objects
            rows = []
            for row_data in cursor.fetchall():
                rows.append(Row(dict(row_data)))

            return rows
        finally:
            cursor.close()

    def execute(self, sql: str, params: Optional[tuple] = None) -> int:
        """
        Execute INSERT/UPDATE/DELETE query.

        Args:
            sql: SQL statement with ? placeholders (will be converted to %s)
            params: Parameter values

        Returns:
            Number of affected rows or last insert ID (for INSERT)
        """
        # Convert placeholders
        sql = self._convert_placeholders(sql)

        cursor = self.connection.cursor()

        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            # For INSERT, try to get the last inserted ID using SCOPE_IDENTITY()
            if sql.strip().upper().startswith('INSERT'):
                cursor.execute("SELECT SCOPE_IDENTITY() as id")
                result = cursor.fetchone()
                if result and result.get('id'):
                    return int(result['id'])
                return cursor.rowcount
            else:
                # For UPDATE/DELETE, return number of affected rows
                return cursor.rowcount
        finally:
            cursor.close()

    def commit(self):
        """Commit current transaction"""
        if self.connection:
            self.connection.commit()

    def rollback(self):
        """Rollback current transaction"""
        if self.connection:
            self.connection.rollback()

    def find(self, table: str, id: Union[int, str]) -> Optional[Row]:
        """
        Find record by primary key (assumed to be 'id').

        Args:
            table: Table name
            id: Primary key value

        Returns:
            Row object or None if not found
        """
        sql = f"SELECT * FROM {table} WHERE id = %s"

        cursor = self.connection.cursor(as_dict=True)

        try:
            cursor.execute(sql, (id,))
            row_data = cursor.fetchone()

            if row_data:
                return Row(dict(row_data))
            return None
        finally:
            cursor.close()

    def where(self, table: str, **conditions) -> List[Row]:
        """
        Find records matching conditions.

        Args:
            table: Table name
            **conditions: Column=value conditions (AND-ed together)

        Returns:
            List of Row objects
        """
        if not conditions:
            # No conditions, return all rows
            return self.query(f"SELECT * FROM {table}")

        # Build WHERE clause
        where_parts = []
        params = []
        for column, value in conditions.items():
            where_parts.append(f"{column} = %s")
            params.append(value)

        where_clause = " AND ".join(where_parts)
        sql = f"SELECT * FROM {table} WHERE {where_clause}"

        cursor = self.connection.cursor(as_dict=True)

        try:
            cursor.execute(sql, tuple(params))

            rows = []
            for row_data in cursor.fetchall():
                rows.append(Row(dict(row_data)))

            return rows
        finally:
            cursor.close()

    def insert(self, table: str, **values) -> int:
        """
        Insert record and return new ID.

        Args:
            table: Table name
            **values: Column=value pairs

        Returns:
            Last insert ID
        """
        if not values:
            raise ValueError("Cannot insert empty record")

        columns = list(values.keys())
        placeholders = ['%s' for _ in columns]
        params = [values[col] for col in columns]

        columns_str = ', '.join(columns)
        placeholders_str = ', '.join(placeholders)

        # Insert and get ID using OUTPUT clause (MSSQL-specific)
        sql = f"INSERT INTO {table} ({columns_str}) OUTPUT INSERTED.id VALUES ({placeholders_str})"

        cursor = self.connection.cursor()

        try:
            cursor.execute(sql, tuple(params))
            result = cursor.fetchone()
            if result:
                # OUTPUT INSERTED.id returns a dict with 'id' key
                return result.get('id', 0) if isinstance(result, dict) else result[0]
            return 0
        except Exception as e:
            # Fallback: try without OUTPUT clause and use SCOPE_IDENTITY()
            sql_fallback = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders_str})"
            cursor.execute(sql_fallback, tuple(params))
            cursor.execute("SELECT SCOPE_IDENTITY() as id")
            result = cursor.fetchone()
            if result:
                return int(result.get('id', 0))
            return 0
        finally:
            cursor.close()

    def update(self, table: str, values: Dict[str, Any], **conditions) -> int:
        """
        Update records matching conditions.

        Args:
            table: Table name
            values: Dict of column=value pairs to update
            **conditions: WHERE conditions (AND-ed together)

        Returns:
            Number of affected rows
        """
        if not values:
            raise ValueError("Cannot update with empty values")

        # Build SET clause
        set_parts = []
        params = []
        for column, value in values.items():
            set_parts.append(f"{column} = %s")
            params.append(value)

        set_clause = ", ".join(set_parts)

        # Build WHERE clause
        if conditions:
            where_parts = []
            for column, value in conditions.items():
                where_parts.append(f"{column} = %s")
                params.append(value)
            where_clause = " WHERE " + " AND ".join(where_parts)
        else:
            where_clause = ""

        sql = f"UPDATE {table} SET {set_clause}{where_clause}"

        cursor = self.connection.cursor()

        try:
            cursor.execute(sql, tuple(params))
            return cursor.rowcount
        finally:
            cursor.close()

    def delete(self, table: str, **conditions) -> int:
        """
        Delete records matching conditions.

        Args:
            table: Table name
            **conditions: WHERE conditions (AND-ed together)

        Returns:
            Number of deleted rows
        """
        if not conditions:
            raise ValueError("Delete requires at least one condition (use 'DELETE FROM table' directly if you really want to delete all rows)")

        # Build WHERE clause
        where_parts = []
        params = []
        for column, value in conditions.items():
            where_parts.append(f"{column} = %s")
            params.append(value)

        where_clause = " AND ".join(where_parts)
        sql = f"DELETE FROM {table} WHERE {where_clause}"

        cursor = self.connection.cursor()

        try:
            cursor.execute(sql, tuple(params))
            return cursor.rowcount
        finally:
            cursor.close()
