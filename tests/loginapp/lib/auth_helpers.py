"""Authentication helpers - auto-loaded into all templates"""
from werkzeug.security import check_password_hash, generate_password_hash


def verify_password(password_hash, password):
    """Verify password against hash"""
    if password is None or password_hash is None:
        return False
    return check_password_hash(password_hash, password)


def hash_password(password):
    """Hash a password for storage"""
    return generate_password_hash(password)
