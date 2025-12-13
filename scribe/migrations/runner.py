"""
Migration runner for applying database schema changes.

Migrations are SQL files in the migrations/ directory, executed in order.
"""

import os
import glob
from typing import List, Union
from scribe.database.base import DatabaseAdapter


def run_migrations(db: Union[DatabaseAdapter, 'DatabaseManager'], project_path: str):
    """
    Run all pending database migrations.

    Args:
        db: DatabaseAdapter or DatabaseManager instance
        project_path: Path to the project directory

    Note:
        If a DatabaseManager is passed, migrations run on the 'default' connection.

    Migration files:
        migrations/
        ├── 001_create_users.sql
        ├── 002_create_posts.sql
        └── 003_add_user_roles.sql

    Files are executed in alphabetical order. Already-applied migrations
    are tracked in the _migrations table.

    Example migration file (001_create_users.sql):
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    # If DatabaseManager is passed, use the 'default' connection
    from scribe.database.manager import DatabaseManager
    if isinstance(db, DatabaseManager):
        if 'default' not in db:
            print("Warning: No 'default' database connection found. Skipping migrations.")
            return
        db = db['default']

    migrations_path = os.path.join(project_path, 'migrations')

    # If migrations/ directory doesn't exist, nothing to do
    if not os.path.exists(migrations_path):
        print("No migrations/ directory found")
        return

    # Create migrations tracking table if it doesn't exist
    _create_migrations_table(db)

    # Get list of migration files
    migration_files = glob.glob(os.path.join(migrations_path, '*.sql'))
    migration_files.sort()  # Execute in alphabetical order

    if not migration_files:
        print("No migration files found")
        return

    # Get list of already-applied migrations
    applied_migrations = _get_applied_migrations(db)

    # Run each migration
    applied_count = 0
    for filepath in migration_files:
        filename = os.path.basename(filepath)

        # Skip if already applied
        if filename in applied_migrations:
            continue

        print(f"  Running migration: {filename}")

        try:
            # Read migration SQL
            with open(filepath, 'r', encoding='utf-8') as f:
                sql = f.read()

            # Split into individual statements (separated by semicolons)
            statements = _split_sql_statements(sql)

            # Execute each statement
            for statement in statements:
                statement = statement.strip()
                if statement:
                    db.execute(statement)

            # Record that this migration was applied
            _record_migration(db, filename)

            db.commit()
            applied_count += 1

            print(f"    ✓ Applied {filename}")

        except Exception as e:
            db.rollback()
            print(f"    ✗ Error applying {filename}: {e}")
            raise

    if applied_count > 0:
        print(f"\n✓ Applied {applied_count} migration(s)")
    else:
        print("\n✓ All migrations up to date")


def _create_migrations_table(db: DatabaseAdapter):
    """Create the _migrations table to track applied migrations."""
    sql = """
    CREATE TABLE IF NOT EXISTS _migrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT UNIQUE NOT NULL,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    db.execute(sql)
    db.commit()


def _get_applied_migrations(db: DatabaseAdapter) -> List[str]:
    """Get list of already-applied migration filenames."""
    try:
        results = db.query("SELECT filename FROM _migrations ORDER BY applied_at")
        return [row['filename'] for row in results]
    except:
        # Table might not exist yet
        return []


def _record_migration(db: DatabaseAdapter, filename: str):
    """Record that a migration has been applied."""
    db.execute("INSERT INTO _migrations (filename) VALUES (?)", (filename,))


def _split_sql_statements(sql: str) -> List[str]:
    """
    Split SQL file into individual statements.

    Handles:
        - Semicolon-separated statements
        - Comments (-- and /* */)
        - Multi-line statements

    Args:
        sql: SQL file content

    Returns:
        List of SQL statements
    """
    # Remove single-line comments
    lines = []
    for line in sql.split('\n'):
        # Remove -- comments
        if '--' in line:
            line = line[:line.index('--')]
        lines.append(line)

    sql = '\n'.join(lines)

    # Remove multi-line comments /* ... */
    import re
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)

    # Split by semicolons
    statements = sql.split(';')

    # Filter out empty statements
    statements = [s.strip() for s in statements if s.strip()]

    return statements


def create_migration(project_path: str, name: str) -> str:
    """
    Create a new migration file.

    Args:
        project_path: Project directory path
        name: Migration name (e.g., "create_users")

    Returns:
        Path to the created migration file

    Example:
        create_migration('/path/to/project', 'create_users')
        # Creates: migrations/001_create_users.sql
    """
    import datetime

    migrations_path = os.path.join(project_path, 'migrations')

    # Create migrations/ directory if it doesn't exist
    os.makedirs(migrations_path, exist_ok=True)

    # Get next migration number
    existing_migrations = glob.glob(os.path.join(migrations_path, '*.sql'))
    if existing_migrations:
        # Extract numbers from filenames
        numbers = []
        for filepath in existing_migrations:
            filename = os.path.basename(filepath)
            if filename[0].isdigit():
                # Extract leading number
                num_str = ''
                for char in filename:
                    if char.isdigit():
                        num_str += char
                    else:
                        break
                if num_str:
                    numbers.append(int(num_str))

        next_num = max(numbers) + 1 if numbers else 1
    else:
        next_num = 1

    # Create filename
    filename = f"{next_num:03d}_{name}.sql"
    filepath = os.path.join(migrations_path, filename)

    # Create file with template
    template = f"""-- Migration: {name}
-- Created: {datetime.datetime.now().isoformat()}

-- Add your SQL statements here

"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(template)

    print(f"Created migration: {filename}")
    return filepath
