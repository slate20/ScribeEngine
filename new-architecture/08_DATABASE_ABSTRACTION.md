# Database Abstraction Layer

Complete specification for multi-database support in ScribeEngine.

---

## Overview

ScribeEngine provides a **unified database interface** that works across multiple database backends:
- SQLite (default, zero configuration)
- PostgreSQL
- MySQL
- Microsoft SQL Server

**Key principle:** Write once, run on any database.

---

## Architecture

```
┌──────────────────────────────────────────────┐
│         Template Code                        │
│  db.query("SELECT * FROM users WHERE id=?") │
└────────────────┬─────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────┐
│       DatabaseAdapter (Abstraction Layer)    │
│                                              │
│  • Unified API                               │
│  • Parameter normalization                   │
│  • Query building                            │
│  • Connection pooling                        │
└────────────────┬─────────────────────────────┘
                 │
     ┌───────────┴───────────┬──────────────┐
     │                       │              │
     ▼                       ▼              ▼
┌──────────┐          ┌──────────┐    ┌──────────┐
│  SQLite  │          │PostgreSQL│    │  MySQL   │
│  Driver  │          │  Driver  │    │  Driver  │
└──────────┘          └──────────┘    └──────────┘
     │                       │              │
     ▼                       ▼              ▼
┌──────────┐          ┌──────────┐    ┌──────────┐
│app.db    │          │PostgreSQL│    │  MySQL   │
│(file)    │          │  Server  │    │  Server  │
└──────────┘          └──────────┘    └──────────┘
```

---

## Database Adapter Interface

### **Core Class**

```python
class DatabaseAdapter:
    """Unified database interface for ScribeEngine"""

    def __init__(self, config):
        """
        Initialize database connection.

        Args:
            config (dict): Database configuration from scribe.json
                {
                    'type': 'sqlite'|'postgresql'|'mysql'|'mssql',
                    ... connection parameters ...
                }
        """
        self.config = config
        self.connection = None
        self.engine = None
        self.connect()

    def connect(self):
        """Establish database connection"""
        raise NotImplementedError

    def close(self):
        """Close database connection"""
        raise NotImplementedError

    # === Query Methods ===

    def query(self, sql, params=None):
        """
        Execute SELECT query and return results.

        Args:
            sql (str): SQL query with ? placeholders
            params (tuple): Parameter values

        Returns:
            list[Row]: Query results as list of Row objects
        """
        raise NotImplementedError

    def execute(self, sql, params=None):
        """
        Execute INSERT/UPDATE/DELETE query.

        Args:
            sql (str): SQL statement
            params (tuple): Parameter values

        Returns:
            int: Number of affected rows or last insert ID
        """
        raise NotImplementedError

    def commit(self):
        """Commit current transaction"""
        raise NotImplementedError

    def rollback(self):
        """Rollback current transaction"""
        raise NotImplementedError

    # === Convenience Methods ===

    def find(self, table, id):
        """Find record by primary key"""
        raise NotImplementedError

    def where(self, table, **conditions):
        """Find records matching conditions"""
        raise NotImplementedError

    def insert(self, table, **values):
        """Insert record and return new ID"""
        raise NotImplementedError

    def update(self, table, values, **conditions):
        """Update records matching conditions"""
        raise NotImplementedError

    def delete(self, table, **conditions):
        """Delete records matching conditions"""
        raise NotImplementedError

    # === Query Builder ===

    def table(self, name):
        """Get query builder for table"""
        return QueryBuilder(self, name)
```

---

## Row Object

Query results return **Row objects** (dict-like):

```python
class Row:
    """
    Database row that supports both dict and attribute access.

    Example:
        row['name']   # Dict access
        row.name      # Attribute access
    """

    def __init__(self, data):
        self._data = data

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __contains__(self, key):
        return key in self._data

    def __getattr__(self, key):
        if key.startswith('_'):
            return object.__getattribute__(self, key)
        return self._data[key]

    def __setattr__(self, key, value):
        if key.startswith('_'):
            object.__setattr__(self, key, value)
        else:
            self._data[key] = value

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __repr__(self):
        return f"Row({self._data})"

    def __iter__(self):
        return iter(self._data)

    def dict(self):
        """Convert to plain dict"""
        return dict(self._data)
```

