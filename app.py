from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, make_response
import os
import json
import sys
import argparse
import shutil
import config_manager
import glob
from datetime import datetime
from jinja2 import Environment
from engine.core import GameEngine

# Add these imports for graceful shutdown
from werkzeug.serving import make_server
import threading
import time # Needed for time.sleep

# --- Flask App Setup ---

# Global variable for game project path, to be set externally
GAME_PROJECT_PATH = None
active_project_path = None

# Flag to indicate if running in GUI mode
_gui_mode = False

def set_gui_mode(enabled: bool):
    """Sets the GUI mode flag."""
    global _gui_mode
    _gui_mode = enabled

def set_game_project_path(path):
    global GAME_PROJECT_PATH
    GAME_PROJECT_PATH = path

import logging

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Suppress Werkzeug access logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app.secret_key = 'your-secret-key-here'  # Change in production

# Template filters for formatting
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

# Initialize game engine (will be done after GAME_PROJECT_PATH is set)
game_engine = None
_app_debug_mode = True # Default to False for production
_temp_game_state = None # New global variable to store temporary game state

# Add a server object to manage the Flask server instance
server = None

# Asset packing functionality (replaces old external build system)
build_status = {}  # Global build status tracking

def set_debug_mode(mode: bool):
    global _app_debug_mode
    _app_debug_mode = mode

def reset_game_engine():
    """Resets the global game engine instance to force re-initialization."""
    global game_engine
    game_engine = None
    print("Game engine has been reset. It will be re-initialized on the next request.")

@app.before_request
def initialize_game_engine():
    global game_engine, GAME_PROJECT_PATH

    # If in GUI mode, engine is initialized on project load, not automatically.
    if _gui_mode:
        return

    # Skip initialization if the request is for shutdown or a GUI route
    if request.path == '/shutdown' or request.path.startswith('/gui') or request.path.startswith('/api') or request.path.startswith('/static') or request.path.startswith('/favicon.ico'):
        return

    # Prioritize environment variable for GAME_PROJECT_PATH
    if os.environ.get('SCRIBE_ENGINE_GAME_PROJECT_PATH') and GAME_PROJECT_PATH is None:
        GAME_PROJECT_PATH = os.environ.get('SCRIBE_ENGINE_GAME_PROJECT_PATH')

    if game_engine is None:
        if GAME_PROJECT_PATH is None:
            # Fallback for direct app.py run without launcher/wrapper
            default_path = os.path.join(os.path.dirname(__file__), 'game')
            print(f"WARNING: GAME_PROJECT_PATH not set. Using default: {default_path}")
            set_game_project_path(default_path)
        game_engine = GameEngine(GAME_PROJECT_PATH, debug_mode=_app_debug_mode)

# --- Routes ---

@app.route('/')
def index():
    # In GUI mode, if no project is loaded, show a message.
    if _gui_mode and game_engine is None:
        return "<h1>No project loaded</h1><p>Please select a project from the Scribe Engine launcher.</p>"

    nav_config = game_engine.config.get('nav', {'enabled': True, 'position': 'horizontal'})
    nav_content = ''

    theme_css = game_engine._generate_theme_css()
    use_engine_defaults = game_engine.theme_config.get('use_engine_defaults', True)

    # Only pass necessary config values to avoid exposing sensitive data
    safe_config = {
        'features': {
            'save_system': game_engine.config.get('features', {}).get('save_system', 'server')
        }
    }

    return render_template('base.html',
                         game_title=game_engine.get_title(),
                         debug_mode=game_engine.debug_mode,
                         nav_config=nav_config,
                         nav_content=nav_content,
                         theme_css=theme_css,
                         use_engine_defaults=use_engine_defaults,
                         features=game_engine.config.get('features', {}),
                         config=safe_config,
                         project_name=os.path.basename(game_engine.project_path))

@app.route('/passage/<passage_name>')
def render_passage(passage_name):
    try:
        html = game_engine.render_main_passage(passage_name)
        return html
    except Exception as e:
        if game_engine.debug_mode:
            return f'<div class="debug-error">Error rendering passage: {str(e)}</div>'
        return '<div class="error">Passage not found</div>'

