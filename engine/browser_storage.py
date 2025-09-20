import json
import time
from datetime import datetime

class BrowserStorage:
    """
    Browser cache storage system that returns JavaScript commands
    for client-side localStorage operations instead of server-side file operations.
    """

    def __init__(self, save_dir='saves', project_path=None):
        self.save_dir = save_dir  # Not used but kept for interface compatibility
        self.project_path = project_path
        self.session_start_time = time.time()
        self.project_prefix = self._generate_storage_prefix()

    def _generate_storage_prefix(self):
        """Generate project-specific localStorage key prefix."""
        if self.project_path:
            import os
            project_name = os.path.basename(self.project_path)
            return f"scribe_{project_name}_"
        return "scribe_"

    def save_game(self, slot, game_state, description=None, passage_name=None):
        """
        Return JavaScript command to save game to localStorage.

        Args:
            slot: Save slot number
            game_state: Current game state dictionary
            description: Optional user description for the save
            passage_name: Current passage name for display

        Returns:
            dict: Contains 'type': 'javascript' and 'code' with JS to execute
        """
        # Calculate playtime (rough estimate based on session time)
        playtime = int(time.time() - self.session_start_time)

        # Create save data with same structure as JSONStorage
        save_data = {
            # Core save data
            'game_state': game_state,

            # Metadata
            'description': description or '',
            'passage_name': passage_name or game_state.get('current_passage', 'Unknown'),
            'timestamp': datetime.now().isoformat(),
            'created_timestamp': datetime.now().isoformat(),  # Will be preserved if slot exists
            'playtime': playtime,
            'version': '2.0',

            # Engine compatibility
            'engine_version': '1.3',
            'save_format_version': 2
        }

        # Generate JavaScript code to save to localStorage
        save_key = f"{self.project_prefix}slot_{slot}"
        save_json = json.dumps(save_data, default=str)

        js_code = f"""
        try {{
            // Preserve creation timestamp if save already exists
            const existingKey = '{save_key}';
            const existing = localStorage.getItem(existingKey);
            let saveData = {save_json};

            if (existing) {{
                try {{
                    const existingSave = JSON.parse(existing);
                    if (existingSave.created_timestamp) {{
                        saveData.created_timestamp = existingSave.created_timestamp;
                    }}
                }} catch(e) {{
                    // Ignore parsing errors
                }}
            }}

            localStorage.setItem(existingKey, JSON.stringify(saveData));

            // Trigger success callback
            if (window.scribeStorageCallback) {{
                window.scribeStorageCallback({{
                    type: 'save',
                    success: true,
                    slot: {slot},
                    message: 'Game saved to browser cache'
                }});
            }}
        }} catch (error) {{
            console.error('Browser save failed:', error);
            if (window.scribeStorageCallback) {{
                window.scribeStorageCallback({{
                    type: 'save',
                    success: false,
                    slot: {slot},
                    message: 'Failed to save: ' + error.message
                }});
            }}
        }}
        """

        return {
            'type': 'javascript',
            'code': js_code.strip()
        }

    def load_game(self, slot):
        """
        Return JavaScript command to load game from localStorage.

        Args:
            slot: Save slot number

        Returns:
            dict: Contains 'type': 'javascript' and 'code' with JS to execute
        """
        save_key = f"{self.project_prefix}slot_{slot}"

        js_code = f"""
        try {{
            const saveData = localStorage.getItem('{save_key}');
            if (saveData) {{
                const parsed = JSON.parse(saveData);
                if (window.scribeStorageCallback) {{
                    window.scribeStorageCallback({{
                        type: 'load',
                        success: true,
                        slot: {slot},
                        data: parsed,
                        message: 'Game loaded from browser cache'
                    }});
                }}
            }} else {{
                if (window.scribeStorageCallback) {{
                    window.scribeStorageCallback({{
                        type: 'load',
                        success: false,
                        slot: {slot},
                        message: 'Save slot is empty'
                    }});
                }}
            }}
        }} catch (error) {{
            console.error('Browser load failed:', error);
            if (window.scribeStorageCallback) {{
                window.scribeStorageCallback({{
                    type: 'load',
                    success: false,
                    slot: {slot},
                    message: 'Failed to load: ' + error.message
                }});
            }}
        }}
        """

        return {
            'type': 'javascript',
            'code': js_code.strip()
        }

    def get_save_metadata(self, slot):
        """
        Return JavaScript command to get save metadata.

        Args:
            slot: Save slot number

        Returns:
            dict: Contains 'type': 'javascript' and 'code' with JS to execute
        """
        save_key = f"{self.project_prefix}slot_{slot}"

        js_code = f"""
        try {{
            const saveData = localStorage.getItem('{save_key}');
            if (saveData) {{
                const parsed = JSON.parse(saveData);
                const metadata = {{
                    slot: {slot},
                    description: parsed.description || '',
                    passage_name: parsed.passage_name || parsed.game_state?.current_passage || 'Unknown',
                    timestamp: parsed.timestamp,
                    created_timestamp: parsed.created_timestamp,
                    playtime: parsed.playtime || 0,
                    version: parsed.version || '1.0',
                    engine_version: parsed.engine_version || '1.3'
                }};

                if (window.scribeStorageCallback) {{
                    window.scribeStorageCallback({{
                        type: 'metadata',
                        success: true,
                        slot: {slot},
                        data: metadata
                    }});
                }}
            }} else {{
                if (window.scribeStorageCallback) {{
                    window.scribeStorageCallback({{
                        type: 'metadata',
                        success: false,
                        slot: {slot},
                        data: null
                    }});
                }}
            }}
        }} catch (error) {{
            console.error('Browser metadata failed:', error);
            if (window.scribeStorageCallback) {{
                window.scribeStorageCallback({{
                    type: 'metadata',
                    success: false,
                    slot: {slot},
                    data: null
                }});
            }}
        }}
        """

        return {
            'type': 'javascript',
            'code': js_code.strip()
        }

    def list_saves_with_metadata(self):
        """
        Return JavaScript command to list all saves with metadata.

        Returns:
            dict: Contains 'type': 'javascript' and 'code' with JS to execute
        """
        js_code = f"""
        try {{
            const saves = {{}};
            const prefix = '{self.project_prefix}slot_';

            // Check all 6 save slots
            for (let slot = 1; slot <= 6; slot++) {{
                const key = prefix + slot;
                const saveData = localStorage.getItem(key);

                if (saveData) {{
                    try {{
                        const parsed = JSON.parse(saveData);
                        saves[slot] = {{
                            slot: slot,
                            description: parsed.description || '',
                            passage_name: parsed.passage_name || parsed.game_state?.current_passage || 'Unknown',
                            timestamp: parsed.timestamp,
                            created_timestamp: parsed.created_timestamp,
                            playtime: parsed.playtime || 0,
                            version: parsed.version || '1.0',
                            engine_version: parsed.engine_version || '1.3'
                        }};
                    }} catch (parseError) {{
                        console.warn('Failed to parse save slot', slot, parseError);
                    }}
                }}
            }}

            if (window.scribeStorageCallback) {{
                window.scribeStorageCallback({{
                    type: 'list_saves',
                    success: true,
                    data: saves
                }});
            }}
        }} catch (error) {{
            console.error('Browser list saves failed:', error);
            if (window.scribeStorageCallback) {{
                window.scribeStorageCallback({{
                    type: 'list_saves',
                    success: false,
                    data: {{}}
                }});
            }}
        }}
        """

        return {
            'type': 'javascript',
            'code': js_code.strip()
        }

    def delete_save(self, slot):
        """
        Return JavaScript command to delete a save.

        Args:
            slot: Save slot number

        Returns:
            dict: Contains 'type': 'javascript' and 'code' with JS to execute
        """
        save_key = f"{self.project_prefix}slot_{slot}"

        js_code = f"""
        try {{
            localStorage.removeItem('{save_key}');

            if (window.scribeStorageCallback) {{
                window.scribeStorageCallback({{
                    type: 'delete',
                    success: true,
                    slot: {slot},
                    message: 'Save deleted from browser cache'
                }});
            }}
        }} catch (error) {{
            console.error('Browser delete failed:', error);
            if (window.scribeStorageCallback) {{
                window.scribeStorageCallback({{
                    type: 'delete',
                    success: false,
                    slot: {slot},
                    message: 'Failed to delete: ' + error.message
                }});
            }}
        }}
        """

        return {
            'type': 'javascript',
            'code': js_code.strip()
        }

    def export_save(self, slot):
        """
        Return JavaScript command to export save data.

        Args:
            slot: Save slot number

        Returns:
            dict: Contains 'type': 'javascript' and 'code' with JS to execute
        """
        save_key = f"{self.project_prefix}slot_{slot}"

        js_code = f"""
        try {{
            const saveData = localStorage.getItem('{save_key}');
            if (saveData) {{
                const parsed = JSON.parse(saveData);
                // Add export metadata
                parsed.exported_timestamp = new Date().toISOString();
                parsed.original_slot = {slot};

                // Create download
                const blob = new Blob([JSON.stringify(parsed, null, 2)], {{
                    type: 'application/json'
                }});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `scribe_save_slot_{slot}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);

                if (window.scribeStorageCallback) {{
                    window.scribeStorageCallback({{
                        type: 'export',
                        success: true,
                        slot: {slot},
                        message: 'Save exported successfully'
                    }});
                }}
            }} else {{
                if (window.scribeStorageCallback) {{
                    window.scribeStorageCallback({{
                        type: 'export',
                        success: false,
                        slot: {slot},
                        message: 'Save slot is empty'
                    }});
                }}
            }}
        }} catch (error) {{
            console.error('Browser export failed:', error);
            if (window.scribeStorageCallback) {{
                window.scribeStorageCallback({{
                    type: 'export',
                    success: false,
                    slot: {slot},
                    message: 'Failed to export: ' + error.message
                }});
            }}
        }}
        """

        return {
            'type': 'javascript',
            'code': js_code.strip()
        }

    def import_save(self, slot, save_data):
        """
        Return JavaScript command to import save data.
        This is typically called after user uploads a file.

        Args:
            slot: Save slot number
            save_data: Save data dictionary to import

        Returns:
            dict: Contains 'type': 'javascript' and 'code' with JS to execute
        """
        if not isinstance(save_data, dict) or 'game_state' not in save_data:
            return {
                'type': 'javascript',
                'code': f'''
                if (window.scribeStorageCallback) {{
                    window.scribeStorageCallback({{
                        type: 'import',
                        success: false,
                        slot: {slot},
                        message: 'Invalid save file format'
                    }});
                }}
                '''
            }

        # Update metadata for import
        save_data['timestamp'] = datetime.now().isoformat()
        save_data['imported_timestamp'] = datetime.now().isoformat()

        save_key = f"{self.project_prefix}slot_{slot}"
        save_json = json.dumps(save_data, default=str)

        js_code = f"""
        try {{
            const saveData = {save_json};
            localStorage.setItem('{save_key}', JSON.stringify(saveData));

            if (window.scribeStorageCallback) {{
                window.scribeStorageCallback({{
                    type: 'import',
                    success: true,
                    slot: {slot},
                    message: 'Save imported successfully'
                }});
            }}
        }} catch (error) {{
            console.error('Browser import failed:', error);
            if (window.scribeStorageCallback) {{
                window.scribeStorageCallback({{
                    type: 'import',
                    success: false,
                    slot: {slot},
                    message: 'Failed to import: ' + error.message
                }});
            }}
        }}
        """

        return {
            'type': 'javascript',
            'code': js_code.strip()
        }

    def validate_save(self, slot):
        """
        Return JavaScript command to validate save file.

        Args:
            slot: Save slot number

        Returns:
            dict: Contains 'type': 'javascript' and 'code' with JS to execute
        """
        save_key = f"{self.project_prefix}slot_{slot}"

        js_code = f"""
        try {{
            const saveData = localStorage.getItem('{save_key}');
            if (!saveData) {{
                if (window.scribeStorageCallback) {{
                    window.scribeStorageCallback({{
                        type: 'validate',
                        success: false,
                        slot: {slot},
                        message: 'Save file not found'
                    }});
                }}
                return;
            }}

            const parsed = JSON.parse(saveData);

            if (!parsed.game_state) {{
                if (window.scribeStorageCallback) {{
                    window.scribeStorageCallback({{
                        type: 'validate',
                        success: false,
                        slot: {slot},
                        message: 'Invalid save format: missing game_state'
                    }});
                }}
                return;
            }}

            if (typeof parsed.game_state !== 'object') {{
                if (window.scribeStorageCallback) {{
                    window.scribeStorageCallback({{
                        type: 'validate',
                        success: false,
                        slot: {slot},
                        message: 'Invalid save format: game_state is not an object'
                    }});
                }}
                return;
            }}

            if (window.scribeStorageCallback) {{
                window.scribeStorageCallback({{
                    type: 'validate',
                    success: true,
                    slot: {slot},
                    message: 'Save file is valid'
                }});
            }}
        }} catch (error) {{
            console.error('Browser validate failed:', error);
            if (window.scribeStorageCallback) {{
                window.scribeStorageCallback({{
                    type: 'validate',
                    success: false,
                    slot: {slot},
                    message: 'Failed to validate: ' + error.message
                }});
            }}
        }}
        """

        return {
            'type': 'javascript',
            'code': js_code.strip()
        }

    # Legacy compatibility methods
    def list_saves(self):
        """Legacy compatibility - returns JS to get save slot numbers."""
        return self.list_saves_with_metadata()