**Usage:**
```python
{$
user = db.find('users', 1)

# Both work:
name1 = user['name']
name2 = user.name

# Dict methods:
'email' in user
user.keys()
user.get('bio', 'No bio')
$}
```

---

## SQLite Implementation

**Default database** - zero configuration required.

```python
import sqlite3
import os

class SQLiteAdapter(DatabaseAdapter):
    """SQLite database adapter"""

    def connect(self):
        """Connect to SQLite database file"""
        db_path = self.config.get('path', 'data/app.db')

        # Create directory if needed
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.connection = sqlite3.connect(
            db_path,
            check_same_thread=False,  # Allow multi-threaded access
            timeout=10.0  # Wait up to 10s for locks
        )

        # Return rows as dicts
        self.connection.row_factory = sqlite3.Row

        # Enable foreign keys
        self.connection.execute("PRAGMA foreign_keys = ON")

    def query(self, sql, params=None):
        """Execute SELECT query"""
        cursor = self.connection.cursor()
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        return [Row(dict(row)) for row in rows]

    def execute(self, sql, params=None):
        """Execute INSERT/UPDATE/DELETE"""
        cursor = self.connection.cursor()
        cursor.execute(sql, params or ())
        return cursor.lastrowid or cursor.rowcount

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        if self.connection:
            self.connection.close()
```

**Configuration (scribe.json):**
```json
{
  "database": {
    "type": "sqlite",
    "path": "data/app.db"
  }
}
```

---

## PostgreSQL Implementation

Uses **SQLAlchemy** for connection pooling and ORM integration.

```python
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool

class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL database adapter"""

    def connect(self):
        """Connect to PostgreSQL server"""
        config = self.config

        # Build connection string
        connection_string = (
            f"postgresql://{config['user']}:{config['password']}"
            f"@{config['host']}:{config.get('port', 5432)}"
            f"/{config['database']}"
        )

        # Create engine with connection pooling
        self.engine = create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Verify connections before use
            echo=config.get('debug', False)  # Log SQL queries
        )

        self.connection = self.engine.connect()

    def query(self, sql, params=None):
        """Execute SELECT query"""
        # Convert ? placeholders to PostgreSQL $1, $2, etc.
        sql_pg = self._convert_placeholders(sql)

        result = self.connection.execute(
            text(sql_pg),
            self._params_to_dict(params)
        )

        rows = result.fetchall()
        return [Row(dict(row._mapping)) for row in rows]

    def execute(self, sql, params=None):
        """Execute INSERT/UPDATE/DELETE"""
        sql_pg = self._convert_placeholders(sql)

        result = self.connection.execute(
            text(sql_pg),
            self._params_to_dict(params)
        )

        # Get last inserted ID or row count
        if 'INSERT' in sql.upper() and 'RETURNING' not in sql.upper():
            # PostgreSQL doesn't have lastrowid like SQLite
            # Use RETURNING clause
            return result.lastrowid if hasattr(result, 'lastrowid') else result.rowcount
        return result.rowcount

    def _convert_placeholders(self, sql):
        """Convert ? placeholders to :param1, :param2, etc."""
        parts = sql.split('?')
        if len(parts) == 1:
            return sql

        result = parts[0]
        for i in range(1, len(parts)):
            result += f":param{i}" + parts[i]
        return result

    def _params_to_dict(self, params):
        """Convert tuple of params to dict for SQLAlchemy"""
        if not params:
            return {}
        return {f"param{i+1}": val for i, val in enumerate(params)}

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()
```

**Configuration (scribe.json):**
```json
{
  "database": {
    "type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "myapp",
    "user": "postgres",
    "password": "secret",
    "debug": false
  }
}
```

---

## MySQL Implementation

```python
from sqlalchemy import create_engine, text

class MySQLAdapter(DatabaseAdapter):
    """MySQL database adapter"""

    def connect(self):
        """Connect to MySQL server"""
        config = self.config

        connection_string = (
            f"mysql+pymysql://{config['user']}:{config['password']}"
            f"@{config['host']}:{config.get('port', 3306)}"
            f"/{config['database']}"
            f"?charset=utf8mb4"
        )

        self.engine = create_engine(
            connection_string,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=config.get('debug', False)
        )

        self.connection = self.engine.connect()

    # query(), execute(), etc. similar to PostgreSQL
    # with MySQL-specific SQL dialect handling
```

