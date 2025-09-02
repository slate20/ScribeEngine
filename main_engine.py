import os
import sys
import subprocess
import json
from datetime import datetime
import argparse
import threading
import time

import config_manager
import app
import build
import webview_wrapper

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
        "main_story_file": "story.tgame",
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
        f.write("# Your custom Python systems go here\n")
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

def run_flask_server(project_absolute_path: str):
    app.set_game_project_path(project_absolute_path)
    # Run Flask app in a separate thread
    # We need to ensure app.run() is called with debug=False and use_reloader=False
    # as it's being run by the engine executable
    app.run_app_server(debug_mode=False, use_reloader=False)

def main():
    parser = argparse.ArgumentParser(description='PyVN Engine Launcher')
    parser.add_argument('--project-root', '-r', type=str, 
                        help='Override the default or configured project root directory.')
    args = parser.parse_args()

    project_root = args.project_root

    if not project_root:
        project_root = config_manager.get_project_root()
        if not project_root or not os.path.isdir(project_root):
            print("\nNo project root configured or found. Please specify one.")
            while True:
                user_input = input("Enter the path for your PyVN game projects (e.g., ~/PyVN_Games): ").strip()
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

    print(f"\n--- PyVN Engine Launcher (Project Root: {project_root}) ---")
    
    while True:
        print("\nOptions:")
        print("1. Create New Project")
        print("2. Load Existing Project")
        print("3. Build Standalone Game")
        print("4. Change Project Root Path")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == '1':
            project_name = input("Enter new project name: ").strip()
            if not project_name:
                print("Project name cannot be empty.")
                continue
            try:
                create_new_project(project_name, project_root)
                selected_project = project_name
                # After creating, automatically load it for development
                project_absolute_path = os.path.abspath(os.path.join(project_root, selected_project))
                print(f"\nLaunching engine for project: {selected_project} (Path: {project_absolute_path})")
                print("\nStarting Flask development server... Press CTRL+C in this terminal to stop it.")
                run_flask_server_thread = threading.Thread(target=run_flask_server, args=(project_absolute_path,))
                run_flask_server_thread.daemon = True
                run_flask_server_thread.start()
                print(f"Flask server started. Access your game at http://127.0.0.1:5000")
                try:
                    input("Press Enter to stop Flask server and return to main menu...") # Keep launcher alive
                    # Send shutdown request to Flask app
                    import requests
                    try:
                        requests.post('http://127.0.0.1:5000/shutdown')
                        print("Flask server shutdown request sent.")
                        time.sleep(1) # Give server a moment to shut down
                    except requests.exceptions.ConnectionError:
                        print("Flask server already stopped or not reachable.")
                except KeyboardInterrupt:
                    print("\nKeyboardInterrupt detected. Attempting to stop Flask server...")
                    # If Ctrl+C is pressed, try to send shutdown request
                    try:
                        requests.post('http://127.0.0.1:5000/shutdown')
                        print("Flask server shutdown request sent.")
                        time.sleep(1) # Give server a moment to shut down
                    except requests.exceptions.ConnectionError:
                        print("Flask server already stopped or not reachable.")
                print("Returning to main menu.")
            except FileExistsError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
        elif choice == '2':
            projects = get_game_projects(project_root)
            if not projects:
                print("No projects to load. Please create a new one first.")
                continue
            selected_project = select_project(projects)
            if selected_project:
                project_absolute_path = os.path.abspath(os.path.join(project_root, selected_project))
                print(f"\nLaunching engine for project: {selected_project} (Path: {project_absolute_path})")
                print("\nStarting Flask development server... Press CTRL+C in this terminal to stop it.")
                run_flask_server_thread = threading.Thread(target=run_flask_server, args=(project_absolute_path,))
                run_flask_server_thread.daemon = True
                run_flask_server_thread.start()
                print(f"Flask server started. Access your game at http://127.0.0.1:5000")
                try:
                    input("Press Enter to stop Flask server and return to main menu...") # Keep launcher alive
                    # Send shutdown request to Flask app
                    import requests
                    try:
                        requests.post('http://127.0.0.1:5000/shutdown')
                        print("Flask server shutdown request sent.")
                        time.sleep(1) # Give server a moment to shut down
                    except requests.exceptions.ConnectionError:
                        print("Flask server already stopped or not reachable.")
                except KeyboardInterrupt:
                    print("\nKeyboardInterrupt detected. Attempting to stop Flask server...")
                    # If Ctrl+C is pressed, try to send shutdown request
                    try:
                        requests.post('http://127.0.0.1:5000/shutdown')
                        print("Flask server shutdown request sent.")
                        time.sleep(1) # Give server a moment to shut down
                    except requests.exceptions.ConnectionError:
                        print("Flask server already stopped or not reachable.")
                print("Returning to main menu.")
        elif choice == '3':
            projects = get_game_projects(project_root)
            if not projects:
                print("No projects to build. Please create or load one first.")
                continue
            selected_project = select_project(projects)
            if selected_project:
                project_absolute_path = os.path.abspath(os.path.join(project_root, selected_project))
                print(f"\nBuilding standalone game for project: {selected_project}")
                # Call build.build_standalone_game
                # We need to pass the project_root_dir to build.py
                build.build_standalone_game(selected_project, project_root)
                print(f"Build process for {selected_project} completed. Executable can be found in the 'dist' directory.")
                input("Press Enter to return to main menu...")
        elif choice == '4':
            # Change Project Root Path
            while True:
                new_root_input = input("Enter the NEW path for your PyVN game projects (e.g., ~/MyPyVN_Games): ").strip()
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
            input("Press Enter to return to main menu...")
        elif choice == '5':
            print("Exiting launcher.")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")

if __name__ == "__main__":
    main()