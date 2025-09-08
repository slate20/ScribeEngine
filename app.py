from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
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

# Initialize game engine (will be done after GAME_PROJECT_PATH is set)
game_engine = None
_app_debug_mode = False # Default to False for production

# Add a server object to manage the Flask server instance
server = None

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
    if nav_config.get('enabled', False):
        nav_content = game_engine.render_special_passage('NavMenu')

    theme_css = game_engine._generate_theme_css()
    use_engine_defaults = game_engine.theme_config.get('use_engine_defaults', True)

    return render_template('base.html',
                         game_title=game_engine.get_title(),
                         debug_mode=game_engine.debug_mode,
                         nav_config=nav_config,
                         nav_content=nav_content,
                         theme_css=theme_css,
                         use_engine_defaults=use_engine_defaults)

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
        game_engine.save_game(slot)
        return jsonify({'status': 'success', 'message': 'Game saved'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

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
        
        game_engine.set_variable(variable_name, input_value)
        
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
        
        # Get the current game context (state + helper functions)
        context = game_engine.get_template_context()
        
        # Use Jinja to execute the action string
        # The {% do %} extension is needed for statements that don't produce output
        env = Environment(extensions=['jinja2.ext.do'])
        template = env.from_string(action_string)
        template.render(**context) # This calls helpers like set_variable that modify the game_state

        # Render the target passage and return the HTML
        html = game_engine.render_main_passage(target_passage)
        return html

    except Exception as e:
        if game_engine.debug_mode:
            return f'<div class="debug-error">Error executing action link: {str(e)}</div>', 500
        return '<div class="error">An error occurred while processing the action.</div>', 500

@app.route('/saves')
def list_saves():
    saves = game_engine.list_saves()
    return jsonify({'saves': saves})

@app.route('/custom.css')
def serve_custom_css():
    custom_css_path = os.path.join(game_engine.project_path, 'custom.css')
    if os.path.exists(custom_css_path):
        return send_file(custom_css_path, mimetype='text/css')
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
    project_debug_mode = False
    if os.path.exists(project_config_path):
        with open(project_config_path, 'r') as f:
            project_config = json.load(f)
            project_debug_mode = project_config.get('debug_mode', False)

    game_engine = GameEngine(active_project_path, debug_mode=project_debug_mode)

    return render_template('editor.html', project_name=project_name, project_root=project_root)

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

    return render_template('_fragments/_file_list.html', 
                           story_files=sorted(story_files),
                           logic_files=sorted(logic_files),
                           config_files=sorted(config_files),
                           asset_files=sorted(asset_files),
                           project_name=project_name,
                           css_files=sorted(css_files))

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
        global game_engine
        game_engine = GameEngine(active_project_path, debug_mode=_app_debug_mode)
        print("Game engine reset and re-initialized!") # For testing purposes
        return jsonify({'status': 'success', 'message': f'{filename} saved successfully'})
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

@app.route('/api/build-game/<project_name>', methods=['POST'])
def build_game_api(project_name):
    from build import build_standalone_game
    project_root = config_manager.get_project_root()
    try:
        print(f"Received build request for {project_name} at {project_root}")
        # build_standalone_game(project_name, project_root) # This can be uncommented when ready
        return jsonify({'status': 'success', 'message': f'Build started for {project_name}'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

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
    config['start_passage'] = request.form.get('start_passage', config.get('start_passage'))

    # Features
    update_nested(config, ['features', 'use_default_player'], 'features.use_default_player' in request.form)
    update_nested(config, ['features', 'use_default_inventory'], 'features.use_default_inventory' in request.form)

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
        game_engine.load_project()

    return jsonify({'status': 'success', 'message': 'Settings saved successfully'})

@app.route('/api/close-project')
def close_project():
    global game_engine, active_project_path
    game_engine = None
    active_project_path = None
    return redirect(url_for('gui_launcher'))

@app.route('/api/preview-panel')
def get_preview_panel():
    return render_template('_fragments/_preview_panel.html')


# Debug routes
@app.route('/api/game-state')
def get_game_state():
    if game_engine and hasattr(game_engine, 'game_state'):
        return jsonify(game_engine.game_state)
    return jsonify({})

@app.route('/debug/state')
def debug_state():
    if not game_engine.debug_mode:
        return jsonify({'error': 'Debug mode disabled'}), 403
    return jsonify(game_engine.game_state)

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
