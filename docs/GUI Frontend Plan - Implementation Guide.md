This guide provides a detailed, step-by-step walkthrough for implementing the new GUI executable for Scribe Engine.

## Phase 1: The `gui_launcher.py` Entry Point

This file will replace `main_engine.py` as the entry point for the GUI application.

### Step 1.1: Create `gui_launcher.py`

Create a new file named `gui_launcher.py` in the root directory.

```
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
from app import set_game_project_path, set_debug_mode, reset_game_engine
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
    webview.create_window('Scribe Engine GUI', '[http://127.0.0.1:5000/gui](http://127.0.0.1:5000/gui)', width=1280, height=800)
    webview.start()
    
if __name__ == '__main__':
    run_gui_app()
```

## Phase 2: HTMX-Driven Backend and Frontend

This phase involves modifying `app.py` and creating new HTML files for the GUI.

### Step 2.1: Update `app.py`

Add new routes to `app.py` to handle the GUI's API requests and serve the HTML fragments.

```
# app.py additions
... (existing imports)

# New imports for file operations and HTMX
import shutil # For copying new project templates

@app.route('/gui')
def gui_launcher():
    return render_template('launcher.html', project_root=config_manager.get_project_root())

@app.route('/api/projects')
def list_projects_fragment():
    project_root = config_manager.get_project_root()
    projects = [d for d in os.listdir(project_root) if os.path.isdir(os.path.join(project_root, d))]
    projects.sort()
    return render_template('_fragments/_project_list.html', projects=projects)

@app.route('/api/project-menu/<project_name>')
def project_menu_fragment(project_name):
    # This route will serve the HTML for the project-specific menu
    return render_template('_fragments/_project_menu.html', project_name=project_name)

@app.route('/api/new-project', methods=['POST'])
def create_project_api():
    project_name = request.json.get('project_name')
    project_root = config_manager.get_project_root()
    
    if not project_name:
        return jsonify({'status': 'error', 'message': 'Project name is required'}), 400
        
    project_path = os.path.join(project_root, project_name)
    if os.path.exists(project_path):
        return jsonify({'status': 'error', 'message': 'Project already exists'}), 409
        
    # Re-use the existing logic from main_engine.py
    # NOTE: You'll need to move the create_new_project function to a shared module
    from create_project_logic import create_new_project
    create_new_project(project_name, project_root)
    
    return jsonify({'status': 'success', 'message': f'Project "{project_name}" created!'}), 200

@app.route('/api/open-editor/<project_name>')
def open_editor(project_name):
    global active_project_path
    project_root = config_manager.get_project_root()
    active_project_path = os.path.join(project_root, project_name)
    set_game_project_path(active_project_path)
    return render_template('editor.html', project_name=project_name)
    
# Add other API endpoints as needed for file saving, opening, etc.
```

### Step 2.2: Create GUI HTML Files and Fragments

Create the following new files in your `templates` directory:

`templates/launcher.html`

```
<div class="launcher-container" hx-target="this" hx-swap="outerHTML">
    <h1>Scribe Engine GUI</h1>
    <div hx-get="/api/projects" hx-trigger="load, createProject from:body">
        <!-- HTMX will load project list here -->
        <p>Loading projects...</p>
    </div>
    
    <button hx-post="/api/new-project" hx-vals='js:{"project_name": prompt("Enter new project name:")}' hx-target="#project-list" hx-swap="innerHTML" hx-on::after-request="window.location.reload()">
        Create New Project
    </button>
</div>
```

`templates/_fragments/_project_list.html`

```
<div id="project-list">
    <h2>Existing Projects</h2>
    <ul>
        {% for project in projects %}
            <li>
                <button hx-get="/api/project-menu/{{ project }}" hx-target=".launcher-container" hx-swap="outerHTML">
                    {{ project }}
                </button>
            </li>
        {% else %}
            <li>No projects found.</li>
        {% endfor %}
    </ul>
</div>
```

`templates/_fragments/_project_menu.html`

```
<div class="project-menu-container" hx-target="this" hx-swap="outerHTML">
    <h1>{{ project_name }}</h1>
    <button hx-get="/api/open-editor/{{ project_name }}" hx-target="body" hx-swap="innerHTML">
        Open Editor
    </button>
    <button hx-post="/api/build-game/{{ project_name }}">
        Build Game
    </button>
    <button hx-get="/api/projects" hx-target=".launcher-container" hx-swap="outerHTML">
        Back to Projects
    </button>
</div>
```

