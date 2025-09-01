import os
import json
from datetime import datetime

class JSONStorage:
    def __init__(self, save_dir='saves'):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)
    
    def save_game(self, slot, game_state):
        filename = f"{self.save_dir}/slot_{slot}.json"
        save_data = {
            'game_state': game_state,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0'
        }
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)
    
    def load_game(self, slot):
        filename = f"{self.save_dir}/slot_{slot}.json"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return None
    
    def list_saves(self):
        saves = []
        for filename in os.listdir(self.save_dir):
            if filename.startswith('slot_') and filename.endswith('.json'):
                slot = int(filename.split('_')[1].split('.')[0])
                saves.append(slot)
        return sorted(saves)