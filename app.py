from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime
from engine.core import GameEngine

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

@app.before_request
def initialize_game_engine():
    global game_engine
    if game_engine is None:
        if GAME_PROJECT_PATH is None:
            # Fallback for direct app.py run without launcher/wrapper
            default_path = os.path.join(os.path.dirname(__file__), 'game')
            print(f"WARNING: GAME_PROJECT_PATH not set. Using default: {default_path}")
            set_game_project_path(default_path)
        game_engine = GameEngine(GAME_PROJECT_PATH, debug_mode=True)

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

@app.route('/shutdown', methods=['POST'])
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

def run_app_server(debug_mode=False, use_reloader=False):
    app.run(debug=debug_mode, host='0.0.0.0', port=5000, use_reloader=use_reloader)