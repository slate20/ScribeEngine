"""
Scribe Engine Game Server
Minimal Flask server providing only game runtime functionality.
Used for standalone game distributions.
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, make_response
import os
import json
import sys
import logging
from datetime import datetime
from engine.core import GameEngine

# --- Flask App Setup ---

# Global variables for game project path and config, to be set externally
GAME_PROJECT_PATH = None
HARDCODED_CONFIG = None

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Suppress Werkzeug access logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app.secret_key = 'game-server-key'

# Template filters for formatting (copied from main app.py)
@app.template_filter('format_timestamp')
def format_timestamp(timestamp):
    """Format ISO timestamp for display."""
    if not timestamp:
        return 'Unknown'
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return str(timestamp)

@app.template_filter('format_playtime')  
def format_playtime(seconds):
    """Format playtime seconds into readable format."""
    if not seconds:
        return '0m'
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f'{hours}h {minutes}m'
    return f'{minutes}m'

# Initialize game engine
game_engine = None

def set_game_project_path(path):
    """Set the game project path and initialize the engine."""
    global GAME_PROJECT_PATH, game_engine
    GAME_PROJECT_PATH = path
    if path and os.path.exists(path):
        game_engine = GameEngine(path, debug_mode=False)  # Always disable debug in games
        
        # For distributed games, save files should go next to the executable, not in the bundled project
        if getattr(sys, 'frozen', False):
            # Running from executable - save next to the executable
            executable_dir = os.path.dirname(sys.executable)
            save_dir = os.path.join(executable_dir, 'saves')
        else:
            # Running from source - save in current working directory
            save_dir = os.path.join(os.getcwd(), 'saves')
        
        # Create save directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)
        
        # Replace the storage with one that uses the correct save directory
        from engine.storage import JSONStorage
        game_engine.storage = JSONStorage(save_dir=save_dir)
        print(f"Game saves will be stored in: {save_dir}")

def set_hardcoded_config(config):
    """Set hardcoded config for games without project.json files."""
    global HARDCODED_CONFIG
    HARDCODED_CONFIG = config

@app.before_request
def ensure_game_engine():
    """Ensure game engine is initialized before handling requests."""
    global game_engine, GAME_PROJECT_PATH
    
    # Skip initialization for certain paths
    if request.path in ['/shutdown'] or request.path.startswith('/static'):
        return
    
    if game_engine is None and GAME_PROJECT_PATH:
        try:
            game_engine = GameEngine(GAME_PROJECT_PATH, debug_mode=False)
        except Exception as e:
            print(f"Error initializing game engine: {e}")
            return f"Failed to initialize game: {e}", 500

# --- Game Routes (Essential for Gameplay) ---

@app.route('/')
def index():
    """Main game interface - renders the base template like main app.py does."""
    if not game_engine:
        return "Game not loaded", 500
    
    try:
        # Get navigation configuration
        nav_config = game_engine.config.get('nav', {'enabled': True, 'position': 'horizontal'})
        nav_content = ''
        if nav_config.get('enabled', False):
            nav_content = game_engine.render_special_passage('NavMenu')

        # Get theme configuration  
        theme_css = game_engine._generate_theme_css()
        use_engine_defaults = game_engine.theme_config.get('use_engine_defaults', True)
        
        return render_template('base.html',
                               game_title=game_engine.get_title(),
                               debug_mode=False,  # Always False for games
                               nav_config=nav_config,
                               nav_content=nav_content,
                               theme_css=theme_css,
                               use_engine_defaults=use_engine_defaults)
    except Exception as e:
        print(f"Error rendering game: {e}")
        return f"Error: {e}", 500

@app.route('/passage/<passage_name>')
def render_passage(passage_name):
    """Render a specific passage - returns HTML directly like main app.py does."""
    try:
        if passage_name not in game_engine.passages:
            return f'<div class="error">Passage "{passage_name}" not found</div>', 404
        
        # Update current passage in state
        game_engine.game_state['current_passage'] = passage_name
        
        # Return the rendered passage HTML directly (like main app.py does)
        html = game_engine.render_main_passage(passage_name)
        return html
    except Exception as e:
        print(f"Error rendering passage '{passage_name}': {e}")
        return f'<div class="error">Error rendering passage: {str(e)}</div>', 500

# --- Game State Management Routes ---

@app.route('/update_game_state', methods=['POST'])
def update_game_state():
    """Update game state from client."""
    try:
        data = request.get_json()
        if data and 'state' in data:
            game_engine.game_state.update(data['state'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/submit_input', methods=['POST'])
def submit_input():
    try:
        variable_name = request.form.get('variable_name')
        input_value = request.form.get('input_value')
        next_passage = request.form.get('next_passage') # Get next_passage
        
        if not variable_name:
            return "Error: variable_name is required.", 400
        
        # Handle dot notation for object attributes (e.g., 'player.name')
        if '.' in variable_name:
            parts = variable_name.split('.')
            current = game_engine.game_state
            
            # Navigate to the parent object
            for part in parts[:-1]:
                if part in current:
                    current = current[part]
                else:
                    # Create nested dict if it doesn't exist
                    current[part] = {}
                    current = current[part]
            
            # Set the final attribute/key
            final_key = parts[-1]
            if hasattr(current, final_key):
                # It's an object attribute
                setattr(current, final_key, input_value)
            else:
                # It's a dictionary key
                current[final_key] = input_value
        else:
            # Simple top-level assignment
            game_engine.game_state[variable_name] = input_value
        
        # Render the specified next_passage or the current one
        passage_to_render = next_passage if next_passage else game_engine.game_state.get('current_passage', 'start')
        html = game_engine.render_main_passage(passage_to_render)
        return html # HTMX expects HTML fragment
        
    except Exception as e:
        if game_engine.debug_mode:
            return f'<div class="debug-error">Error submitting input: {str(e)}</div>', 500
        return '<div class="error">Error submitting input: ' + str(e) + '</div>', 500

@app.route('/action_link', methods=['POST'])
def handle_action_link():
    try:
        action_string = request.form.get('action')
        target_passage = request.form.get('target_passage')

        if not all([action_string, target_passage]):
            return "Error: 'action' and 'target_passage' are required.", 400

        # TEMPORARY DIAGNOSTIC: Strip delimiters here to isolate the parser issue.
        if action_string.strip().startswith('{$') and action_string.strip().endswith('$}'):
            action_string = action_string.strip()[2:-2].strip()

        # Use the SafeExecutor to execute the action string as Python code.
        # The executor will directly modify the game_state.
        error = game_engine.executor.execute_code(action_string)
        
        # Prepend an error message to the next passage if one occurs
        error_html = ''
        if error and game_engine.debug_mode:
            error_html = f'<div class="debug-error">Error in link action: {error}</div>'

        # Render the target passage and return the HTML
        html = game_engine.render_main_passage(target_passage)
        return error_html + html

    except Exception as e:
        if game_engine.debug_mode:
            return f'<div class="debug-error">Error executing action link: {str(e)}</div>', 500
        return f'<div class="error">An error occurred while processing the action: {str(e)}</div>', 500

# --- Save/Load System Routes ---

@app.route('/save', methods=['POST'])
def save_game():
    try:
        slot = request.json.get('slot', 1)
        description = request.json.get('description', '')
        game_engine.save_game(slot, description)
        return jsonify({'status': 'success', 'message': 'Game saved'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500@app.route('/load', methods=['POST'])

@app.route('/load', methods=['POST'])
def load_game():
    try:
        slot = request.json.get('slot', 1)
        success = game_engine.load_game(slot)
        if success:
            current_passage = game_engine.game_state.get('current_passage', 'start')
            passage_html = game_engine.render_main_passage(current_passage)
            return jsonify({'status': 'success', 'message': 'Game loaded', 'passage_html': passage_html}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Save not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/saves')
def list_saves():
    """List all saved games."""
    saves = game_engine.list_saves()
    return jsonify(saves)

@app.route('/saves/metadata')
def get_saves_metadata():
    """Get all saves with their metadata for the save/load modals."""
    try:
        metadata = game_engine.storage.list_saves_with_metadata()
        return jsonify(metadata)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/saves/<int:slot>/delete', methods=['POST'])
def delete_save(slot):
    """Delete a specific save slot."""
    try:
        success = game_engine.storage.delete_save(slot)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/saves/<int:slot>/export')
def export_save(slot):
    """Export a save file for download."""
    try:
        save_path = game_engine.storage.get_save_path(slot)
        if os.path.exists(save_path):
            filename = f"game_save_{slot}.json"
            return send_file(save_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'Save file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/saves/<int:slot>/import', methods=['POST'])
def import_save(slot):
    """Import a save file."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read and validate the save file
        save_data = json.loads(file.read().decode('utf-8'))
        success = game_engine.storage.import_save(slot, save_data)
        
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/saves/<int:slot>/validate')
def validate_save(slot):
    """Validate a save file's integrity."""
    try:
        is_valid = game_engine.storage.validate_save(slot)
        return jsonify({'valid': is_valid})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Save/Load Modal Routes ---

