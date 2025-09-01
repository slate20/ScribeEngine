import os
import json
import sys
from datetime import datetime

def create_new_project(project_name: str):
    """Creates a new game project with a default skeleton structure."""
    # Determine the base directory for games (relative to this script)
    script_dir = os.path.dirname(__file__)
    games_base_dir = os.path.abspath(os.path.join(script_dir, 'games'))
    
    project_path = os.path.join(games_base_dir, project_name)

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
    print(f"To run your new game, update GAME_PROJECT_PATH in app.py to: 'games/{project_name}' and then run 'python app.py'.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_game.py <project_name>")
        sys.exit(1)
    
    project_name = sys.argv[1]
    try:
        create_new_project(project_name)
    except FileExistsError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)