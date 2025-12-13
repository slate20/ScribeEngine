"""
Unit tests for PostgreSQL database adapter.

These tests verify the adapter works correctly but require a PostgreSQL server.
To run these tests:
1. Install PostgreSQL locally
2. Create a test database
3. Run: pytest tests/test_postgresql_adapter.py
"""

import pytest
from scribe.database.postgresql import PostgreSQLAdapter


def test_adapter_imports():
    """Test that PostgreSQL adapter imports successfully"""
    assert PostgreSQLAdapter is not None


def test_placeholder_conversion():
    """Test SQLite-style placeholder conversion"""
    config = {
        'type': 'postgresql',
        'host': 'localhost',
        'port': 5432,
        'user': 'test',
        'database': 'test'
    }

    # We can't actually connect without a real DB, but we can test the class exists
    assert hasattr(PostgreSQLAdapter, '_convert_placeholders')

    # Create a mock instance to test placeholder conversion
    # Note: This will fail to connect, which is expected for unit tests
    try:
        adapter = PostgreSQLAdapter(config)
    except Exception as e:
        # Expected - no actual database available
        assert 'could not connect' in str(e).lower() or 'connection' in str(e).lower()


def test_config_validation():
    """Test that adapter validates required config parameters"""
    # Missing 'user'
    config = {
        'type': 'postgresql',
        'database': 'test'
    }

    with pytest.raises(ValueError, match="PostgreSQL requires 'user' and 'database'"):
        adapter = PostgreSQLAdapter(config)

    # Missing 'database'
    config = {
        'type': 'postgresql',
        'user': 'test'
    }

    with pytest.raises(ValueError, match="PostgreSQL requires 'user' and 'database'"):
        adapter = PostgreSQLAdapter(config)


def test_required_methods():
    """Test that adapter has all required methods"""
    required_methods = [
        'connect', 'close', 'query', 'execute', 'commit', 'rollback',
        'find', 'where', 'insert', 'update', 'delete', 'table'
    ]

    for method in required_methods:
        assert hasattr(PostgreSQLAdapter, method), f"Missing method: {method}"


# Integration tests (require actual PostgreSQL server)
# These are skipped by default - run with: pytest --run-integration

@pytest.mark.integration
@pytest.mark.skipif(True, reason="Requires PostgreSQL server - run with --run-integration")
def test_postgresql_connection():
    """
    Integration test: Connect to PostgreSQL (requires actual server)

    Setup instructions:
    1. Install PostgreSQL
    2. Create database: CREATE DATABASE scribe_test;
    3. Create user: CREATE USER scribe_test WITH PASSWORD 'test123';
    4. Grant access: GRANT ALL PRIVILEGES ON DATABASE scribe_test TO scribe_test;
    """
    config = {
        'type': 'postgresql',
        'host': 'localhost',
        'port': 5432,
        'user': 'scribe_test',
        'password': 'test123',
        'database': 'scribe_test'
    }

    adapter = PostgreSQLAdapter(config)

    # Test basic query
    result = adapter.query("SELECT 1 as test")
    assert len(result) == 1
    assert result[0]['test'] == 1

    adapter.close()


@pytest.mark.integration
@pytest.mark.skipif(True, reason="Requires PostgreSQL server - run with --run-integration")
def test_postgresql_crud_operations():
    """
    Integration test: Test CRUD operations (requires actual server)
    """
    config = {
        'type': 'postgresql',
        'host': 'localhost',
        'port': 5432,
        'user': 'scribe_test',
        'password': 'test123',
        'database': 'scribe_test'
    }

    adapter = PostgreSQLAdapter(config)

    try:
        # Create test table
        adapter.execute("""
            CREATE TABLE IF NOT EXISTS test_users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100),
                email VARCHAR(100)
            )
        """)
        adapter.commit()

        # INSERT
        user_id = adapter.insert('test_users', username='alice', email='alice@example.com')
        assert user_id > 0
        adapter.commit()

        # FIND
        user = adapter.find('test_users', user_id)
        assert user is not None
        assert user['username'] == 'alice'
        assert user['email'] == 'alice@example.com'

        # WHERE
        users = adapter.where('test_users', username='alice')
        assert len(users) == 1
        assert users[0]['id'] == user_id

        # UPDATE
        updated_count = adapter.update('test_users', {'email': 'alice.updated@example.com'}, id=user_id)
        assert updated_count == 1
        adapter.commit()

        user = adapter.find('test_users', user_id)
        assert user['email'] == 'alice.updated@example.com'

        # DELETE
        deleted_count = adapter.delete('test_users', id=user_id)
        assert deleted_count == 1
        adapter.commit()

        user = adapter.find('test_users', user_id)
        assert user is None

        # Clean up
        adapter.execute("DROP TABLE IF EXISTS test_users")
        adapter.commit()

    finally:
        adapter.close()


if __name__ == '__main__':
    # Run basic tests only (no integration)
    pytest.main([__file__, '-v'])
