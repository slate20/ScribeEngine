import os
import json
import time
from datetime import datetime

class JSONStorage:
    def __init__(self, save_dir='saves'):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)
        self.session_start_time = time.time()
    
    def save_game(self, slot, game_state, description=None, passage_name=None):
        """
        Save game with enhanced metadata support.
        
        Args:
            slot: Save slot number
            game_state: Current game state dictionary
            description: Optional user description for the save
            passage_name: Current passage name for display
        """
        filename = f"{self.save_dir}/slot_{slot}.json"
        
        # Calculate playtime (rough estimate based on session time)
        playtime = int(time.time() - self.session_start_time)
        
        # Load existing save to preserve creation timestamp
        existing_save = self.load_game(slot)
        created_timestamp = existing_save.get('created_timestamp') if existing_save else datetime.now().isoformat()
        
        save_data = {
            # Core save data
            'game_state': game_state,
            
            # Metadata
            'description': description or '',
            'passage_name': passage_name or game_state.get('current_passage', 'Unknown'),
            'timestamp': datetime.now().isoformat(),
            'created_timestamp': created_timestamp,
            'playtime': playtime,
            'version': '2.0',
            
            # Engine compatibility
            'engine_version': '2.0',
            'save_format_version': 2
        }
        
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2, default=str)
    
    def load_game(self, slot):
        """Load game save data."""
        filename = f"{self.save_dir}/slot_{slot}.json"
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return None
        return None
    
    def get_save_metadata(self, slot):
        """Get save metadata without loading full game state."""
        save_data = self.load_game(slot)
        if save_data:
            return {
                'slot': slot,
                'description': save_data.get('description', ''),
                'passage_name': save_data.get('passage_name', save_data.get('game_state', {}).get('current_passage', 'Unknown')),
                'timestamp': save_data.get('timestamp'),
                'created_timestamp': save_data.get('created_timestamp'),
                'playtime': save_data.get('playtime', 0),
                'version': save_data.get('version', '1.0'),
                'engine_version': save_data.get('engine_version', '1.0')
            }
        return None
    
    def list_saves(self):
        """List save slot numbers (legacy compatibility)."""
        saves = []
        for filename in os.listdir(self.save_dir):
            if filename.startswith('slot_') and filename.endswith('.json'):
                try:
                    slot = int(filename.split('_')[1].split('.')[0])
                    saves.append(slot)
                except ValueError:
                    continue
        return sorted(saves)
    
    def list_saves_with_metadata(self):
        """List all saves with their metadata."""
        saves = {}
        for filename in os.listdir(self.save_dir):
            if filename.startswith('slot_') and filename.endswith('.json'):
                try:
                    slot = int(filename.split('_')[1].split('.')[0])
                    metadata = self.get_save_metadata(slot)
                    if metadata:
                        saves[slot] = metadata
                except ValueError:
                    continue
        return saves
    
    def delete_save(self, slot):
        """Delete a save file."""
        filename = f"{self.save_dir}/slot_{slot}.json"
        if os.path.exists(filename):
            try:
                os.remove(filename)
                return True
            except OSError:
                return False
        return False
    
    def export_save(self, slot):
        """Export save data for sharing/backup."""
        save_data = self.load_game(slot)
        if save_data:
            # Add export metadata
            save_data['exported_timestamp'] = datetime.now().isoformat()
            save_data['original_slot'] = slot
            return save_data
        return None
    
    def import_save(self, slot, save_data):
        """Import save data from backup/sharing."""
        if not isinstance(save_data, dict) or 'game_state' not in save_data:
            return False
        
        try:
            # Update metadata for import
            save_data['timestamp'] = datetime.now().isoformat()
            save_data['imported_timestamp'] = datetime.now().isoformat()
            
            filename = f"{self.save_dir}/slot_{slot}.json"
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2, default=str)
            return True
        except Exception:
            return False
    
    def validate_save(self, slot):
        """Validate save file integrity."""
        save_data = self.load_game(slot)
        if not save_data:
            return False, "Save file not found"
        
        if 'game_state' not in save_data:
            return False, "Invalid save format: missing game_state"
        
        if not isinstance(save_data['game_state'], dict):
            return False, "Invalid save format: game_state is not a dictionary"
        
        return True, "Save file is valid"