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

class Api:
    """
    API class exposed to the webview frontend.
    """
    def open_folder_dialog(self):
        """
        Opens a folder selection dialog and returns the selected path.
        """
        result = webview.create_file_dialog(webview.FOLDER_DIALOG)
        if result:
            # result is a tuple, we want the first element
            return result[0]
        return None

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
        # Determine the base path for the application
        if getattr(sys, 'frozen', False):
            # Running as a bundled executable
            base_path = os.path.dirname(sys.executable)
        else:
            # Running as a script
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        project_root_path = os.path.join(base_path, 'ScribeEngine_Projects')
        os.makedirs(project_root_path, exist_ok=True)
        config_manager.set_project_root(project_root_path)

    # Start Flask in a separate thread
    flask_thread_instance = threading.Thread(target=start_flask_app)
    flask_thread_instance.daemon = True
    flask_thread_instance.start()
    time.sleep(2) # Give Flask a moment to start up

    # Create an API instance to expose to the webview
    api = Api()

    # Create the webview window
    webview.create_window('Scribe Engine', 'http://127.0.0.1:5000/gui', js_api=api, width=1920, height=1080)
    webview.start()

    # Wait for the user to close the window
    # try:
    #     input("Press Enter to stop the server and exit...")
    # except KeyboardInterrupt:
    #     print("\nExiting...")
    
if __name__ == '__main__':
    run_gui_app()
