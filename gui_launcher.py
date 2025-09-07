import sys
import io
import os
import threading
import time
import webview
import requests

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app as flask_app
from app import set_game_project_path, set_debug_mode, reset_game_engine, set_gui_mode
import config_manager

# Global variables for server management
flask_thread_instance = None
project_root_path = None
active_project_path = None

def start_flask_app():
    """Starts the Flask server in a separate thread."""
    flask_app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

def run_gui_app():
    """Main function to launch the GUI and the Flask server."""
    global project_root_path, flask_thread_instance
    
    # Set the application to run in GUI mode
    set_gui_mode(True)

    # Check for the project root and handle first-run setup
    project_root_path = config_manager.get_project_root()
    if not project_root_path or not os.path.isdir(project_root_path):
        # In a real GUI, this would be a file dialog, but for now, we'll
        # just assume a default path or prompt the user via console.
        print("No project root found. Please set one.")
        project_root_path = os.path.join(os.path.expanduser('~'), 'ScribeEngine_Games')
        os.makedirs(project_root_path, exist_ok=True)
        config_manager.set_project_root(project_root_path)

    # Start Flask in a separate thread
    flask_thread_instance = threading.Thread(target=start_flask_app)
    flask_thread_instance.daemon = True
    flask_thread_instance.start()
    time.sleep(2) # Give Flask a moment to start up

    # Create the webview window
    webview.create_window('Scribe Engine GUI', 'http://127.0.0.1:5000/gui', width=1280, height=800)
    webview.start()

    # Keep the main thread alive to prevent the Flask daemon from exiting
    try:
        input("Press Enter to stop the server and exit...")
    except KeyboardInterrupt:
        print("\nExiting...")
    
if __name__ == '__main__':
    run_gui_app()