**Configuration (scribe.json):**
```json
{
  "database": {
    "type": "mysql",
    "host": "localhost",
    "port": 3306,
    "database": "myapp",
    "user": "root",
    "password": "secret"
  }
}
```

---

## Convenience Methods Implementation

```python
class DatabaseAdapter:
    # ... (previous methods) ...

    def find(self, table, id):
        """
        Find record by primary key.

        Args:
            table (str): Table name
            id: Primary key value

        Returns:
            Row or None
        """
        sql = f"SELECT * FROM {table} WHERE id = ? LIMIT 1"
        results = self.query(sql, (id,))
        return results[0] if results else None

    def where(self, table, **conditions):
        """
        Find records matching conditions.

        Args:
            table (str): Table name
            **conditions: Column=value pairs

        Returns:
            list[Row]

        Example:
            db.where('users', active=True, role='admin')
            # SELECT * FROM users WHERE active = ? AND role = ?
        """
        if not conditions:
            return self.query(f"SELECT * FROM {table}")

        where_parts = []
        params = []
        for key, value in conditions.items():
            where_parts.append(f"{key} = ?")
            params.append(value)

        sql = f"SELECT * FROM {table} WHERE {' AND '.join(where_parts)}"
        return self.query(sql, tuple(params))

    def insert(self, table, **values):
        """
        Insert record.

        Args:
            table (str): Table name
            **values: Column=value pairs

        Returns:
            int: New record ID

        Example:
            user_id = db.insert('users', name='Alice', email='alice@example.com')
        """
        columns = list(values.keys())
        placeholders = ['?' for _ in columns]

        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        params = tuple(values.values())

        return self.execute(sql, params)

    def update(self, table, values, **conditions):
        """
        Update records.

        Args:
            table (str): Table name
            values (dict): Column=value pairs to set
            **conditions: WHERE conditions

        Returns:
            int: Number of affected rows

        Example:
            db.update('users', {'active': True}, id=123)
            # UPDATE users SET active = ? WHERE id = ?
        """
        set_parts = []
        params = []
        for key, value in values.items():
            set_parts.append(f"{key} = ?")
            params.append(value)

        sql = f"UPDATE {table} SET {', '.join(set_parts)}"

        if conditions:
            where_parts = []
            for key, value in conditions.items():
                where_parts.append(f"{key} = ?")
                params.append(value)
            sql += f" WHERE {' AND '.join(where_parts)}"

        return self.execute(sql, tuple(params))

    def delete(self, table, **conditions):
        """
        Delete records.

        Args:
            table (str): Table name
            **conditions: WHERE conditions

        Returns:
            int: Number of affected rows

        Example:
            db.delete('users', id=123)
            db.delete('posts', user_id=456, published=False)
        """
        if not conditions:
            raise ValueError("delete() requires at least one condition (safety check)")

        where_parts = []
        params = []
        for key, value in conditions.items():
            where_parts.append(f"{key} = ?")
            params.append(value)

        sql = f"DELETE FROM {table} WHERE {' AND '.join(where_parts)}"
        return self.execute(sql, tuple(params))
```

---

## Query Builder

Fluent interface for complex queries.

