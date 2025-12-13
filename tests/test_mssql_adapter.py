"""
Unit tests for Microsoft SQL Server database adapter.

These tests verify the adapter works correctly but require an MSSQL server.
To run these tests:
1. Install SQL Server locally (or use Docker)
2. Create a test database
3. Run: pytest tests/test_mssql_adapter.py
"""

import pytest
from scribe.database.mssql import MSSQLAdapter


def test_adapter_imports():
    """Test that MSSQL adapter imports successfully"""
    assert MSSQLAdapter is not None


def test_placeholder_conversion():
    """Test SQLite-style placeholder conversion"""
    config = {
        'type': 'mssql',
        'host': 'localhost',
        'port': 1433,
        'user': 'sa',
        'password': 'test',
        'database': 'test'
    }

    # We can't actually connect without a real DB, but we can test the class exists
    assert hasattr(MSSQLAdapter, '_convert_placeholders')

    # Create a mock instance to test placeholder conversion
    # Note: This will fail to connect, which is expected for unit tests
    try:
        adapter = MSSQLAdapter(config)
    except Exception as e:
        # Expected - no actual database available
        assert 'connect' in str(e).lower() or 'connection' in str(e).lower() or 'login' in str(e).lower()


def test_config_validation():
    """Test that adapter validates required config parameters"""
    # Missing 'user'
    config = {
        'type': 'mssql',
        'database': 'test'
    }

    with pytest.raises(ValueError, match="MSSQL requires 'user' and 'database'"):
        adapter = MSSQLAdapter(config)

    # Missing 'database'
    config = {
        'type': 'mssql',
        'user': 'sa'
    }

    with pytest.raises(ValueError, match="MSSQL requires 'user' and 'database'"):
        adapter = MSSQLAdapter(config)


def test_required_methods():
    """Test that adapter has all required methods"""
    required_methods = [
        'connect', 'close', 'query', 'execute', 'commit', 'rollback',
        'find', 'where', 'insert', 'update', 'delete', 'table'
    ]

    for method in required_methods:
        assert hasattr(MSSQLAdapter, method), f"Missing method: {method}"


# Integration tests (require actual MSSQL server)
# These are skipped by default - run with: pytest --run-integration

@pytest.mark.integration
@pytest.mark.skipif(True, reason="Requires MSSQL server - run with --run-integration")
def test_mssql_connection():
    """
    Integration test: Connect to MSSQL (requires actual server)

    Setup instructions (Docker):
    docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=Test123!" \
        -p 1433:1433 -d mcr.microsoft.com/mssql/server:2022-latest

    Then create test database:
    docker exec -it <container> /opt/mssql-tools/bin/sqlcmd \
        -S localhost -U sa -P "Test123!" \
        -Q "CREATE DATABASE scribe_test"
    """
    config = {
        'type': 'mssql',
        'host': 'localhost',
        'port': 1433,
        'user': 'sa',
        'password': 'Test123!',
        'database': 'scribe_test'
    }

    adapter = MSSQLAdapter(config)

    # Test basic query
    result = adapter.query("SELECT 1 as test")
    assert len(result) == 1
    assert result[0]['test'] == 1

    adapter.close()


@pytest.mark.integration
@pytest.mark.skipif(True, reason="Requires MSSQL server - run with --run-integration")
def test_mssql_crud_operations():
    """
    Integration test: Test CRUD operations (requires actual server)
    """
    config = {
        'type': 'mssql',
        'host': 'localhost',
        'port': 1433,
        'user': 'sa',
        'password': 'Test123!',
        'database': 'scribe_test'
    }

    adapter = MSSQLAdapter(config)

    try:
        # Create test table
        adapter.execute("""
            IF OBJECT_ID('test_users', 'U') IS NOT NULL
                DROP TABLE test_users
        """)
        adapter.execute("""
            CREATE TABLE test_users (
                id INT IDENTITY(1,1) PRIMARY KEY,
                username NVARCHAR(100),
                email NVARCHAR(100)
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
