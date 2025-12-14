"""
Execution context for sandboxed Python code in templates.

This module provides a controlled environment for executing Python code
from template files, with access to database, session, request, and helpers.
"""

import types
import inspect
from typing import Dict, Any, Optional
from scribe.execution.builtins import get_safe_builtins


class ExecutionContext:
    """
    Sandboxed execution environment for template Python code.

    Provides controlled access to:
        - Database operations (db)
        - Session management (session)
        - Request data (request)
        - Flask g object (g)
        - Helper functions from lib/
        - Safe built-in functions

    Blocks dangerous operations like file I/O and system calls.
    """

    def __init__(
        self,
        db=None,
        session=None,
        request=None,
        g=None,
        helpers: Optional[Dict[str, Any]] = None,
        route_params: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize execution context.

        Args:
            db: DatabaseAdapter instance
            session: Flask session object
            request: Flask request object
            g: Flask g object
            helpers: Dict of helper functions/objects loaded from lib/
            route_params: Dict of route parameters (e.g., {'post_id': 123})
        """
        self.db = db
        self.session = session
        self.request = request
        self.g = g
        self.helpers = helpers or {}
        self.route_params = route_params or {}

        # Namespace for code execution (variables set in Python blocks)
        self.namespace: Dict[str, Any] = {}

        # Build the execution globals
        self._build_globals()

    def _build_globals(self):
        """
        Build the global namespace for code execution.

        Includes:
            - Safe builtins
            - Database adapter (db)
            - Session (session)
            - Request (request)
            - Flask g (g)
            - Helper functions
            - Route parameters
        """
        # Start with safe builtins
        self.namespace = get_safe_builtins()

        # Add framework objects
        self.namespace['db'] = self.db
        self.namespace['session'] = self.session
        self.namespace['request'] = self.request
        self.namespace['g'] = self.g

        # Add helpers from lib/ directory
        self.namespace.update(self.helpers)

        # Add route parameters (e.g., post_id from /posts/<int:post_id>)
        self.namespace.update(self.route_params)

        # Add common imports that are safe
        self._add_safe_imports()

    def _add_safe_imports(self):
        """Add commonly used safe modules to namespace."""
        # We can add safe modules here if needed
        # For now, templates can import them explicitly in code blocks

        # Example of pre-importing safe modules:
        import datetime
        import json
        import re
        import math

        self.namespace['datetime'] = datetime
        self.namespace['json'] = json
        self.namespace['re'] = re
        self.namespace['math'] = math

    def execute(self, code: str) -> Any:
        """
        Execute Python code in the sandboxed environment.

        Args:
            code: Python code to execute

        Returns:
            Return value from the code (if any), or None

        Raises:
            Any exceptions raised by the code

        Example:
            context = ExecutionContext(db=db, session=session, request=request)
            context.execute('''
            user_id = session.get('user_id')
            user = db.find('users', user_id)
            ''')
            user = context.get_variable('user')
        """
        try:
            # Check if code contains return statements
            import re
            has_return = bool(re.search(r'\breturn\b', code))

            if has_return:
                # Define custom exception class for handling returns
                # Execute this in the namespace so it's available
                setup_code = '''
class __ScribeReturn__(Exception):
    """Internal exception for handling return statements"""
    def __init__(self, value):
        self.value = value
        super().__init__()
'''
                exec(setup_code, self.namespace, self.namespace)

                # Transform return statements to raise exception instead
                # Replace "return xyz" with "raise __ScribeReturn__(xyz)"
                transformed_code = re.sub(
                    r'\breturn\s+(.+)$',
                    r'raise __ScribeReturn__(\1)',
                    code,
                    flags=re.MULTILINE
                )

                # Also handle bare "return" statements
                transformed_code = re.sub(
                    r'\breturn\s*$',
                    r'raise __ScribeReturn__(None)',
                    transformed_code,
                    flags=re.MULTILINE
                )

                # Wrap in try/except to catch the return exception
                wrapped_code = f'''
try:
{self._indent_code(transformed_code, 4)}
    __scribe_return__ = None
except __ScribeReturn__ as __e__:
    __scribe_return__ = __e__.value
'''
                # Execute directly in the namespace (no function wrapper)
                exec(wrapped_code, self.namespace, self.namespace)
            else:
                # No return statements, execute directly
                exec(code, self.namespace, self.namespace)

            # Check if there's a return value
            return_value = self.namespace.get('__scribe_return__')

            # Store in __return__ for backward compatibility
            if return_value is not None:
                self.namespace['__return__'] = return_value

            return return_value

        except Exception as e:
            # Re-raise exceptions with better context
            raise ExecutionError(f"Error executing template code: {e}") from e

    def _indent_code(self, code: str, spaces: int = 4) -> str:
        """
        Indent code by specified number of spaces for wrapping in a function.

        Args:
            code: Code to indent
            spaces: Number of spaces to indent (default: 4)

        Returns:
            Indented code
        """
        indent = ' ' * spaces
        lines = code.split('\n')
        indented_lines = [indent + line if line.strip() else line for line in lines]
        return '\n'.join(indented_lines)

    def get_variable(self, name: str, default: Any = None) -> Any:
        """
        Get a variable from the execution namespace.

        Args:
            name: Variable name
            default: Default value if variable doesn't exist

        Returns:
            Variable value or default
        """
        return self.namespace.get(name, default)

    def get_variables(self) -> Dict[str, Any]:
        """
        Get all variables from the namespace for template rendering.

        Returns:
            Dict of variable name -> value

        This returns user-defined variables (excluding builtins and framework objects)
        """
        # Get safe builtins to exclude them
        safe_builtins = get_safe_builtins()

        # Filter out builtins, framework objects, and modules
        user_vars = {}
        for key, value in self.namespace.items():
            # Skip builtins
            if key in safe_builtins:
                continue

            # Skip framework objects
            if key in ('db', 'session', 'request', 'g'):
                continue

            # Skip modules, functions, and classes (but NOT instances)
            if isinstance(value, types.ModuleType):
                continue
            if isinstance(value, types.FunctionType):
                continue
            if inspect.isclass(value):
                continue

            # Skip private variables
            if key.startswith('_'):
                continue

            user_vars[key] = value

        return user_vars

    def set_variable(self, name: str, value: Any):
        """
        Set a variable in the execution namespace.

        Args:
            name: Variable name
            value: Variable value
        """
        self.namespace[name] = value

    def has_return_value(self) -> bool:
        """
        Check if the executed code has a return value.

        Returns:
            True if code returned a value (redirect, jsonify, abort, etc.)
        """
        return '__return__' in self.namespace


class ExecutionError(Exception):
    """Exception raised when template code execution fails."""
    pass
