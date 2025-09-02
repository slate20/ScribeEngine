import os
import sys
import subprocess
import json
from datetime import datetime

# --- Helper function adapted from create_game.py ---
def create_new_project(project_name: str):
    """Creates a new game project with a default skeleton structure."""
    # Determine the base directory for games (relative to this script)
    script_dir = os.path.dirname(__file__)
    game_base_dir = os.path.abspath(os.path.join(script_dir, 'game'))
    
    project_path = os.path.join(game_base_dir, project_name)

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
def get_game_projects():
    game_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'game'))
    if not os.path.exists(game_dir):
        os.makedirs(game_dir)
        return []
    
    projects = [d for d in os.listdir(game_dir) if os.path.isdir(os.path.join(game_dir, d))]
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

def main():
    print("\n--- PyVN Engine Launcher ---")
    
    while True:
        print("\nOptions:")
        print("1. Create New Project")
        print("2. Load Existing Project")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            project_name = input("Enter new project name: ").strip()
            if not project_name:
                print("Project name cannot be empty.")
                continue
            try:
                create_new_project(project_name)
                selected_project = project_name
                break
            except FileExistsError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
        elif choice == '2':
            projects = get_game_projects()
            if not projects:
                print("No projects to load. Please create a new one first.")
                continue
            selected_project = select_project(projects)
            if selected_project:
                break
        elif choice == '3':
            print("Exiting launcher.")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

    # Launch the game engine (app.py) with the selected project
    if selected_project:
        project_absolute_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'game', selected_project))
        print(f"\nLaunching engine for project: {selected_project} (Path: {project_absolute_path})")
        
        # Use sys.executable to ensure the correct python interpreter is used (e.g., from venv)
        # Run app.py in a new process, allowing the launcher to exit or continue
        try:
            # Start app.py as a separate process
            print("\nStarting Flask development server... Press CTRL+C in the browser's terminal to stop it.")
            # Use Popen to run app.py in the background, allowing launcher.py to exit
            # We redirect stdout/stderr to the current process's stdout/stderr
            # This allows the user to see Flask logs in the terminal where launcher.py was run
            process = subprocess.Popen([sys.executable, 'app.py', '--project', project_absolute_path, '--production'],
                                       stdout=sys.stdout, stderr=sys.stderr)
            # The launcher can now exit, as app.py is running independently
            print(f"Flask server started. Access your game at http://127.0.0.1:5000")
            print("You can now close this launcher window.")
        except Exception as e:
            print(f"Failed to launch app.py: {e}")

if __name__ == "__main__":
    main()