@app.route('/modal/save')
def get_save_modal():
    """Get the save modal with current save data."""
    try:
        current_passage = game_engine.game_state.get('current_passage', 'unknown')
        saves = game_engine.storage.list_saves_with_metadata()
        
        return render_template('_fragments/_htmx_save_modal.html', saves=saves)
    except Exception as e:
        return f"Error loading save modal: {e}", 500

@app.route('/modal/load')
def get_load_modal():
    """Get the load modal with available saves."""
    try:
        saves = game_engine.storage.list_saves_with_metadata()
        # Filter to only populated saves for loading
        populated_saves = {slot: info for slot, info in saves.items() if info}
        
        return render_template('_fragments/_htmx_load_modal.html', 
                             saves=saves, populated_saves=populated_saves)
    except Exception as e:
        return f"Error loading load modal: {e}", 500

@app.route('/modal/save/select', methods=['POST'])
def select_save_slot():
    """Handle save slot selection."""
    try:
        slot = int(request.form.get('slot', 1))
        current_passage = game_engine.game_state.get('current_passage', 'unknown')
        saves = game_engine.storage.list_saves_with_metadata()
        
        return render_template('_fragments/_save_details.html',
                             slot=slot,
                             current_passage=current_passage,
                             saves=saves)
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/modal/load/select', methods=['POST'])
def select_load_slot():
    """Handle load slot selection."""
    try:
        slot = int(request.form.get('slot', 1))
        saves = game_engine.storage.list_saves_with_metadata()
        save_info = saves.get(slot)
        
        return render_template('_fragments/_load_details.html',
                             slot=slot, save_info=save_info)
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/modal/save/confirm', methods=['POST'])
def confirm_save():
    """Handle save confirmation."""
    try:
        slot = int(request.form.get('slot', 1))
        description = request.form.get('description', '').strip()
        
        success = game_engine.save_game(slot, description)
        if success:
            return jsonify({'success': True, 'message': f'Game saved to slot {slot}'})
        else:
            return jsonify({'success': False, 'error': 'Failed to save game'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/modal/load/confirm', methods=['POST'])
def confirm_load():
    """Handle load confirmation - returns the loaded game content HTML directly."""
    try:
        slot = int(request.form.get('slot', 1))
        
        success = game_engine.load_game(slot)
        if success:
            # Return the rendered passage HTML directly (like main app.py does)
            current_passage = game_engine.game_state.get('current_passage', game_engine.state_manager.starting_passage)
            passage_html = game_engine.render_main_passage(current_passage)
            return passage_html
        else:
            return '<div class="error">Failed to load game</div>', 500
    except Exception as e:
        return f'<div class="error">Error loading game: {str(e)}</div>', 500

@app.route('/modal/close', methods=['POST'])
def close_modal():
    """Close any open modal."""
    return '', 200

# --- Asset and Styling Routes ---

@app.route('/custom.css')
def serve_custom_css():
    """Serve custom CSS from the game project."""
    if not game_engine:
        return '', 404
    
    custom_css_path = os.path.join(game_engine.project_path, 'custom.css')
    if os.path.exists(custom_css_path):
        return send_file(custom_css_path, mimetype='text/css')
    else:
        # Return empty CSS if no custom stylesheet exists
        response = make_response('/* No custom CSS */')
        response.headers['Content-Type'] = 'text/css'
        return response

@app.route('/game/assets/<path:filename>')
def serve_project_asset(filename):
    """Serve assets from the game project."""
    if not game_engine:
        return '', 404
    
    # Look for assets in the bundled game_data directory structure
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # In bundled executable, assets are in game_data/<project_name>/assets
        base_path = sys._MEIPASS
        game_data_path = os.path.join(base_path, 'game_data')
        if os.path.exists(game_data_path):
            project_dirs = [d for d in os.listdir(game_data_path) if os.path.isdir(os.path.join(game_data_path, d))]
            if project_dirs:
                assets_path = os.path.join(game_data_path, project_dirs[0], 'assets')
            else:
                assets_path = os.path.join(game_engine.project_path, 'assets')
        else:
            assets_path = os.path.join(game_engine.project_path, 'assets')
    else:
        # Development mode
        assets_path = os.path.join(game_engine.project_path, 'assets')
    
    file_path = os.path.join(assets_path, filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return '', 404

# --- Shutdown Route ---

@app.route('/shutdown', methods=['GET', 'POST'])
def shutdown():
    """Shutdown the server."""
    def shutdown_server():
        import time
        time.sleep(0.1)  # Brief delay to allow response to be sent
        os._exit(0)
    
    import threading
    threading.Thread(target=shutdown_server).start()
    return jsonify({'message': 'Server shutting down...'})

if __name__ == "__main__":
    # This should only be used for testing - in production, use game_server_wrapper.py
    app.run(host='127.0.0.1', port=5001, debug=False)
