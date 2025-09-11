import webview
import threading
import time
import os
import sys
import json

# Add the project root to the Python path to allow importing app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app as flask_app, set_game_project_path, set_debug_mode
from loading_window import LoadingWindow

def start_flask_app():
    flask_app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

def run_webview_app(project_path_for_app: str):
    # Get game title and icon from project configuration for loading window
    game_title = "Game"
    icon_path = None
    
    try:
        project_config_path = os.path.join(project_path_for_app, 'project.json')
        if os.path.exists(project_config_path):
            with open(project_config_path, 'r') as f:
                config = json.load(f)
                game_title = config.get('title', 'Game')
                
                # Check for custom icon
                icon_relative_path = config.get('icon_path', '').strip()
                if icon_relative_path:
                    icon_absolute_path = os.path.join(project_path_for_app, icon_relative_path)
                    if os.path.exists(icon_absolute_path):
                        icon_path = icon_absolute_path
    except Exception:
        # If we can't read the config, use defaults
        pass
    
    # Fallback to engine icon if no game icon is found
    if not icon_path:
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        engine_icon_path = os.path.join(base_path, 'SE_icon.png')
        if os.path.exists(engine_icon_path):
            icon_path = engine_icon_path
    
    # Create loading window
    loading_window = LoadingWindow(
        title=game_title,
        subtitle="Loading game...",
        icon_path=icon_path
    )
    
    def flask_startup_sequence():
        """The Flask startup sequence that runs behind the loading window."""
        # Set the game project path in the app module
        set_game_project_path(project_path_for_app)
        set_debug_mode(False) # Disable debug mode for standalone builds

        # Start Flask in a separate thread
        flask_thread = threading.Thread(target=start_flask_app)
        flask_thread.daemon = True  # Daemonize thread so it exits when main thread exits
        flask_thread.start()

        # Give Flask a moment to start up
        time.sleep(2) 
        
        return True  # Signal that Flask startup is complete
    
    # Run the Flask startup sequence with the loading window
    loading_window.run_with_loading(flask_startup_sequence)
    
    # Create webview window (this must run on main thread after loading window closes)
    # The URL should match the Flask app's host and port
    webview.create_window(game_title, 'http://127.0.0.1:5000', width=1024, height=768)
    webview.start()

if __name__ == "__main__":
    # Entry point for standalone game executables
    # The project path should be bundled in the game_data directory
    import os
    import sys
    
    # Get the base path (either _MEIPASS for bundled apps or current directory)
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Look for the bundled game project in the game_data directory
    game_data_path = os.path.join(base_path, 'game_data')
    if os.path.exists(game_data_path):
        # Get the first (and should be only) project directory
        project_dirs = [d for d in os.listdir(game_data_path) if os.path.isdir(os.path.join(game_data_path, d))]
        if project_dirs:
            project_path = os.path.join(game_data_path, project_dirs[0])
            run_webview_app(project_path)
        else:
            print("Error: No game project found in bundled executable")
            sys.exit(1)
    else:
        print("Error: Game data directory not found in bundled executable")
        sys.exit(1)