`templates/editor.html`

```
<div class="editor-container">
    <div id="file-tree">
        <!-- File tree will be rendered here via a separate HTMX call -->
    </div>
    <div id="editor-pane">
        <!-- CodeMirror editor will be initialized here -->
    </div>
    <div id="preview-pane">
        <!-- Live preview of the game will be in an iframe -->
        <iframe src="/passage/start"></iframe>
    </div>
</div>
```

## Phase 3: The Client-Side Editor

The editor itself is a complex, client-side component. HTMX is not well-suited for this, so we will use a dedicated JavaScript library.

### Step 3.1: Add `editor.html` and JavaScript

The `editor.html` file will contain the CodeMirror editor and an iframe for the live preview. The JavaScript in `gui.js` will handle the editor's functionality.

- **CodeMirror Setup:** Add the CodeMirror library to your project. Include the core library and any necessary modes (e.g., Python mode, Jinja2 mode).
    

```
<!-- Inside templates/editor.html's <head> -->
<link rel="stylesheet" href="[https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.css](https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.css)">
<script src="[https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.js](https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.js)"></script>
<script src="[https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/mode/python/python.js](https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/mode/python/python.js)"></script>
<script src="[https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/mode/jinja2/jinja2.js](https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/mode/jinja2/jinja2.js)"></script>
```

- **Editor Logic (`static/js/gui.js`):**
    
    - Initialize the CodeMirror editor on `DOMContentLoaded` or when the `editor.html` page is loaded.
        
    - Implement logic to handle saving: when the user hits `Ctrl+S` or a save button, the JavaScript will get the content from the editor and `POST` it to a new Flask endpoint (e.g., `/api/save-file`).
        
    - Since your backend already uses `watchdog` to reload the server on file changes, the live preview iframe will automatically refresh when a file is saved.
        

```
// static/js/gui.js
document.addEventListener('DOMContentLoaded', () => {
    // Check if we are on the editor page
    const editorPane = document.getElementById('editor-pane');
    if (!editorPane) {
        return; // Not on the editor page, exit
    }
    
    // Initialize the CodeMirror Editor
    const editor = CodeMirror(editorPane, {
        value: 'Loading file...',
        mode: 'jinja2', // Set to Jinja2 mode for proper syntax highlighting
        theme: 'default', // You can use a dark theme here
        lineNumbers: true
    });

    // Add an event listener for Ctrl+S to save the file
    editor.setOption('extraKeys', {
        'Ctrl-S': function(cm) {
            const content = cm.getValue();
            const filename = 'story.tgame'; // This should be dynamic
            fetch('/api/save-file', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename, content })
            })
            .then(response => response.json())
            .then(data => console.log('File saved:', data));
        }
    });

    // Fetch a file to display
    fetch(`/api/get-file-content/story.tgame`)
        .then(res => res.text())
        .then(content => editor.setValue(content));
});
```

## Phase 4: Build Process

This step will modify `build_engine.py` to create both GUI and CLI executables.

### Step 4.1: Update `build_engine.py`

Modify the `build_engine.py` script to accept a `--gui` argument.

```
# build_engine.py additions
... (existing imports)

def build_engine_executable():
    ... (existing code)
    
    # Check for command line argument for GUI build
    if len(sys.argv) > 1 and sys.argv[1] == 'gui':
        print("Building GUI Scribe Engine executable...")
        build_type = 'gui'
        pyinstaller_options.append('--noconsole')
        main_script = os.path.join(script_dir, 'gui_launcher.py')
        name = f'scribe-engine-gui-v{version}-{platform_suffix}'
        # Add a placeholder for additional GUI files
        gui_add_data = [
            # Add data files for the GUI
            f'{os.path.join(script_dir, "templates", "launcher.html")}{os.path.sep}templates',
            f'{os.path.join(script_dir, "templates", "_fragments")}{os.path.sep}templates/_fragments',
            # Add other GUI-specific files as needed
        ]
        pyinstaller_args.extend(gui_add_data)
    else:
        print("Building CLI Scribe Engine executable...")
        build_type = 'cli'
        main_script = os.path.join(script_dir, 'main_engine.py')
        name = f'scribe-engine-v{version}-{platform_suffix}'
    
    # Update PyInstaller arguments
    pyinstaller_args.append(main_script)
    pyinstaller_args.append(f'--name={name}')
    
    ... (rest of the build script)
```

This guide provides the foundation for a seamless GUI implementation, offering a more versatile experience for Scribe Engine users.