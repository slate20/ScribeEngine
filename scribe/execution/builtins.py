"""
Safe builtins for sandboxed Python execution in templates.

This module defines which built-in functions and types are available
in template code blocks, blocking dangerous operations like file I/O
and system calls.
"""

import builtins


def get_safe_builtins():
    """
    Get a dictionary of safe built-in functions for template execution.

    Allows:
        - Basic types: int, float, str, bool, list, dict, tuple, set
        - Type checking: isinstance, type, hasattr, getattr
        - Utilities: len, range, enumerate, zip, sorted, reversed
        - String operations: str methods, format
        - Math: abs, min, max, sum, round
        - Iterables: all, any, filter, map

    Blocks:
        - File I/O: open, read, write
        - System calls: exec, eval, compile, __import__
        - Network: socket, urllib
    """

    safe_builtins = {
        # Basic types
        'int': int,
        'float': float,
        'str': str,
        'bool': bool,
        'list': list,
        'dict': dict,
        'tuple': tuple,
        'set': set,
        'frozenset': frozenset,
        'bytes': bytes,
        'bytearray': bytearray,

        # Type checking and introspection
        'isinstance': isinstance,
        'issubclass': issubclass,
        'type': type,
        'hasattr': hasattr,
        'getattr': getattr,
        'setattr': setattr,
        'delattr': delattr,
        'callable': callable,

        # Container operations
        'len': len,
        'range': range,
        'enumerate': enumerate,
        'zip': zip,
        'sorted': sorted,
        'reversed': reversed,
        'slice': slice,

        # Math
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'round': round,
        'pow': pow,
        'divmod': divmod,

        # Iteration and filtering
        'all': all,
        'any': any,
        'filter': filter,
        'map': map,

        # String and representation
        'repr': repr,
        'ascii': ascii,
        'chr': chr,
        'ord': ord,
        'format': format,

        # Object creation
        'object': object,
        'property': property,
        'staticmethod': staticmethod,
        'classmethod': classmethod,

        # Special values
        'None': None,
        'True': True,
        'False': False,
        'Ellipsis': Ellipsis,
        'NotImplemented': NotImplemented,

        # Exceptions (for raising errors)
        'Exception': Exception,
        'ValueError': ValueError,
        'TypeError': TypeError,
        'KeyError': KeyError,
        'IndexError': IndexError,
        'AttributeError': AttributeError,
        'RuntimeError': RuntimeError,
        'StopIteration': StopIteration,

        # Other utilities
        'hash': hash,
        'id': id,
        'next': next,
        'iter': iter,
        'vars': vars,
        'dir': dir,
        'print': print,  # Allow printing for debugging

        # Note: Explicitly BLOCKED:
        # - open, file, input, raw_input
        # - exec, eval, compile, execfile
        # - __import__, reload
        # - globals, locals (we provide a controlled namespace)
    }

    return safe_builtins


# List of explicitly blocked builtins for documentation
BLOCKED_BUILTINS = [
    'open',           # File I/O
    'file',           # File object
    'input',          # User input
    'eval',           # Code evaluation
    'exec',           # Code execution
    'compile',        # Code compilation
    '__import__',     # Dynamic imports
    'reload',         # Module reloading
    'globals',        # Access to global namespace
    'locals',         # Access to local namespace (we provide controlled vars)
]
