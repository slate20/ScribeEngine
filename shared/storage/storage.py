import os
import json
import time
import base64
import hashlib
from datetime import datetime

class JSONStorage:
    def __init__(self, save_dir='saves', project_path=None):
        self.save_dir = save_dir
        self.project_path = project_path
        os.makedirs(self.save_dir, exist_ok=True)
        self.session_start_time = time.time()
        self._obfuscation_key = self._generate_obfuscation_key()

    def _generate_obfuscation_key(self):
        """Generate project-specific obfuscation key."""
        if self.project_path:
            # Use project path and directory name for key generation
            key_material = f"{self.project_path}:{os.path.basename(self.project_path)}"
        else:
            # Fallback key for older instances
            key_material = f"{self.save_dir}:default"

        # Create deterministic but project-specific key
        return hashlib.sha256(key_material.encode()).digest()[:16]  # 16 bytes for XOR

    def _obfuscate_data(self, data_str):
        """Obfuscate save data using XOR + Base64."""
        try:
            data_bytes = data_str.encode('utf-8')
            key = self._obfuscation_key

            # XOR with repeating key
            obfuscated = bytearray()
            for i, byte in enumerate(data_bytes):
                obfuscated.append(byte ^ key[i % len(key)])

            # Encode to Base64 for safe storage
            return base64.b64encode(obfuscated).decode('ascii')
        except Exception as e:
            # If obfuscation fails, return original (for debugging)
            return data_str

    def _deobfuscate_data(self, obfuscated_str):
        """Deobfuscate save data from Base64 + XOR."""
        try:
            # Decode from Base64
            obfuscated_bytes = base64.b64decode(obfuscated_str.encode('ascii'))
            key = self._obfuscation_key

            # XOR with repeating key (same operation reverses it)
            data_bytes = bytearray()
            for i, byte in enumerate(obfuscated_bytes):
                data_bytes.append(byte ^ key[i % len(key)])

            return data_bytes.decode('utf-8')
        except Exception as e:
            # If deobfuscation fails, treat as plain text (migration case)
            return obfuscated_str

    def save_game(self, slot, game_state, description=None, passage_name=None):
        """
        Save game with enhanced metadata support.
        
        Args:
            slot: Save slot number
            game_state: Current game state dictionary
            description: Optional user description for the save
            passage_name: Current passage name for display
        """
        filename = f"{self.save_dir}/slot_{slot}.save"
        
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
            'engine_version': '1.3',
            'save_format_version': 2
        }
        
        # Convert to JSON and obfuscate
        json_str = json.dumps(save_data, indent=2, default=str)
        obfuscated_data = self._obfuscate_data(json_str)

        with open(filename, 'w') as f:
            f.write(obfuscated_data)
    
    def load_game(self, slot):
        """Load game save data."""
        filename = f"{self.save_dir}/slot_{slot}.save"
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    file_content = f.read().strip()

                # Deobfuscate and parse JSON
                json_str = self._deobfuscate_data(file_content)
                return json.loads(json_str)
            except (json.JSONDecodeError, FileNotFoundError, ValueError):
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
                'engine_version': save_data.get('engine_version', '1.3')
            }
        return None
    
    def list_saves(self):
        """List save slot numbers (legacy compatibility)."""
        saves = []
        for filename in os.listdir(self.save_dir):
            if filename.startswith('slot_') and filename.endswith('.save'):
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
            if filename.startswith('slot_') and filename.endswith('.save'):
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
        filename = f"{self.save_dir}/slot_{slot}.save"
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
            
            filename = f"{self.save_dir}/slot_{slot}.save"
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