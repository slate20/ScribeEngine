from typing import Dict, Any, List
from datetime import datetime

class StateManager:
    def __init__(self, features: Dict = None, starting_passage: str = 'start'):
        self.features = features if features is not None else {}
        self.starting_passage = starting_passage
        self.initial_state = self.create_initial_state()
    
    def create_initial_state(self) -> Dict[str, Any]:
        """Create initial game state based on features."""
        state = {
            'current_passage': self.starting_passage,
            'flags': {},
            'variables': {},
            'metadata': {
                'created_date': datetime.now().isoformat(),
                'last_played': datetime.now().isoformat()
            }
        }

        if self.features.get('use_default_player', False):
            state['player'] = {
                'name': '',
                'health': 100,
                'score': 0,
                'experience': 0,
                'level': 1
            }
            if self.features.get('use_default_inventory', False):
                state['player']['inventory'] = []
        
        return state
    
    def get_initial_state(self) -> Dict[str, Any]:
        """Get a copy of initial state"""
        # Return a deep copy to prevent modification of the template
        return {k: v.copy() if isinstance(v, dict) else v for k, v in self.initial_state.items()}
    
    def reset_state(self) -> Dict[str, Any]:
        """Reset to initial state"""
        return self.create_initial_state()

    # The validation and helper methods remain largely the same,
    # but they should be robust enough to handle the absence of 'player'
    # or 'inventory' if the features are disabled.

    def get_flag(self, state: Dict[str, Any], name: str, default: bool = False) -> bool:
        """Get flag value"""
        return state.get('flags', {}).get(name, default)
    
    def set_flag(self, state: Dict[str, Any], name: str, value: bool = True):
        """Set flag value"""
        state.setdefault('flags', {})[name] = value
    
    def has_item(self, state: Dict[str, Any], item: str) -> bool:
        """Check if player has item. Returns False if inventory system is disabled."""
        inventory = state.get('player', {}).get('inventory', [])
        return any(i.get('name') == item for i in inventory)
    
    def get_item_count(self, state: Dict[str, Any], item: str) -> int:
        """Get item count. Returns 0 if inventory system is disabled."""
        inventory = state.get('player', {}).get('inventory', [])
        for inv_item in inventory:
            if inv_item.get('name') == item:
                return inv_item.get('quantity', 0)
        return 0
    
    def get_variable(self, state: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Get variable value"""
        return state.get('variables', {}).get(key, default)
    
    def set_variable(self, state: Dict[str, Any], key: str, value: Any):
        """Set variable value"""
        state.setdefault('variables', {})[key] = value
