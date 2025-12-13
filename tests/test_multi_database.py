"""
Tests for multi-database support in ScribeEngine.

Demonstrates connecting to multiple databases simultaneously.
"""

import pytest
import os
import tempfile
from scribe.database import DatabaseManager


def test_single_database_configuration():
    """Test single database configuration (most common use case)"""
    config = {
        'databases': {
            'default': {
                'type': 'sqlite',
                'database': ':memory:'
            }
        }
    }

    db_manager = DatabaseManager(config)

    # Should have exactly one connection
    assert len(list(db_manager.keys())) == 1
    assert 'default' in db_manager

    # Can access the connection
    db = db_manager['default']
    assert db is not None

    # Test a simple query
    result = db.query("SELECT 1 as test")
    assert len(result) == 1
    assert result[0]['test'] == 1

    db_manager.close_all()
    print("✓ Single database configuration works")


def test_multiple_database_configuration():
    """Test multiple database configuration"""
    # Create two temporary databases
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f1:
        db1_path = f1.name
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f2:
        db2_path = f2.name

    try:
        config = {
            'databases': {
                'primary': {
                    'type': 'sqlite',
                    'database': db1_path
                },
                'analytics': {
                    'type': 'sqlite',
                    'database': db2_path
                }
            }
        }

        db_manager = DatabaseManager(config)

        # Should have two connections
        assert len(list(db_manager.keys())) == 2
        assert 'primary' in db_manager
        assert 'analytics' in db_manager

        # Access each connection
        primary_db = db_manager['primary']
        analytics_db = db_manager['analytics']

        # Create tables in each database
        primary_db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        primary_db.commit()

        analytics_db.execute("CREATE TABLE page_views (id INTEGER PRIMARY KEY, page TEXT)")
        analytics_db.commit()

        # Insert data
        primary_db.insert('users', name='Alice')
        primary_db.commit()

        analytics_db.insert('page_views', page='/home')
        analytics_db.commit()

        # Query from each database
        users = primary_db.query("SELECT * FROM users")
        assert len(users) == 1
        assert users[0]['name'] == 'Alice'

        page_views = analytics_db.query("SELECT * FROM page_views")
        assert len(page_views) == 1
        assert page_views[0]['page'] == '/home'

        db_manager.close_all()
        print("✓ Multiple database configuration works")

    finally:
        # Clean up temp files
        if os.path.exists(db1_path):
            os.unlink(db1_path)
        if os.path.exists(db2_path):
            os.unlink(db2_path)


def test_explicit_connection_access_required():
    """Test that direct method calls raise helpful errors"""
    config = {
        'databases': {
            'default': {
                'type': 'sqlite',
                'database': ':memory:'
            }
        }
    }

    db_manager = DatabaseManager(config)

    # Direct method call should raise AttributeError
    with pytest.raises(AttributeError) as exc_info:
        db_manager.query("SELECT 1")

    error_msg = str(exc_info.value)
    assert "Cannot call db.query()" in error_msg
    assert "default" in error_msg  # Should mention available connections
    print("✓ Direct method calls properly prevented with helpful error")

    db_manager.close_all()


def test_invalid_connection_name():
    """Test accessing non-existent connection"""
    config = {
        'databases': {
            'default': {
                'type': 'sqlite',
                'database': ':memory:'
            }
        }
    }

    db_manager = DatabaseManager(config)

    with pytest.raises(KeyError) as exc_info:
        db_manager['nonexistent']

    error_msg = str(exc_info.value)
    assert "not found" in error_msg
    assert "default" in error_msg  # Should list available connections

    db_manager.close_all()
    print("✓ Invalid connection names raise helpful errors")


def test_backward_compatibility():
    """Test that old 'database' config key still works"""
    config = {
        'database': {
            'type': 'sqlite',
            'database': ':memory:'
        }
    }

    # Should auto-convert to new format
    db_manager = DatabaseManager(config)

    # Should create 'default' connection
    assert 'default' in db_manager
    assert len(list(db_manager.keys())) == 1

    # Should work normally
    db = db_manager['default']
    result = db.query("SELECT 1 as test")
    assert result[0]['test'] == 1

    db_manager.close_all()
    print("✓ Backward compatibility works")


def test_database_manager_repr():
    """Test string representation"""
    config = {
        'databases': {
            'db1': {'type': 'sqlite', 'database': ':memory:'},
            'db2': {'type': 'sqlite', 'database': ':memory:'}
        }
    }

    db_manager = DatabaseManager(config)
    repr_str = repr(db_manager)

    assert 'DatabaseManager' in repr_str
    assert 'db1' in repr_str
    assert 'db2' in repr_str

    db_manager.close_all()
    print("✓ String representation works")


if __name__ == '__main__':
    # Run all tests
    pytest.main([__file__, '-v'])