```python
class QueryBuilder:
    """Fluent query builder"""

    def __init__(self, db, table):
        self.db = db
        self.table_name = table
        self._select = ['*']
        self._where = []
        self._where_params = []
        self._order_by = []
        self._limit_value = None
        self._offset_value = None

    def select(self, *columns):
        """Specify columns to select"""
        self._select = list(columns)
        return self

    def where(self, **conditions):
        """Add WHERE conditions (AND)"""
        for key, value in conditions.items():
            self._where.append(f"{key} = ?")
            self._where_params.append(value)
        return self

    def where_in(self, column, values):
        """Add WHERE IN condition"""
        placeholders = ', '.join(['?' for _ in values])
        self._where.append(f"{column} IN ({placeholders})")
        self._where_params.extend(values)
        return self

    def where_like(self, column, pattern):
        """Add WHERE LIKE condition"""
        self._where.append(f"{column} LIKE ?")
        self._where_params.append(pattern)
        return self

    def order_by(self, column):
        """
        Add ORDER BY clause.

        Args:
            column (str): Column name or '-column' for DESC

        Example:
            .order_by('name')        # ASC
            .order_by('-created_at') # DESC
        """
        if column.startswith('-'):
            self._order_by.append(f"{column[1:]} DESC")
        else:
            self._order_by.append(f"{column} ASC")
        return self

    def limit(self, count):
        """Limit number of results"""
        self._limit_value = count
        return self

    def offset(self, count):
        """Skip number of results"""
        self._offset_value = count
        return self

    def all(self):
        """Execute and return all results"""
        sql = self._build_sql()
        return self.db.query(sql, tuple(self._where_params))

    def first(self):
        """Execute and return first result"""
        self.limit(1)
        results = self.all()
        return results[0] if results else None

    def count(self):
        """Count matching rows"""
        self._select = ['COUNT(*) as count']
        result = self.first()
        return result['count'] if result else 0

    def _build_sql(self):
        """Build final SQL query"""
        sql = f"SELECT {', '.join(self._select)} FROM {self.table_name}"

        if self._where:
            sql += f" WHERE {' AND '.join(self._where)}"

        if self._order_by:
            sql += f" ORDER BY {', '.join(self._order_by)}"

        if self._limit_value is not None:
            sql += f" LIMIT {self._limit_value}"

        if self._offset_value is not None:
            sql += f" OFFSET {self._offset_value}"

        return sql
```

**Usage examples:**
```python
{$
# Simple query
users = db.table('users').where(active=True).all()

# Complex query
posts = db.table('posts') \
    .select('id', 'title', 'created_at') \
    .where(published=True) \
    .where_in('category', ['tech', 'news']) \
    .order_by('-created_at') \
    .limit(10) \
    .all()

# Count
user_count = db.table('users').where(active=True).count()

# First result
admin = db.table('users').where(role='admin').first()

# Pagination
page = 2
per_page = 20
posts = db.table('posts') \
    .where(published=True) \
    .order_by('-created_at') \
    .limit(per_page) \
    .offset((page - 1) * per_page) \
    .all()
$}
```

---

## Database Factory

```python
def create_database_adapter(config):
    """
    Factory function to create appropriate database adapter.

    Args:
        config (dict): Database configuration

    Returns:
        DatabaseAdapter subclass instance
    """
    db_type = config.get('type', 'sqlite').lower()

    adapters = {
        'sqlite': SQLiteAdapter,
        'postgresql': PostgreSQLAdapter,
        'postgres': PostgreSQLAdapter,
        'mysql': MySQLAdapter,
        'mssql': MSSQLAdapter,
    }

    adapter_class = adapters.get(db_type)
    if not adapter_class:
        raise ValueError(f"Unsupported database type: {db_type}")

    return adapter_class(config)
```

---

## Usage in Templates

```python
@route('/users')
{$
# Raw SQL
users = db.query("SELECT * FROM users WHERE active = ?", (True,))

# Convenience methods
user = db.find('users', 123)
admins = db.where('users', role='admin')

# Insert
user_id = db.insert('users', name='Alice', email='alice@example.com')
db.commit()

# Update
db.update('users', {'last_login': datetime.now()}, id=user_id)
db.commit()

# Delete
db.delete('posts', id=456)
db.commit()

# Query builder
recent_posts = db.table('posts') \
    .where(published=True) \
    .order_by('-created_at') \
    .limit(10) \
    .all()
$}
```

---

## Transaction Support

```python
{$
try:
    # Begin implicit transaction
    user_id = db.insert('users', name='Alice', email='alice@example.com')
    db.insert('profiles', user_id=user_id, bio='Developer')

    # Commit on success
    db.commit()
except Exception as e:
    # Rollback on error
    db.rollback()
    error = str(e)
$}
```

---

## Next: Flask Integration

See [10_FLASK_INTEGRATION.md](10_FLASK_INTEGRATION.md) for how the database adapter integrates with Flask routes.
