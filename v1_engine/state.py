from typing import Dict, Any, List
from datetime import datetime

class DefaultPlayer:
    """Default Player class for quickstart projects"""
    def __init__(self):
        self.name = ''
        self.health = 100
        self.energy = 100
        self.inventory = []
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'health': self.health,
            'energy': self.energy,
            'inventory': self.inventory,
            '__class_name__': 'DefaultPlayer'
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create instance from dictionary"""
        player = cls()
        player.name = data.get('name', '')
        player.health = data.get('health', 100)
        player.energy = data.get('energy', 100)
        player.inventory = data.get('inventory', [])
        return player

class StateManager:
    def __init__(self, features: Dict = None, starting_passage: str = 'start'):
        self.features = features if features is not None else {}
        self.starting_passage = starting_passage
        self.initial_state = self.create_initial_state()
    
    def create_initial_state(self) -> Dict[str, Any]:
        """Create initial game state based on features."""
        state = {
            'current_passage': self.starting_passage,
            'metadata': {
                'created_date': datetime.now().isoformat(),
                'last_played': datetime.now().isoformat()
            }
        }

        if self.features.get('use_default_player', False):
            state['player'] = DefaultPlayer()
        
        return state
    
    def get_initial_state(self) -> Dict[str, Any]:
        """Get a copy of initial state"""
        # Create fresh initial state to ensure objects are not shared
        return self.create_initial_state()
    
    def reset_state(self) -> Dict[str, Any]:
        """Reset to initial state"""
        return self.create_initial_state()

