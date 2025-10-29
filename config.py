"""
Environment configuration module for Scribe Framework

Provides centralized configuration management with environment variable support.
Supports development and production modes with appropriate defaults for each.
"""

import os
from typing import Optional


class Config:
    """Centralized configuration with environment variable support"""

    @staticmethod
    def get_env() -> str:
        """
        Get current environment mode.

        Returns:
            'development' or 'production'

        Environment:
            SCRIBE_ENV: Set to 'production' for production mode
        """
        return os.getenv('SCRIBE_ENV', 'development').lower()

    @staticmethod
    def is_production() -> bool:
        """Check if running in production mode."""
        return Config.get_env() == 'production'

    @staticmethod
    def is_development() -> bool:
        """Check if running in development mode."""
        return Config.get_env() == 'development'

    @staticmethod
    def get_secret_key() -> Optional[str]:
        """
        Get Flask secret key from environment.

        Returns:
            Secret key string or None if not set

        Environment:
            SCRIBE_SECRET_KEY: Required in production mode
        """
        return os.getenv('SCRIBE_SECRET_KEY')

    @staticmethod
    def get_project_path() -> Optional[str]:
        """
        Get project path from environment.

        Returns:
            Project directory path or None if not set

        Environment:
            SCRIBE_PROJECT_PATH: Path to the project directory
        """
        return os.getenv('SCRIBE_PROJECT_PATH')

    @staticmethod
    def get_port() -> int:
        """
        Get server port from environment.

        Returns:
            Port number (default: 5000)

        Environment:
            SCRIBE_PORT: Server port number
        """
        try:
            return int(os.getenv('SCRIBE_PORT', '5000'))
        except ValueError:
            return 5000

    @staticmethod
    def get_host() -> str:
        """
        Get server host from environment.

        Returns:
            Host address (default: '127.0.0.1' for dev, '0.0.0.0' for prod)

        Environment:
            SCRIBE_HOST: Server host address
        """
        default_host = '0.0.0.0' if Config.is_production() else '127.0.0.1'
        return os.getenv('SCRIBE_HOST', default_host)

    @staticmethod
    def get_debug_mode() -> bool:
        """
        Get debug mode setting.

        Returns:
            True if debug enabled, False otherwise

        Environment:
            SCRIBE_DEBUG: Set to '1', 'true', 'yes' to enable debug
        """
        debug_env = os.getenv('SCRIBE_DEBUG', '').lower()
        if debug_env in ('1', 'true', 'yes'):
            return True
        # Default: debug in development, no debug in production
        return Config.is_development()

    @staticmethod
    def validate_production() -> tuple[bool, str]:
        """
        Validate that production requirements are met.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not Config.is_production():
            return True, ""

        errors = []

        # Check secret key
        if not Config.get_secret_key():
            errors.append("SCRIBE_SECRET_KEY environment variable is required in production")

        # Check project path
        if not Config.get_project_path():
            errors.append("SCRIBE_PROJECT_PATH environment variable is required in production")

        if errors:
            return False, "; ".join(errors)

        return True, ""

    @staticmethod
    def get_all_config() -> dict:
        """
        Get all configuration as a dictionary for debugging.

        Returns:
            Dictionary with all configuration values
        """
        return {
            'environment': Config.get_env(),
            'is_production': Config.is_production(),
            'is_development': Config.is_development(),
            'host': Config.get_host(),
            'port': Config.get_port(),
            'debug_mode': Config.get_debug_mode(),
            'project_path': Config.get_project_path(),
            'has_secret_key': bool(Config.get_secret_key()),
        }

    @staticmethod
    def print_config():
        """Print current configuration to console (for debugging)."""
        config = Config.get_all_config()
        print("\n" + "="*50)
        print("Scribe Framework Configuration")
        print("="*50)
        for key, value in config.items():
            if key == 'has_secret_key':
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value}")
        print("="*50 + "\n")


def generate_secret_key() -> str:
    """
    Generate a random secret key for Flask.

    Returns:
        Random hex string suitable for Flask secret_key
    """
    import secrets
    return secrets.token_hex(32)


# Example usage in production:
#   export SCRIBE_ENV=production
#   export SCRIBE_PROJECT_PATH=/var/www/myapp
#   export SCRIBE_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
#   export SCRIBE_PORT=8000
#   export SCRIBE_HOST=0.0.0.0
#   gunicorn -w 4 -b 0.0.0.0:8000 wsgi:application
