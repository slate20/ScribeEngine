import os
import sys
import subprocess
import json
from datetime import datetime
import argparse
import threading
import time
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import config_manager
import app
from app import reset_game_engine
import build
import webview_wrapper

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# --- Helper function adapted from create_game.py ---
def create_new_project(project_name: str, project_root_dir: str):
    """Creates a new game project with a default skeleton structure."""
    project_path = os.path.join(project_root_dir, project_name)

    if os.path.exists(project_path):
        raise FileExistsError(f"Project '{project_name}' already exists at {project_path}")

    print(f"Creating new project: {project_name} at {project_path}")

    os.makedirs(project_path)
    os.makedirs(os.path.join(project_path, 'saves'))
    os.makedirs(os.path.join(project_path, 'assets'))

    # Default project.json content
    default_project_json = {
        "title": project_name.replace('_', ' ').title(),
        "author": "Anonymous",
        "starting_passage": "start",
        "features": {
            "use_default_player": True,
            "use_default_inventory": True
        },
        "nav": {
            "enabled": True,
            "position": "horizontal"
        },
        "theme": {
            "enabled": True,
            "use_engine_defaults": True,
            "colors": {},
            "fonts": {}
        }
    }

    # Default story.tgame content
    default_story_tgame = f"""
:: NavMenu
[[Home->start]]

:: PrePassage
<div class="hud">
    <span>Health: {{ player.health }}</span>
    <span>Score: {{ player.score }}</span>
</div>
<hr>

:: PostPassage
<hr>
<div class="footer">
    <p>Copyright {datetime.now().year}, {{ game_title }}</p>
</div>

:: start
Welcome to your new adventure, {{ player.name }}!

This is your first passage. You can edit this file (story.tgame) to begin writing your story.

[[Start the adventure!->first_step]]

:: first_step
You have taken your first step into a larger world.

[[Go back->start]]
"""

    # Write project.json
    with open(os.path.join(project_path, 'project.json'), 'w') as f:
        json.dump(default_project_json, f, indent=2)

    # Write story.tgame
    with open(os.path.join(project_path, 'story.tgame'), 'w') as f:
        f.write(default_story_tgame)

    # Optional: Create placeholder systems.py and custom.css
    with open(os.path.join(project_path, 'systems.py'), 'w') as f:
        f.write("# Your custom Python logic goes here.\n# You can create multiple .py files in your project to organize your code.\n")
    with open(os.path.join(project_path, 'custom.css'), 'w') as f:
        f.write("/* Your custom CSS goes here */\n")

    print(f"Project '{project_name}' created successfully.")

# --- Launcher Logic ---
def get_game_projects(project_root_dir: str):
    if not os.path.exists(project_root_dir):
        os.makedirs(project_root_dir)
        return []
    
    projects = [d for d in os.listdir(project_root_dir) if os.path.isdir(os.path.join(project_root_dir, d))]
    return sorted(projects)

def select_project(projects):
    if not projects:
        print("No existing projects found.")
        return None

    print("\nExisting Projects:")
    for i, project in enumerate(projects):
        print(f"{i + 1}. {project}")
    
    while True:
        try:
            choice = input("Enter the number of the project to load: ")
            idx = int(choice) - 1
            if 0 <= idx < len(projects):
                return projects[idx]
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

flask_process = None # Global variable to hold the Flask server subprocess
flask_thread_instance = None # Global variable to hold the Flask server thread instance
observer = None # Global variable to hold the watchdog observer
project_path_for_watcher = None # Global variable to hold the project path for the watcher
restart_lock = threading.Lock()

class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_restart_time = 0

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(('.tgame', '.py')):
            current_time = time.time()
            if current_time - self.last_restart_time > 2:
                print(f"Detected change in {event.src_path}. Restarting server...")
                self.last_restart_time = current_time
                restart_flask_server()

