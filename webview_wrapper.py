import webview
import threading
import time
import os
import sys
import argparse

# Add the project root to the Python path to allow importing app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app as flask_app, set_game_project_path

def start_flask_app():
    flask_app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PyVN Engine Webview Wrapper')
    parser.add_argument('--project', '-p', type=str, 
                        help='Path to the game project directory (e.g., game/my_game)',
                        required=False) # Make it optional for bundled builds
    args = parser.parse_args()

    # Determine the correct project path based on whether it's a bundled executable
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle
        bundle_dir = sys._MEIPASS
        game_project_name_in_bundle = args.project if args.project else "example" # Default to example if not provided
        project_path_to_pass_to_app = os.path.join(bundle_dir, 'game_data', game_project_name_in_bundle)
        print(f"Running from bundle. Project path for app: {project_path_to_pass_to_app}")
    else:
        # Running as a script
        if not args.project:
            print("Error: --project argument is required when running as a script.")
            sys.exit(1)
        project_path_to_pass_to_app = os.path.abspath(args.project)
        print(f"Running as script. Project path for app: {project_path_to_pass_to_app}")

    # Set the game project path in the app module
    set_game_project_path(project_path_to_pass_to_app)

    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=start_flask_app)
    flask_thread.daemon = True  # Daemonize thread so it exits when main thread exits
    flask_thread.start()

    # Give Flask a moment to start up
    time.sleep(2) 

    # Create webview window
    # The URL should match the Flask app's host and port
    webview.create_window('PyVN Engine', 'http://127.0.0.1:5000', width=1024, height=768)
    webview.start()