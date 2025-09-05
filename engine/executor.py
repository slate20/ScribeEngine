import sys
import traceback
import inspect
from types import SimpleNamespace, FunctionType, ModuleType
from typing import Dict, Any, Optional, List

class SafeExecutor:
    def __init__(self, game_state: Dict, features: Dict = None, debug_mode: bool = False):
        self.game_state = game_state
        self.features = features if features is not None else {}
        self.debug_mode = debug_mode
        self.allowed_imports = {'random', 'math', 'datetime'}
        self.systems = {}

    def load_systems(self, python_files: List[str]):
        """Load functions and classes from .py files into the executor."""
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

        # Then, extract only the functions and classes
        for name, value in temp_globals.items():
            if isinstance(value, (FunctionType, type)) and not name.startswith('__'):
                self.systems[name] = value

    def get_systems(self) -> Dict[str, Any]:
        return self.systems

    def load_systems_from_cache(self, systems_cache: Dict[str, Any]):
        """Load systems from a pre-existing cache."""
        self.systems = systems_cache

    def create_safe_globals(self) -> Dict[str, Any]:
        """Create the sandboxed global environment for game code execution."""
        def custom_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name in self.allowed_imports:
                return __import__(name, globals, locals, fromlist, level)
            raise ImportError(f"Module '{name}' is not allowed.")

        safe_builtins = {
            'len': len, 'str': str, 'int': int, 'float': float,
            'bool': bool, 'list': list, 'dict': dict, 'range': range,
            'min': min, 'max': max, 'sum': sum, 'abs': abs, 'round': round,
            'print': self.debug_print, 'isinstance': isinstance,
            'hasattr': hasattr, 'getattr': getattr, 'setattr': setattr,
            '__import__': custom_import
        }

        safe_globals = {
            '__builtins__': safe_builtins,
            'flags': self.game_state.get('flags', {}),
            'variables': self.game_state.get('variables', {}),
            'passage_tags': self.game_state.get('passage_tags', []), # Expose current passage tags
            'set_flag': self.set_flag,
            'get_flag': self.get_flag,
            'set_variable': self.set_variable,
            'get_variable': self.get_variable,
            'debug': self.debug_print,
        }

        # Add systems
        safe_globals.update(self.systems)

        # Conditionally add player object
        if self.features.get('use_default_player', True):
            player_dict = self.game_state.get('player', {})
            safe_globals['player'] = SimpleNamespace(**player_dict)
        else:
            # Use custom player class if provided
            if 'Player' in self.systems and isinstance(self.systems['Player'], type):
                # Check if a player state already exists (e.g., from a save)
                player_data = self.game_state.get('player', {})
                safe_globals['player'] = self.systems['Player'](**player_data)
            else:
                # Optionally, raise an error or default to a basic object
                raise TypeError("Custom player class 'Player' not found in project Python files.")

        # Conditionally add inventory helpers
        if self.features.get('use_default_inventory', False):
            safe_globals.update({
                'add_to_inventory': self.add_to_inventory,
                'remove_from_inventory': self.remove_from_inventory,
                'has_item': self.has_item,
                'get_item_count': self.get_item_count,
            })

        return safe_globals

    def execute_code(self, code: str) -> Optional[str]:
        self.debug_print(f"execute_code received: {code}")
        """Execute a block of code from a passage safely."""
        try:
            safe_globals = self.create_safe_globals()

            exec(code, safe_globals)
            self.update_game_state(safe_globals)
            return None
        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            self.debug_print(f"ERROR in passage code: {error_msg}")
            if self.debug_mode:
                traceback.print_exc(file=sys.stdout)
            return error_msg

    def update_game_state(self, safe_globals: Dict):
        """Update the main game state from the sandbox environment after execution."""
        if 'player' in safe_globals:
            player_obj = safe_globals['player']
            # Convert the player object (whether it's a SimpleNamespace or a custom class instance) to a dictionary
            player_dict = {k: v for k, v in vars(player_obj).items() if not k.startswith('__') and not callable(v)}
            self.game_state['player'] = player_dict

    def debug_print(self, *args):
        if self.debug_mode:
            message = ' '.join(str(arg) for arg in args)
            print(f"[DEBUG] {message}")

    # --- Helper Functions --- #

    def set_flag(self, name: str, value: bool = True):
        self.game_state.setdefault('flags', {})[name] = value

    def get_flag(self, name: str, default: bool = False) -> bool:
        return self.game_state.get('flags', {}).get(name, default)

    def set_variable(self, key: str, value: Any):
        parts = key.split('.')
        current = self.game_state.setdefault('variables', {})
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                current[part] = value
            else:
                if not isinstance(current, dict):
                    raise TypeError(f"Cannot set variable: '{'.'.join(parts[:i])}' is not a dictionary.")
                current = current.setdefault(part, {})

    def get_variable(self, key: str, default: Any = None) -> Any:
        parts = key.split('.')
        current = self.game_state.get('variables', {})
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current

    def add_to_inventory(self, item: str, quantity: int = 1):
        inventory = self.game_state.get('player', {}).setdefault('inventory', [])
        existing = next((i for i in inventory if i.get('name') == item), None)
        if existing:
            existing['quantity'] = existing.get('quantity', 1) + quantity
        else:
            inventory.append({'name': item, 'quantity': quantity})

    def remove_from_inventory(self, item: str, quantity: int = 1):
        inventory = self.game_state.get('player', {}).get('inventory', [])
        for i, inv_item in enumerate(inventory):
            if inv_item.get('name') == item:
                current_qty = inv_item.get('quantity', 1)
                if current_qty <= quantity:
                    inventory.pop(i)
                else:
                    inv_item['quantity'] -= quantity
                break

    def has_item(self, item: str) -> bool:
        inventory = self.game_state.get('player', {}).get('inventory', [])
        return any(i.get('name') == item for i in inventory)

    def get_item_count(self, item: str) -> int:
        inventory = self.game_state.get('player', {}).get('inventory', [])
        for inv_item in inventory:
            if inv_item.get('name') == item:
                return inv_item.get('quantity', 0)
        return 0