def restart_flask_server():
    global project_path_for_watcher
    if project_path_for_watcher and restart_lock.acquire(blocking=False):
        try:
            print("Acquired lock, restarting server...")
            # Reset the game engine to force a reload of game files
            app.reset_game_engine()
            stop_flask_server()
            run_flask_server(project_path_for_watcher)
            print(f"Flask server restarted. Access your game at http://127.0.0.1:5000")
        finally:
            restart_lock.release()
            print("Released lock.")
    else:
        print("Could not acquire lock, another restart is in progress.")

def start_watcher(path):
    global observer, project_path_for_watcher
    project_path_for_watcher = path
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print(f"Started watching {path} for changes.")

def stop_watcher():
    global observer
    if observer:
        observer.stop()
        observer.join()
        print("Stopped watching for file changes.")



def run_flask_server(project_absolute_path: str):
    global flask_process, flask_thread_instance
    app.set_game_project_path(project_absolute_path)

    if getattr(sys, 'frozen', False): # Running as a PyInstaller bundled executable
        # Directly run the Flask app in a separate thread
        print("Starting Flask server in a separate thread (bundled executable mode)...")
        flask_thread_instance = threading.Thread(target=app.run_app_server, kwargs={
            'debug_mode': False, # Debug mode should be off for bundled apps
            'host': '0.0.0.0',
            'port': 5000,
            'use_reloader': False # Reloader should be off for bundled apps
        })
        flask_thread_instance.daemon = True # Allow main thread to exit even if Flask thread is running
        flask_thread_instance.start()
        flask_process = None # Clear the subprocess handle as we are using a thread
        # Give the server a moment to start up
        time.sleep(1) # Give the server a moment to start up
    else:
        # When running as a script, use the flask command via subprocess
        cmd = [sys.executable, '-m', 'flask', 'run', '--host=0.0.0.0', '--port=5000']

        # Set FLASK_APP environment variable
        env = os.environ.copy()
        env['FLASK_APP'] = 'app.py'
        env['FLASK_DEBUG'] = '0' # Disable debug mode to prevent Flask's reloader
        env['SCRIBE_ENGINE_GAME_PROJECT_PATH'] = project_absolute_path # Pass project path via environment variable

        print(f"Running Flask server with command: {' '.join(cmd)}")
        flask_process = subprocess.Popen(cmd, env=env, cwd=os.path.dirname(os.path.abspath(__file__)))
        flask_thread_instance = None # Clear the thread handle as we are using a subprocess
        time.sleep(1) # Give the server a moment to start up

def stop_flask_server():
    global flask_process, flask_thread_instance
    if flask_process:
        print("Terminating Flask server process...")
        if flask_process.poll() is None: # Check if process is still running
            flask_process.terminate() # Send SIGTERM
            try:
                flask_process.wait(timeout=5) # Wait for process to terminate
                print("Flask server process terminated.")
            except subprocess.TimeoutExpired:
                print("Flask server process did not terminate gracefully. Killing...")
                flask_process.kill() # Send SIGKILL if it doesn't terminate
        flask_process = None
    elif flask_thread_instance and flask_thread_instance.is_alive():
        print("Attempting to shut down Flask server thread...")
        try:
            # Make a request to the shutdown endpoint
            requests.get('http://127.0.0.1:5000/shutdown', timeout=2)
            # Wait for the thread to terminate
            flask_thread_instance.join(timeout=3)
            if flask_thread_instance.is_alive():
                 print("Warning: Flask server thread did not terminate in time.")
            else:
                 print("Flask server thread terminated successfully.")
        except requests.exceptions.RequestException as e:
            print(f"Could not send shutdown signal to server: {e}")
        finally:
            flask_thread_instance = None
    else:
        print("No Flask server process or thread to terminate.")

active_project_path = None
flask_server_running = False

