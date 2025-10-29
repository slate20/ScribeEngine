import sys
import traceback
import inspect
from types import SimpleNamespace, FunctionType, ModuleType
from typing import Dict, Any, Optional, List, Tuple

class SafeExecutor:
    def __init__(self, game_state: Dict, features: Dict = None, debug_mode: bool = False):
        self.game_state = game_state
        self.features = features if features is not None else {}
        self.debug_mode = debug_mode
        self.allowed_imports = {'random', 'math', 'datetime', 'sqlite3'}
        self.systems = {}

    def load_systems(self, python_files: List[str]):
        """Load functions, classes, AND module-level variables from .py files into the executor."""
        self.debug_print(f"Found {len(python_files)} Python files to load.")
        temp_globals = {}
        # First, execute all code in a shared temporary environment
        for py_file in python_files:
            self.debug_print(f"Loading system file: {py_file}")
            with open(py_file, 'r', encoding='utf-8') as f:
                try:
                    exec(f.read(), temp_globals)
                except Exception as e:
                    print(f"Error loading system file {py_file}: {e}")

        # Then, extract functions, classes, AND non-private variables
        for name, value in temp_globals.items():
            if not name.startswith('__'):  # Skip private/magic attributes
                if isinstance(value, (FunctionType, type)):
                    self.systems[name] = value
                    self.debug_print(f"Loaded {type(value).__name__}: {name}")
                elif not callable(value) and not inspect.ismodule(value):
                    # Include non-callable, non-module objects (dicts, lists, etc.)
                    self.systems[name] = value
                    self.debug_print(f"Loaded variable: {name} = {type(value).__name__}")

    def get_systems(self) -> Dict[str, Any]:
        return self.systems

    def load_systems_from_cache(self, systems_cache: Dict[str, Any]):
        """Load systems from a pre-existing cache."""
        self.systems = systems_cache

    def create_safe_globals(self) -> Tuple[Dict[str, Any], set]:
        """Create the sandboxed global environment for game code execution."""
        def custom_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name in self.allowed_imports:
                return __import__(name, globals, locals, fromlist, level)
            raise ImportError(f"Module '{name}' is not allowed.")

        safe_globals = {}
        safe_globals.update(self.game_state)  # Direct references to game state objects

        safe_builtins = {
            # Basic types
            'len': len, 'str': str, 'int': int, 'float': float,
            'bool': bool, 'list': list, 'dict': dict, 'tuple': tuple,
            'set': set, 'frozenset': frozenset,

            # Numeric operations
            'min': min, 'max': max, 'sum': sum, 'abs': abs, 'round': round,
            'range': range,

            # Collection operations
            'enumerate': enumerate, 'zip': zip, 'sorted': sorted,
            'reversed': reversed, 'any': any, 'all': all,
            'map': map, 'filter': filter,

            # Iterator protocol
            'iter': iter, 'next': next,

            # String/character operations
            'chr': chr, 'ord': ord, 'hex': hex, 'oct': oct, 'bin': bin,
            'repr': repr, 'ascii': ascii,

            # Type introspection
            'type': type, 'isinstance': isinstance, 'callable': callable,
            'hasattr': hasattr, 'getattr': getattr, 'setattr': setattr,
            'delattr': delattr, 'vars': vars, 'dir': dir, 'id': id,

            # Exception types for error handling
            'Exception': Exception, 'TypeError': TypeError, 'ValueError': ValueError,
            'KeyError': KeyError, 'IndexError': IndexError, 'AttributeError': AttributeError,
            'ZeroDivisionError': ZeroDivisionError, 'RuntimeError': RuntimeError,

            # System functions (custom implementations)
            'print': self.debug_print,
            'locals': lambda: safe_globals, 'globals': lambda: safe_globals,
            '__import__': custom_import,
            '__delitem__': lambda obj, key: obj.__delitem__(key),
            '__delattr__': lambda obj, attr: delattr(obj, attr)
        }
        safe_globals['__builtins__'] = safe_builtins

        helpers = {
            'debug': self.debug_print,
            'delete_var': lambda var_name: self.delete_variable(var_name, safe_globals),
        }
        safe_globals.update(helpers)
        safe_globals.update(self.systems)

        # Expose database if available
        if hasattr(self, 'db') and self.db is not None:
            safe_globals['db'] = self.db

        non_persistent_keys = set(helpers.keys()) | set(self.systems.keys())
        non_persistent_keys.add('__builtins__')
        if hasattr(self, 'db') and self.db is not None:
            non_persistent_keys.add('db')  # Don't persist db object to game state

        return safe_globals, non_persistent_keys

    def execute_code(self, code: str) -> Optional[str]:
        self.debug_print(f"execute_code received: {code}")
        """Execute a block of code from a passage safely."""
        return self.execute_code_with_context(code, {})

    def execute_code_with_context(self, code: str, context: Dict[str, Any]) -> Optional[str]:
        """Execute a block of code with additional context variables from template rendering."""
        self.debug_print(f"execute_code_with_context received: {code}")
        self.debug_print(f"Context variables: {list(context.keys())}")
        try:
            safe_globals, non_persistent_keys = self.create_safe_globals()

            # Add context variables to the execution environment
            # Context variables are temporary and shouldn't persist to game state
            for key, value in context.items():
                if key not in safe_globals:  # Don't override existing game state
                    safe_globals[key] = value
                    non_persistent_keys.add(key)  # Mark as non-persistent

            exec(code, safe_globals)
            self.update_game_state(safe_globals, non_persistent_keys)
            return None
        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            self.debug_print(f"ERROR in passage code: {error_msg}")
            if self.debug_mode:
                traceback.print_exc(file=sys.stdout)
            return error_msg

    def update_game_state(self, safe_globals: Dict, non_persistent_keys: set):
        """Update the main game state from the sandbox environment after execution."""
        # Since we're working with direct references, most updates should already be applied
        # We only need to sync back any newly created variables
        for key, value in safe_globals.items():
            if key in non_persistent_keys:
                continue

            if inspect.ismodule(value) or inspect.isfunction(value) or inspect.isclass(value):
                continue

            # Only update if this is a new key or the reference changed
            if key not in self.game_state or self.game_state[key] is not value:
                self.game_state[key] = value

    def debug_print(self, *args):
        if self.debug_mode:
            message = ' '.join(str(arg) for arg in args)
            print(f"[DEBUG] {message}")

    def delete_variable(self, var_name: str, local_scope=None):
        """Safely delete a variable from both local scope and game state"""
        deleted = False

        # Remove from local execution scope if provided
        if local_scope and var_name in local_scope:
            del local_scope[var_name]
            deleted = True
            self.debug_print(f"Deleted '{var_name}' from local scope")

        # Remove from persistent game state
        if var_name in self.game_state:
            del self.game_state[var_name]
            deleted = True
            self.debug_print(f"Deleted '{var_name}' from game state")

        if not deleted:
            self.debug_print(f"Variable '{var_name}' not found in any scope")

    # --- Helper Functions --- #


