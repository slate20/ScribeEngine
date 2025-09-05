from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import sys
import argparse
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

def set_game_project_path(path):
    global GAME_PROJECT_PATH
    GAME_PROJECT_PATH = path

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.secret_key = 'your-secret-key-here'  # Change in production

# Initialize game engine (will be done after GAME_PROJECT_PATH is set)
game_engine = None
_app_debug_mode = True # Default to True for development

# Add a server object to manage the Flask server instance
server = None

def set_debug_mode(mode: bool):
    global _app_debug_mode
    _app_debug_mode = mode

@app.before_request
def initialize_game_engine():
    global game_engine, GAME_PROJECT_PATH
    # Skip initialization if the request is for shutdown
    if request.path == '/shutdown':
        return

    # Prioritize environment variable for GAME_PROJECT_PATH
    if os.environ.get('PYVN_GAME_PROJECT_PATH') and GAME_PROJECT_PATH is None:
        GAME_PROJECT_PATH = os.environ.get('PYVN_GAME_PROJECT_PATH')

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
        return '<div class="error">Error submitting input</div>', 500

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

# Debug routes
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
    parser = argparse.ArgumentParser(description='PyVN Flask App')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host address to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    args = parser.parse_args()

    # When running directly, use the standard Flask app.run for development convenience
    # This will use Werkzeug's reloader, which is fine for development.
    app.run(debug=True, use_reloader=True, host=args.host, port=args.port)