@app.route('/save', methods=['POST'])
def save_game():
    try:
        slot = request.json.get('slot', 1)
        description = request.json.get('description', '')

        if hasattr(game_engine, 'is_browser_storage') and game_engine.is_browser_storage:
            # Browser storage mode - return JavaScript to execute
            current_passage = game_engine.game_state.get('current_passage', 'Unknown')
            serializable_state = game_engine.get_serializable_state()
            js_result = game_engine.storage.save_game(slot, serializable_state, description, current_passage)
            return jsonify(js_result), 200
        else:
            # Server storage mode - execute save directly
            game_engine.save_game(slot, description)
            return jsonify({'status': 'success', 'message': 'Game saved'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/load', methods=['POST'])
def load_game():
    try:
        slot = request.json.get('slot', 1)

        if hasattr(game_engine, 'is_browser_storage') and game_engine.is_browser_storage:
            # Browser storage mode - return JavaScript to execute
            js_result = game_engine.storage.load_game(slot)
            return jsonify(js_result), 200
        else:
            # Server storage mode - execute load directly
            success = game_engine.load_game(slot)
            if success:
                current_passage = game_engine.game_state.get('current_passage', 'start')
                passage_html = game_engine.render_main_passage(current_passage)
                return jsonify({'status': 'success', 'message': 'Game loaded', 'passage_html': passage_html}), 200
            else:
                return jsonify({'status': 'error', 'message': 'Save not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/browser-storage/load-complete', methods=['POST'])
def browser_load_complete():
    """Handle browser storage load completion - process loaded data from localStorage."""
    try:
        data = request.get_json()
        slot = data.get('slot')
        save_data = data.get('save_data')

        if not save_data or 'game_state' not in save_data:
            return jsonify({'status': 'error', 'message': 'Invalid save data'}), 400

        # Restore the game state
        game_engine.restore_state_from_dict(save_data['game_state'])

        # Render current passage
        current_passage = game_engine.game_state.get('current_passage', 'start')
        passage_html = game_engine.render_main_passage(current_passage)

        return jsonify({
            'status': 'success',
            'message': 'Game loaded from browser cache',
            'passage_html': passage_html
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/update_game_state', methods=['POST'])
def update_game_state():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No JSON data provided'}), 400

        next_passage = data.pop('next_passage', None) # Extract next_passage if present

        game_engine.update_state_from_json(data)

        if next_passage:
            passage_html = game_engine.render_main_passage(next_passage)
            return jsonify({'status': 'success', 'message': 'Game state updated', 'passage_html': passage_html}), 200
        else:
            return jsonify({'status': 'success', 'message': 'Game state updated'}), 200

    except Exception as e:
        if game_engine.debug_mode:
            return jsonify({'status': 'error', 'message': f'Error updating game state: {str(e)}'}), 500
        return jsonify({'status': 'error', 'message': 'Error updating game state'}), 500

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
        context_encoded = request.form.get('context', '')

        if not all([action_string, target_passage]):
            return "Error: 'action' and 'target_passage' are required.", 400

        # TEMPORARY DIAGNOSTIC: Strip delimiters here to isolate the parser issue.
        if action_string.strip().startswith('{$') and action_string.strip().endswith('$}'):
            action_string = action_string.strip()[2:-2].strip()

        # Decode context data if present
        context_data = {}
        if context_encoded:
            try:
                import json
                import base64
                context_json = base64.b64decode(context_encoded.encode('utf-8')).decode('utf-8')
                serialized_context = json.loads(context_json)

                # Restore context objects
                for key, value in serialized_context.items():
                    context_data[key] = game_engine._auto_restore_object(value)

                if game_engine.debug_mode:
                    print(f"Restored context for action: {list(context_data.keys())}")
            except Exception as e:
                if game_engine.debug_mode:
                    print(f"Warning: Failed to decode context data: {e}")

        # Use the context-aware executor to execute the action string
        error = game_engine.executor.execute_code_with_context(action_string, context_data)
        
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

@app.route('/saves')
def list_saves():
    saves = game_engine.list_saves()
    return jsonify({'saves': saves})

@app.route('/saves/metadata')
def get_saves_metadata():
    """Get all saves with their metadata for the save/load modals."""
    try:
        if game_engine is None:
            return jsonify({'status': 'error', 'message': 'No game project loaded'}), 400

        if hasattr(game_engine, 'is_browser_storage') and game_engine.is_browser_storage:
            # Browser storage mode - return JavaScript to execute
            js_result = game_engine.storage.list_saves_with_metadata()
            return jsonify(js_result), 200
        else:
            # Server storage mode - get saves directly
            saves = game_engine.storage.list_saves_with_metadata()
            return jsonify({'status': 'success', 'saves': saves}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/saves/<int:slot>/delete', methods=['POST'])
def delete_save(slot):
    """Delete a specific save slot."""
    try:
        if hasattr(game_engine, 'is_browser_storage') and game_engine.is_browser_storage:
            # Browser storage mode - return JavaScript to execute
            js_result = game_engine.storage.delete_save(slot)
            return jsonify(js_result), 200
        else:
            # Server storage mode - delete directly
            success = game_engine.storage.delete_save(slot)
            if success:
                return jsonify({'status': 'success', 'message': 'Save deleted'}), 200
            else:
                return jsonify({'status': 'error', 'message': 'Save not found or could not be deleted'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/saves/<int:slot>/export')
def export_save(slot):
    """Export a save file for download."""
    try:
        if hasattr(game_engine, 'is_browser_storage') and game_engine.is_browser_storage:
            # Browser storage mode - return JavaScript to execute
            js_result = game_engine.storage.export_save(slot)
            return jsonify(js_result), 200
        else:
            # Server storage mode - create download response
            save_data = game_engine.storage.export_save(slot)
            if save_data:
                from flask import Response
                response_data = json.dumps(save_data, indent=2, default=str)
                response = Response(
                    response_data,
                    mimetype='application/json',
                    headers={
                        'Content-Disposition': f'attachment; filename=save_slot_{slot}.json'
                    }
                )
                return response
            else:
                return jsonify({'status': 'error', 'message': 'Save not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/saves/<int:slot>/import', methods=['POST'])
def import_save(slot):
    """Import a save file."""
    try:
        if hasattr(game_engine, 'is_browser_storage') and game_engine.is_browser_storage:
            # Browser storage mode - expect JSON data directly (from JavaScript)
            save_data = request.get_json()
            if not save_data:
                return jsonify({'status': 'error', 'message': 'No save data provided'}), 400

            js_result = game_engine.storage.import_save(slot, save_data)
            return jsonify(js_result), 200
        else:
            # Server storage mode - handle file upload
            if 'file' not in request.files:
                return jsonify({'status': 'error', 'message': 'No file provided'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'status': 'error', 'message': 'No file selected'}), 400

            if not file.filename.endswith('.json'):
                return jsonify({'status': 'error', 'message': 'Invalid file type. Please upload a JSON file'}), 400

            save_data = json.loads(file.read().decode('utf-8'))
            success = game_engine.storage.import_save(slot, save_data)

            if success:
                return jsonify({'status': 'success', 'message': 'Save imported successfully'}), 200
            else:
                return jsonify({'status': 'error', 'message': 'Invalid save file format'}), 400

    except json.JSONDecodeError:
        return jsonify({'status': 'error', 'message': 'Invalid JSON file'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/saves/<int:slot>/validate')
def validate_save(slot):
    """Validate a save file's integrity."""
    try:
        if hasattr(game_engine, 'is_browser_storage') and game_engine.is_browser_storage:
            # Browser storage mode - return JavaScript to execute
            js_result = game_engine.storage.validate_save(slot)
            return jsonify(js_result), 200
        else:
            # Server storage mode - validate directly
            is_valid, message = game_engine.storage.validate_save(slot)
            return jsonify({
                'status': 'success' if is_valid else 'error',
                'valid': is_valid,
                'message': message
            }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# HTMX Modal Routes
@app.route('/modal/save')
def get_save_modal():
    """Get the save modal with current save data."""
    try:
        if game_engine is None:
            return '<div class="error">No game project loaded</div>', 400
        
        if hasattr(game_engine, 'is_browser_storage') and game_engine.is_browser_storage:
            # Browser storage mode - render modal with empty saves, JavaScript will populate it
            safe_config = {
                'features': {
                    'save_system': game_engine.config.get('features', {}).get('save_system', 'server')
                }
            }
            modal_html = render_template('_fragments/_htmx_save_modal.html', saves={}, config=safe_config, project_name=os.path.basename(game_engine.project_path))

            # Get JavaScript to list saves
            js_result = game_engine.storage.list_saves_with_metadata()

            # Return modal with embedded JavaScript to populate saves
            return f'''
            {modal_html}
            <script>
                console.log('Loading browser storage save modal');
                // Execute JavaScript to populate save list
                {js_result['code']}
            </script>
            '''
        else:
            # Server storage mode - get saves directly
            saves = game_engine.storage.list_saves_with_metadata()
            safe_config = {
                'features': {
                    'save_system': game_engine.config.get('features', {}).get('save_system', 'server')
                }
            }
            return render_template('_fragments/_htmx_save_modal.html', saves=saves, config=safe_config, project_name=os.path.basename(game_engine.project_path))
    except Exception as e:
        return f'<div class="error">Error loading save modal: {str(e)}</div>', 500

@app.route('/modal/load')
def get_load_modal():
    """Get the load modal with available saves."""
    try:
        if game_engine is None:
            return '<div class="error">No game project loaded</div>', 400
        
        if hasattr(game_engine, 'is_browser_storage') and game_engine.is_browser_storage:
            # Browser storage mode - render modal with empty saves, JavaScript will populate it
            safe_config = {
                'features': {
                    'save_system': game_engine.config.get('features', {}).get('save_system', 'server')
                }
            }
            modal_html = render_template('_fragments/_htmx_load_modal.html', saves={}, populated_saves={}, config=safe_config, project_name=os.path.basename(game_engine.project_path))

            # Get JavaScript to list saves
            js_result = game_engine.storage.list_saves_with_metadata()

            # Return modal with embedded JavaScript to populate saves
            return f'''
            {modal_html}
            <script>
                console.log('Loading browser storage load modal');
                // Execute JavaScript to populate save list
                {js_result['code']}
            </script>
            '''
        else:
            # Server storage mode - get saves directly
            saves = game_engine.storage.list_saves_with_metadata()
            # Filter to only populated saves for loading
            populated_saves = {slot: info for slot, info in saves.items() if info}

            safe_config = {
                'features': {
                    'save_system': game_engine.config.get('features', {}).get('save_system', 'server')
                }
            }
            return render_template('_fragments/_htmx_load_modal.html',
                                 saves=saves, populated_saves=populated_saves, config=safe_config, project_name=os.path.basename(game_engine.project_path))
    except Exception as e:
        return f'<div class="error">Error loading load modal: {str(e)}</div>', 500

@app.route('/modal/save/select', methods=['POST'])
def select_save_slot():
    """Handle save slot selection."""
    try:
        if game_engine is None:
            return '<div class="error">No game project loaded</div>', 400
            
        slot = int(request.form.get('slot', 1))
        current_passage = game_engine.game_state.get('current_passage', 'Unknown')
        
        # Get existing save info if any
        existing_save = game_engine.storage.get_save_metadata(slot)
        existing_description = existing_save.get('description', '') if existing_save else ''
        
        return render_template('_fragments/_save_details.html',
                             slot=slot,
                             current_passage=current_passage,
                             existing_save=existing_save,
                             existing_description=existing_description)
    except Exception as e:
        return f'<div class="error">Error selecting save slot: {str(e)}</div>', 500

@app.route('/modal/load/select', methods=['POST'])
def select_load_slot():
    """Handle load slot selection."""
    try:
        if game_engine is None:
            return '<div class="error">No game project loaded</div>', 400
            
        slot = int(request.form.get('slot', 1))

        if hasattr(game_engine, 'is_browser_storage') and game_engine.is_browser_storage:
            # Browser storage mode - get metadata via JavaScript
            js_result = game_engine.storage.get_save_metadata(slot)

            return f'''
            <script>
                console.log('Getting save metadata for slot {slot}');
                // Execute JavaScript to get save metadata
                {js_result['code']}
            </script>
            <div id="load-details-placeholder">Loading save details...</div>
            '''
        else:
            # Server storage mode - get metadata directly
            save_info = game_engine.storage.get_save_metadata(slot)

            if not save_info:
                return '<div class="error">Save not found</div>', 404

            return render_template('_fragments/_load_details.html',
                                 slot=slot, save_info=save_info)
    except Exception as e:
        return f'<div class="error">Error selecting load slot: {str(e)}</div>', 500

@app.route('/modal/save/confirm', methods=['POST'])
def confirm_save():
    """Handle save confirmation."""
    try:
        if game_engine is None:
            return '<div class="error">No game project loaded</div>', 400
            
        slot = int(request.form.get('slot', 1))
        description = request.form.get('save-description', '').strip()

        if hasattr(game_engine, 'is_browser_storage') and game_engine.is_browser_storage:
            # Browser storage mode - get JavaScript and execute it
            current_passage = game_engine.game_state.get('current_passage', 'Unknown')
            serializable_state = game_engine.get_serializable_state()
            js_result = game_engine.storage.save_game(slot, serializable_state, description, current_passage)

            # Return HTML with embedded JavaScript execution
            return f'''
            <div class="success-message">Game saved successfully!</div>
            <script>
                console.log('Executing browser storage save from modal confirm');
                // Execute the storage JavaScript
                {js_result['code']}

                // Close modal after short delay
                setTimeout(() => {{
                    document.getElementById('modal-container').innerHTML = '';
                }}, 1500);
            </script>
            '''
        else:
            # Server storage mode - normal save
            game_engine.save_game(slot, description)

            # Return success message and close modal
            return '''
            <div class="success-message">Game saved successfully!</div>
            <script>
                setTimeout(() => {
                    document.getElementById('modal-container').innerHTML = '';
                }, 1500);
            </script>
            '''
    except Exception as e:
        return f'<div class="error">Error saving game: {str(e)}</div>', 500

@app.route('/modal/load/confirm', methods=['POST'])
def confirm_load():
    """Handle load confirmation - returns the loaded game content."""
    try:
        if game_engine is None:
            return '<div class="error">No game project loaded</div>', 400
            
        slot = int(request.form.get('slot', 1))

        if hasattr(game_engine, 'is_browser_storage') and game_engine.is_browser_storage:
            # Browser storage mode - return JavaScript to load from localStorage
            # The JavaScript will handle loading and sending data back to server
            js_result = game_engine.storage.load_game(slot)

            return f'''
            <script>
                console.log('Executing browser storage load from modal confirm');
                // Execute the storage JavaScript which will call scribeStorageCallback
                {js_result['code']}

                // Close modal - the callback will handle the actual game loading
                setTimeout(() => {{
                    document.getElementById('modal-container').innerHTML = '';
                }}, 500);
            </script>
            '''
        else:
            # Server storage mode - normal load
            success = game_engine.load_game(slot)

            if success:
                current_passage = game_engine.game_state.get('current_passage', 'start')
                passage_html = game_engine.render_main_passage(current_passage)
                return passage_html
            else:
                return '<div class="error">Failed to load game</div>', 500
    except Exception as e:
        return f'<div class="error">Error loading game: {str(e)}</div>', 500

@app.route('/modal/close', methods=['POST'])
def close_modal():
    """Close any open modal."""
    return ''  # Return empty content to clear modal container

@app.route('/modal/new-file/<project_name>/<category>')
def new_file_modal(project_name, category):
    """Show new file modal with category context."""
    category_config = {
        'story': {
            'title': 'New Story File',
            'extension': '.tgame',
            'placeholder': 'story_scene',
            'hint': 'Enter filename without extension (will add .tgame automatically)'
        },
        'logic': {
            'title': 'New Logic File',
            'extension': '.py',
            'placeholder': 'game_logic',
            'hint': 'Enter filename without extension (will add .py automatically)'
        },
        'css': {
            'title': 'New CSS File',
            'extension': '.css',
            'placeholder': 'custom_styles',
            'hint': 'Enter filename without extension (will add .css automatically)'
        }
    }

    config = category_config.get(category, category_config['story'])
    return render_template('_fragments/_htmx_new_file_modal.html',
                         project_name=project_name,
                         category=category,
                         config=config)

@app.route('/modal/rename-file/<project_name>/<path:file_path>')
def rename_file_modal(project_name, file_path):
    """Show rename file modal with current file info."""
    # Extract filename and extension from path
    filename_with_ext = os.path.basename(file_path)
    filename, extension = os.path.splitext(filename_with_ext)

    return render_template('_fragments/_htmx_rename_file_modal.html',
                         project_name=project_name,
                         current_path=file_path,
                         current_filename=filename,
                         extension=extension)

@app.route('/api/subdirectories/<project_name>/<category>')
def get_subdirectories(project_name, category):
    """Get existing subdirectories for a specific category."""
    project_root = config_manager.get_project_root()
    project_path = os.path.join(project_root, project_name)

    if not os.path.isdir(project_path):
        return jsonify({'status': 'error', 'message': 'Project not found'}), 404

    # Map categories to file extensions and base directories
    category_mapping = {
        'story': {'extensions': ['*.tgame'], 'base_dir': ''},
        'logic': {'extensions': ['*.py'], 'base_dir': ''},
        'css': {'extensions': ['*.css'], 'base_dir': ''}
    }

    if category not in category_mapping:
        return jsonify({'status': 'error', 'message': 'Invalid category'}), 400

    mapping = category_mapping[category]
    directories = set()

    # Find all files of this type and extract their directories
    for extension in mapping['extensions']:
        pattern = os.path.join(project_path, '**', extension)
        files = glob.glob(pattern, recursive=True)

        for file_path in files:
            rel_path = os.path.relpath(file_path, project_path)
            dir_name = os.path.dirname(rel_path)
            if dir_name and dir_name != '.':
                directories.add(dir_name.replace('\\', '/'))

    # Sort directories and add root option
    sorted_dirs = [''] + sorted(list(directories))  # Empty string represents root

    return jsonify({'status': 'success', 'directories': sorted_dirs})

@app.route('/modal/new-folder/<project_name>')
def new_folder_modal(project_name):
    """Show new folder modal."""
    return render_template('_fragments/_htmx_new_folder_modal.html', project_name=project_name)

@app.route('/game_theme.css')
def serve_game_theme_css():
    game_theme_css_path = os.path.join(game_engine.project_path, 'game_theme.css')
    if os.path.exists(game_theme_css_path):
        return send_file(game_theme_css_path, mimetype='text/css')
    return '', 404

# Backward compatibility route for existing projects
@app.route('/custom.css')
def serve_custom_css():
    custom_css_path = os.path.join(game_engine.project_path, 'custom.css')
    if os.path.exists(custom_css_path):
        return send_file(custom_css_path, mimetype='text/css')
    # If custom.css doesn't exist, try game_theme.css as fallback
    game_theme_css_path = os.path.join(game_engine.project_path, 'game_theme.css')
    if os.path.exists(game_theme_css_path):
        return send_file(game_theme_css_path, mimetype='text/css')
    return '', 404

# GUI routes
# New route for the main GUI launcher page
@app.route('/gui')
def gui_launcher():
    return render_template('launcher.html', project_root=config_manager.get_project_root())

@app.route('/api/startup-screen')
def get_startup_screen():
    return render_template('_fragments/_startup_screen.html')

# New route to list projects as an HTMX fragment
@app.route('/api/projects')
def list_projects_fragment():
    project_root = config_manager.get_project_root()
    projects = [d for d in os.listdir(project_root) if os.path.isdir(os.path.join(project_root, d))]
    projects.sort()
    return render_template('_fragments/_project_list.html', projects=projects)

# New route for the project-specific menu fragment
@app.route('/api/project-menu/<project_name>')
def project_menu_fragment(project_name):
    return render_template('_fragments/_project_menu.html', project_name=project_name)

# Route for the new project form
@app.route('/api/new-project-form')
def new_project_form():
    return render_template('_fragments/_new_project_form.html')

# New route to handle project creation from the GUI
@app.route('/api/new-project', methods=['POST'])
def create_project_api():
    from main_engine import create_new_project
    
    # Check the Content-Type to determine how to parse the data
    content_type = request.headers.get('Content-Type')
    if content_type and 'application/json' in content_type:
        data = request.get_json()
    else:
        data = request.form
    
    project_name = data.get('project_name')
    project_root = config_manager.get_project_root()
    
    if not project_name:
        return jsonify({'status': 'error', 'message': 'Project name is required'}), 400
        
    project_path = os.path.join(project_root, project_name)
    if os.path.exists(project_path):
        return jsonify({'status': 'error', 'message': 'Project already exists'}), 409
        
    create_new_project(project_name, project_root)
    
    return jsonify({'status': 'success', 'message': project_name}), 200
# New route to handle opening the editor for a project
@app.route('/api/open-editor/<project_name>')
def open_editor(project_name):
    global active_project_path, game_engine
    project_root = config_manager.get_project_root()
    active_project_path = os.path.join(project_root, project_name)
    set_game_project_path(active_project_path)
    
    # Initialize the game engine for the selected project
    # Read project.json to get debug_mode for this project
    project_config_path = os.path.join(active_project_path, 'project.json')
    project_debug_mode = True
    if os.path.exists(project_config_path):
        with open(project_config_path, 'r') as f:
            project_config = json.load(f)
            project_debug_mode = project_config.get('debug_mode', False)

    game_engine = GameEngine(active_project_path, debug_mode=project_debug_mode)

    return render_template('editor.html', project_name=project_name, project_root=project_root)

def group_files_by_directory(files):
    """Groups files by their directory structure, separating root files."""
    groups = {}
    root_files = []

    for file_path in files:
        dir_name = os.path.dirname(file_path)

        if not dir_name:  # Root file
            root_files.append({
                'filename': os.path.basename(file_path),
                'full_path': file_path,
                'relative_path': file_path
            })
        else:  # File in subdirectory
            if dir_name not in groups:
                groups[dir_name] = []
            groups[dir_name].append({
                'filename': os.path.basename(file_path),
                'full_path': file_path,
                'relative_path': file_path
            })

    # Sort files within each group and root files
    for group in groups.values():
        group.sort(key=lambda x: x['filename'])
    root_files.sort(key=lambda x: x['filename'])

    return groups, root_files

def group_asset_files_by_directory(asset_files):
    """Groups asset files by their directory structure, stripping 'assets/' prefix from group names."""
    groups = {}
    root_files = []

    for file_path in asset_files:
        # Strip 'assets/' prefix from the path for grouping purposes
        if file_path.startswith('assets/'):
            relative_path = file_path[7:]  # Remove 'assets/' prefix
        else:
            relative_path = file_path

        dir_name = os.path.dirname(relative_path)

        if not dir_name:  # Root asset file (directly in assets/)
            root_files.append({
                'filename': os.path.basename(file_path),
                'full_path': file_path,
                'relative_path': file_path
            })
        else:  # Asset file in subdirectory
            if dir_name not in groups:
                groups[dir_name] = []
            groups[dir_name].append({
                'filename': os.path.basename(file_path),
                'full_path': file_path,
                'relative_path': file_path
            })

    # Sort files within each group and root files
    for group in groups.values():
        group.sort(key=lambda x: x['filename'])
    root_files.sort(key=lambda x: x['filename'])

    return groups, root_files

@app.route('/api/files/<project_name>')
def list_files(project_name):
    """Lists all files in the project directory, grouped by type."""
    project_root = config_manager.get_project_root()
    project_path = os.path.join(project_root, project_name)

    if not os.path.isdir(project_path):
        return "Project not found", 404

    # Add .replace() to normalize paths here
    story_files = [os.path.relpath(f, project_path).replace('\\', '/') for f in glob.glob(f"{project_path}/**/*.tgame", recursive=True)]
    logic_files = [os.path.relpath(f, project_path).replace('\\', '/') for f in glob.glob(f"{project_path}/**/*.py", recursive=True)]
    config_files = [os.path.relpath(f, project_path).replace('\\', '/') for f in glob.glob(f"{project_path}//**.json", recursive=True) if os.path.basename(f) != 'project.json']
    css_files = [os.path.relpath(f, project_path).replace('\\', '/') for f in glob.glob(f"{project_path}/**/*.css", recursive=True)]
    asset_files = [os.path.relpath(f, project_path).replace('\\', '/') for f in glob.glob(f"{project_path}/assets/**/*", recursive=True) if os.path.isfile(f)]

    # Group files by directory
    story_groups, story_root_files = group_files_by_directory(story_files)
    logic_groups, logic_root_files = group_files_by_directory(logic_files)
    css_groups, css_root_files = group_files_by_directory(css_files)
    asset_groups, asset_root_files = group_asset_files_by_directory(asset_files)

    return render_template('_fragments/_file_list.html',
                           story_groups=story_groups,
                           story_root_files=story_root_files,
                           logic_groups=logic_groups,
                           logic_root_files=logic_root_files,
                           config_files=sorted(config_files),
                           asset_groups=asset_groups,
                           asset_root_files=asset_root_files,
                           project_name=project_name,
                           css_groups=css_groups,
                           css_root_files=css_root_files)

@app.route('/api/create-item/<project_name>', methods=['POST'])
def create_item(project_name):
    project_root = config_manager.get_project_root()
    data = request.form
    item_path = data.get('path')
    item_type = data.get('type') # 'file' or 'folder'

    if not all([item_path, item_type]):
        # In a real app, you'd return an error message to the user
        return list_files(project_name) # For simplicity, just refresh the list

    # Basic security check
    if ".." in item_path or os.path.isabs(item_path):
        print(f"SECURITY: Invalid path requested: {item_path}")
        return list_files(project_name)

    full_path = os.path.join(project_root, project_name, item_path)

    if os.path.exists(full_path):
        print(f"INFO: Item already exists at {full_path}")
        return list_files(project_name)

    try:
        if item_type == 'folder':
            os.makedirs(full_path)
        elif item_type == 'file':
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write("") # Create an empty file
    except Exception as e:
        print(f"ERROR: Could not create item {full_path}. Reason: {e}")

    # After action, return the updated file list fragment
    return list_files(project_name)

@app.route('/api/get-file-content/<project_name>/<path:filename>')
def get_file_content(project_name, filename):
    project_root = config_manager.get_project_root()
    
    # Sanitize filename to prevent directory traversal
    if ".." in filename or filename.startswith("/"):
        return jsonify({'status': 'error', 'message': 'Invalid file path'}), 400
        
    file_path = os.path.join(project_root, project_name, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'status': 'error', 'message': 'File not found'}), 404
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'status': 'success', 'content': content})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/save-file/<project_name>/<path:filename>', methods=['POST'])
def save_file_content(project_name, filename):
    project_root = config_manager.get_project_root()
    data = request.json
    
    if "content" not in data:
        return jsonify({'status': 'error', 'message': 'No content provided'}), 400

    # Sanitize filename to prevent directory traversal
    if ".." in filename or filename.startswith("/"):
        return jsonify({'status': 'error', 'message': 'Invalid file path'}), 400
        
    file_path = os.path.join(project_root, project_name, filename)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data['content'])
        reset_game_engine() # Reset the game engine to pick up changes
        # Re-initialize the game engine for the current project
        global game_engine, _temp_game_state
        game_engine = GameEngine(active_project_path, debug_mode=_app_debug_mode)

        # Restore game state if available
        if _temp_game_state:
            game_engine.restore_state_from_dict(_temp_game_state)
            _temp_game_state = None # Clear the temporary state after use
            print("Game state restored after file save.") # For testing purposes

        # Render the current passage from the restored state and return it
        # For IDE preview updates, exclude OOB navigation and tags to prevent duplicate elements
        current_passage = game_engine.game_state.get('current_passage', 'start')
        passage_html = game_engine.render_main_passage(current_passage, include_oob_nav=False, include_oob_tags=False)

        return jsonify({'status': 'success', 'message': f'{filename} saved successfully', 'passage_html': passage_html})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/delete-item/<project_name>', methods=['POST'])
def delete_item(project_name):
    project_root = config_manager.get_project_root()
    item_path = request.form.get('path')

    if not item_path:
        return list_files(project_name)
    
    # Basic security check
    if ".." in item_path or os.path.isabs(item_path):
        print(f"SECURITY: Invalid path requested: {item_path}")
        return list_files(project_name)

    full_path = os.path.join(project_root, project_name, item_path)

    if not os.path.exists(full_path):
        print(f"INFO: Item to delete does not exist at {full_path}")
        return list_files(project_name)

    try:
        if os.path.isfile(full_path):
            os.remove(full_path)
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path)
    except Exception as e:
        print(f"ERROR: Could not delete item {full_path}. Reason: {e}")

    # After action, return the updated file list fragment
    return list_files(project_name)

@app.route('/api/rename-item/<project_name>', methods=['POST'])
def rename_item(project_name):
    """Rename a file or folder."""
    project_root = config_manager.get_project_root()
    old_path = request.form.get('old_path')
    new_path = request.form.get('new_path')

    if not all([old_path, new_path]):
        return list_files(project_name)

    # Basic security checks
    for path in [old_path, new_path]:
        if ".." in path or os.path.isabs(path):
            print(f"SECURITY: Invalid path requested: {path}")
            return list_files(project_name)

    old_full_path = os.path.join(project_root, project_name, old_path)
    new_full_path = os.path.join(project_root, project_name, new_path)

    if not os.path.exists(old_full_path):
        print(f"INFO: File to rename does not exist at {old_full_path}")
        return list_files(project_name)

    if os.path.exists(new_full_path):
        print(f"INFO: Target filename already exists: {new_full_path}")
        return list_files(project_name)

    try:
        # Create target directory if it doesn't exist
        new_dir = os.path.dirname(new_full_path)
        if new_dir and not os.path.exists(new_dir):
            os.makedirs(new_dir)

        # Perform the rename
        os.rename(old_full_path, new_full_path)
        print(f"INFO: Renamed {old_path} to {new_path}")
    except Exception as e:
        print(f"ERROR: Could not rename {old_path} to {new_path}. Reason: {e}")

    # After action, return the updated file list fragment
    return list_files(project_name)

# Legacy build functionality moved to cleanup/build_tool_standalone_old.py
# Now using integrated AssetPacker system (see /api/build-game routes above)

@app.route('/api/settings-panel')
def settings_panel():
    project_root = config_manager.get_project_root()
    if not project_root:
        project_root = os.path.join(os.path.expanduser('~'), 'ScribeEngineProjects')
    return render_template('_fragments/_settings_panel.html', project_root=project_root)

@app.route('/api/settings/project_root', methods=['POST'])
def set_project_root_api():
    new_path = request.form.get('project_root')

    if not new_path:
        return ('<div class="error">Project root path cannot be empty.</div>', 400)

    try:
        os.makedirs(new_path, exist_ok=True)
        config_manager.set_project_root(new_path)
        return get_startup_screen()
    except Exception as e:
        return (f'<div class="error">Failed to set project root: {e}</div>', 500)

@app.route('/api/project-settings/<project_name>', methods=['GET'])
def get_project_settings(project_name):
    project_root = config_manager.get_project_root()
    project_path = os.path.join(project_root, project_name)
    config_path = os.path.join(project_path, 'project.json')

    config = {}
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            
    return render_template('_fragments/_project_settings.html', project_name=project_name, config=config)

@app.route('/api/project-settings/<project_name>', methods=['POST'])
def save_project_settings(project_name):
    project_root = config_manager.get_project_root()
    project_path = os.path.join(project_root, project_name)
    config_path = os.path.join(project_path, 'project.json')

    config = {}
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)

    # Helper to update nested dictionary
    def update_nested(d, keys, value):
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value

    # Update config with form data
    config['title'] = request.form.get('title', config.get('title'))
    config['author'] = request.form.get('author', config.get('author'))
    config['starting_passage'] = request.form.get('starting_passage', config.get('starting_passage'))
    config['icon_path'] = request.form.get('icon_path', config.get('icon_path', ''))

    # Features
    update_nested(config, ['features', 'use_default_player'], 'features.use_default_player' in request.form)
    update_nested(config, ['features', 'save_system'], request.form.get('features.save_system', 'server'))
    # update_nested(config, ['features', 'last_passage_enabled'], 'features.last_passage_enabled' in request.form)

    # Navigation
    update_nested(config, ['nav', 'enabled'], 'nav.enabled' in request.form)
    update_nested(config, ['nav', 'position'], request.form.get('nav.position'))

    # Debug Mode
    config['debug_mode'] = 'debug_mode' in request.form

    # Theme
    update_nested(config, ['theme', 'enabled'], 'theme.enabled' in request.form)
    update_nested(config, ['theme', 'use_engine_defaults'], 'theme.use_engine_defaults' in request.form)
    update_nested(config, ['theme', 'colors', 'primary_color'], request.form.get('theme.colors.primary_color'))
    update_nested(config, ['theme', 'colors', 'background_color'], request.form.get('theme.colors.background_color'))
    update_nested(config, ['theme', 'colors', 'text_color'], request.form.get('theme.colors.text_color'))
    update_nested(config, ['theme', 'colors', 'link_color'], request.form.get('theme.colors.link_color'))
    update_nested(config, ['theme', 'colors', 'border_color'], request.form.get('theme.colors.border_color'))
    update_nested(config, ['theme', 'fonts', 'body_font'], request.form.get('theme.fonts.body_font'))
    update_nested(config, ['theme', 'fonts', 'heading_font'], request.form.get('theme.fonts.heading_font'))

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

    # It's good practice to reload the engine's config if it's running
    if game_engine and game_engine.project_path == project_path:
        # First update the debug mode explicitly
        new_debug_mode = config.get('debug_mode', False)
        game_engine.update_debug_mode(new_debug_mode)
        # Then reload the full project configuration
        game_engine.load_project()

    return jsonify({'status': 'success', 'message': 'Settings saved successfully'})

# Asset Packer Build API Routes

@app.route('/api/build-game/<project_name>', methods=['POST'])
def build_game_api(project_name):
    """Start building a game using the new asset packer system."""
    import threading
    from datetime import datetime
    from engine.asset_packer import AssetPacker

    project_root = config_manager.get_project_root()
    project_path = os.path.join(project_root, project_name)

    # Validate project exists
    if not os.path.exists(project_path):
        return jsonify({'status': 'error', 'message': 'Project not found'}), 404

    # Check if build is already in progress
    if project_name in build_status and build_status[project_name]['status'] == 'building':
        return jsonify({'status': 'error', 'message': 'Build already in progress'}), 409

    # Initialize build status
    build_status[project_name] = {
        'status': 'building',
        'progress': 'Initializing build...',
        'start_time': datetime.now(),
        'executable_path': None,
        'error': None
    }

    def build_thread():
        """Background thread for building the game."""
        try:
            build_status[project_name]['progress'] = 'Scanning project files...'

            # Create asset packer
            packer = AssetPacker()

            build_status[project_name]['progress'] = 'Packing game assets...'

            # Create distribution inside the project directory
            builds_dir = os.path.join(project_path, 'builds')
            info = packer.create_distribution(project_path, builds_dir)

            build_status[project_name].update({
                'status': 'completed',
                'progress': f'Build completed! Distribution: {info["clean_title"]}_Distribution',
                'executable_path': info['distribution_dir'],
                'build_info': info
            })

        except Exception as e:
            build_status[project_name].update({
                'status': 'failed',
                'progress': f'Build failed: {str(e)}',
                'error': str(e)
            })

    # Start build in background thread
    threading.Thread(target=build_thread, daemon=True).start()

    return jsonify({'status': 'success', 'message': 'Build started successfully'})

@app.route('/api/build-status/<project_name>')
def get_build_status(project_name):
    """Get current build status for a project."""
    if project_name not in build_status:
        return jsonify({'status': 'error', 'message': 'No build found for project'}), 404

    status = build_status[project_name].copy()

    # Add elapsed time
    if 'start_time' in status:
        elapsed = datetime.now() - status['start_time']
        status['elapsed_seconds'] = int(elapsed.total_seconds())

    # Remove internal fields
    status.pop('start_time', None)

    return jsonify(status)

@app.route('/api/close-project')
def close_project():
    global game_engine, active_project_path
    game_engine = None
    active_project_path = None
    return redirect(url_for('gui_launcher'))

@app.route('/api/reset-game-state', methods=['POST'])
def reset_game_state_api():
    if game_engine:
        game_engine.reset_game_state()
        # return jsonify({'status': 'success', 'message': 'Game state reset successfully'}), 200
        response = make_response('', 204)
        response.headers['HX-Trigger'] = '{"showNotification": {"message": "Game state has been reset.", "type": "success"}}'
        return response
    return jsonify({'status': 'error', 'message': 'Game engine not initialized'}), 500

@app.route('/api/preview-panel')
def get_preview_panel():
    return render_template('_fragments/_preview_panel.html')


# Debug routes
@app.route('/api/game-state')
def get_game_state():
    if game_engine and hasattr(game_engine, 'game_state'):
        return jsonify(game_engine.get_serializable_state())
    return jsonify({})

@app.route('/api/set-temp-game-state', methods=['POST'])
def set_temp_game_state():
    global _temp_game_state
    try:
        _temp_game_state = request.json
        return jsonify({'status': 'success', 'message': 'Temporary game state set.'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/debug/state')
def debug_state():
    if not game_engine.debug_mode:
        return jsonify({'error': 'Debug mode disabled'}), 403
    return jsonify(game_engine.get_serializable_state())

@app.route('/debug/passages')
def debug_passages():
    if not game_engine.debug_mode:
        return jsonify({'error': 'Debug mode disabled'}), 403
    return jsonify(list(game_engine.passages.keys()))

@app.route('/debug/passage/<name>')
def debug_passage(name):
    if not game_engine.debug_mode:
        return jsonify({'error': 'Debug mode disabled'}), 403
    return jsonify(game_engine.passages.get(name, {}))

@app.route('/game/assets/<path:filename>')
def serve_project_asset(filename):
    # Assets are now served directly from the local 'game/assets' directory
    asset_path = os.path.join(game_engine.project_path, 'assets', filename)
    if os.path.exists(asset_path):
        return send_file(asset_path)
    else:
        from flask import abort
        return abort(404)

def shutdown_server_thread():
    global server
    time.sleep(0.1) # Give the request a moment to complete
    if server:
        server.shutdown()

@app.route('/shutdown', methods=['GET', 'POST'])
def shutdown():
    threading.Thread(target=shutdown_server_thread).start()
    return 'Server shutting down...'

def run_app_server(debug_mode=False, use_reloader=False, host='0.0.0.0', port=5000):
    global server
    # Reset server before starting a new one
    server = make_server(host, port, app)
    print(f"Serving Flask app on http://{host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scribe Engine Flask App')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host address to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    args = parser.parse_args()

    # When running directly, use the standard Flask app.run for development convenience
    # This will use Werkzeug's reloader, which is fine for development.
    app.run(debug=True, use_reloader=True, host=args.host, port=args.port)
