import webview
import threading
import time
import os
import sys

# Add the project root to the Python path to allow importing app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app as flask_app, set_game_project_path

def start_flask_app():
    flask_app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

def run_webview_app(project_path_for_app: str):
    # Set the game project path in the app module
    set_game_project_path(project_path_for_app)
    set_debug_mode(False) # Disable debug mode for standalone builds

    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=start_flask_app)
    flask_thread.daemon = True  # Daemonize thread so it exits when main thread exits
    flask_thread.start()

    # Give Flask a moment to start up
    time.sleep(2) 

    # Create webview window
    # The URL should match the Flask app's host and port
    webview.create_window('Scribe Engine', 'http://127.0.0.1:5000', width=1024, height=768)
    webview.start()