def main_menu(project_root):
    global active_project_path
    while True:
        clear_screen()
        print("""
  █████████                      ███  █████                 ██████████                      ███                     
 ███▒▒▒▒▒███                    ▒▒▒  ▒▒███                 ▒▒███▒▒▒▒▒█                     ▒▒▒                      
▒███    ▒▒▒   ██████  ████████  ████  ▒███████   ██████     ▒███  █ ▒  ████████    ███████ ████  ████████    ██████ 
▒▒█████████  ███▒▒███▒▒███▒▒███▒▒███  ▒███▒▒███ ███▒▒███    ▒██████   ▒▒███▒▒███  ███▒▒███▒▒███ ▒▒███▒▒███  ███▒▒███
 ▒▒▒▒▒▒▒▒███▒███ ▒▒▒  ▒███ ▒▒▒  ▒███  ▒███ ▒███▒███████     ▒███▒▒█    ▒███ ▒███ ▒███ ▒███ ▒███  ▒███ ▒███ ▒███████ 
 ███    ▒███▒███  ███ ▒███      ▒███  ▒███ ▒███▒███▒▒▒      ▒███ ▒   █ ▒███ ▒███ ▒███ ▒███ ▒███  ▒███ ▒███ ▒███▒▒▒  
▒▒█████████ ▒▒██████  █████     █████ ████████ ▒▒██████     ██████████ ████ █████▒▒███████ █████ ████ █████▒▒██████ 
 ▒▒▒▒▒▒▒▒▒   ▒▒▒▒▒▒  ▒▒▒▒▒     ▒▒▒▒▒ ▒▒▒▒▒▒▒▒   ▒▒▒▒▒▒     ▒▒▒▒▒▒▒▒▒▒ ▒▒▒▒ ▒▒▒▒▒  ▒▒▒▒▒███▒▒▒▒▒ ▒▒▒▒ ▒▒▒▒▒  ▒▒▒▒▒▒  
                                                                                  ███ ▒███                          
                                                                                 ▒▒██████                           
                                                                                  ▒▒▒▒▒▒
        """)
        print(f"---(Projects Root: {project_root}) ---")
        print("\nMain Menu:")
        print("1. Create New Project")
        print("2. Load Existing Project")
        print("3. Change Projects Root Path")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            project_name = input("Enter new project name: ").strip()
            if not project_name:
                print("Project name cannot be empty.")
                continue
            try:
                create_new_project(project_name, project_root)
                active_project_path = os.path.abspath(os.path.join(project_root, project_name))
                print(f"Project '{project_name}' created and set as active.")
                return "project_menu" # Transition to project menu
            except FileExistsError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
        elif choice == '2':
            projects = get_game_projects(project_root)
            if not projects:
                print("No projects found. Please create one first.")
                continue
            selected_project_name = select_project(projects)
            if selected_project_name:
                active_project_path = os.path.abspath(os.path.join(project_root, selected_project_name))
                print(f"Project '{selected_project_name}' set as active.")
                return "project_menu" # Transition to project menu
            else:
                pass # User cancelled project selection
        elif choice == '3':
            stop_watcher() # Stop watcher if it was running from a previous session
            while True:
                new_root_input = input("Enter the NEW path for your Scribe Engine game projects (e.g., ~/MyScribeEngine_Games): ").strip()
                if new_root_input:
                    new_project_root = os.path.abspath(os.path.expanduser(new_root_input))
                    try:
                        os.makedirs(new_project_root, exist_ok=True)
                        config_manager.set_project_root(new_project_root)
                        project_root = new_project_root # Update current session's root
                        print(f"Project root successfully changed to: {project_root}")
                        break
                    except OSError as e:
                        print(f"Error creating directory {new_project_root}: {e}. Please try again.")
                else:
                    print("New project root cannot be empty.")
            # Stay in main menu
        elif choice == '4':
            print("Exiting launcher.")
            stop_watcher()
            stop_flask_server()
            clear_screen()
            sys.exit(0)
        else:
            print("Invalid choice. Please enter 1, 2, 3 or 4.")

def project_menu(project_root):
    global active_project_path, flask_server_running
    project_name = os.path.basename(active_project_path)
    while True:
        clear_screen()
        print(f"--- Scribe Engine Launcher (Project Root: {project_root}) ---")
        print(f"\nActive Project: {project_name}")
        print("\nProject Menu:")
        print("1. Start Development Server")
        print("2. Build Standalone Game")
        print("3. Go Back to Main Menu")
        print("4. Quit Engine")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            print(f"\nStarting Flask development server for {project_name}...")
            run_flask_server(active_project_path)
            start_watcher(active_project_path)
            flask_server_running = True
            print(f"Flask server started. Access your game at http://127.0.0.1:5000")
            return "server_running_menu" # Transition to server running menu
        elif choice == '2':
            print(f"\nBuilding standalone game for project: {project_name}")
            # Ensure server is stopped before building
            if flask_server_running:
                print("Stopping development server before building...")
                stop_flask_server()
                stop_watcher()
                flask_server_running = False
                time.sleep(2) # Give server time to shut down
            build.build_standalone_game(project_name, project_root)
            print(f"Build process for {project_name} completed. Executable can be found in the 'dist' directory.")
            # Stay in project menu
        elif choice == '3':
            if flask_server_running:
                print("Stopping development server before returning to main menu...")
                stop_flask_server()
                stop_watcher()
                flask_server_running = False
                time.sleep(2) # Give server time to shut down
            active_project_path = None # Deselect project
            return "main_menu" # Transition to main menu
        elif choice == '4':
            print("Exiting launcher.")
            if flask_server_running:
                stop_flask_server()
                stop_watcher()
            sys.exit(0)
        else:
            print("Invalid choice. Please enter 1, 2, 3 or 4.")

def server_running_menu(project_root):
    global flask_server_running
    project_name = os.path.basename(active_project_path)
    while True:
        clear_screen()
        print(f"--- Scribe Engine Launcher (Project Root: {project_root}) ---")
        print(f"\nActive Project: {project_name} (Server Running)")
        print(f"Access your game at http://127.0.0.1:5000")
        print("\nServer Running Menu:")
        print("1. Stop Development Server")

        choice = input("Enter your choice (1): ")

        if choice == '1':
            print("Stopping Flask development server...")
            stop_flask_server()
            stop_watcher()
            flask_server_running = False
            return "project_menu" # Transition to project menu
        else:
            print("Invalid choice. Please enter 1.")

def main():
    global active_project_path, flask_server_running

    parser = argparse.ArgumentParser(description='Scribe Engine Launcher')
    parser.add_argument('--project-root', '-r', type=str, 
                        help='Override the default or configured project root directory.')
    args = parser.parse_args()

    project_root = args.project_root

    if not project_root:
        project_root = config_manager.get_project_root()
        if not project_root or not os.path.isdir(project_root):
            clear_screen()
            print("\nNo project root configured or found. Please specify one.")
            while True:
                user_input = input("Enter the path for your Scribe Engine game projects (e.g., ~/ScribeEngine_Games): ").strip()
                if user_input:
                    project_root = os.path.expanduser(user_input)
                    try:
                        os.makedirs(project_root, exist_ok=True)
                        config_manager.set_project_root(project_root)
                        print(f"Project root set to: {project_root}")
                        break
                    except OSError as e:
                        print(f"Error creating directory {project_root}: {e}. Please try again.")
                else:
                    print("Project root cannot be empty.")
    else:
        project_root = os.path.abspath(os.path.expanduser(project_root))
        os.makedirs(project_root, exist_ok=True)
        config_manager.set_project_root(project_root) # Save if overridden via CLI
        print(f"Project root set to: {project_root}")

    current_state = "main_menu"

    while True:
        if current_state == "main_menu":
            next_state = main_menu(project_root)
        elif current_state == "project_menu":
            next_state = project_menu(project_root)
        elif current_state == "server_running_menu":
            next_state = server_running_menu(project_root)
        else:
            print("Unknown state. Exiting.")
            sys.exit(1)
        
        current_state = next_state


if __name__ == "__main__":
    main()
