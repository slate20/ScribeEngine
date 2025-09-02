# PyVN - A Python-based Visual Novel Engine

This is a text-based game engine that allows creators to build interactive fiction games using a combination of plain text, HTML, Jinja2 templating, and embedded Python code. The engine is inspired by Twine but provides more programming flexibility through Python integration.

## Setup and Run

1.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Running the Engine and Developing Your Game

To start the PyVN engine and begin developing or playing a game, use the `launcher.py` script:

```bash
python3 launcher.py
```

Upon running the launcher, you will be presented with options:

*   **Create New Project:** This will prompt you for a new game name and set up a basic project structure under the `game/` directory (e.g., `game/your_project_name`).
*   **Load Existing Project:** This will list all existing game projects found under the `game/` directory and allow you to select one to load.

Once a project is created or selected, the Flask development server will start. You can then open your web browser and navigate to `http://127.0.0.1:5000` to view and interact with your game. Changes to your game files will be reflected in the browser.

## Building a Standalone Game Executable

When you are ready to distribute your game as a standalone executable, use the `build.py` script. This will package the engine and your chosen game into a single executable using PyInstaller and PyWebview.

```bash
python3 build.py <your_project_name>
```

Replace `<your_project_name>` with the name of the game project you wish to build (e.g., `example` or `my_new_game`).

The executable will be generated in the `dist/` directory (e.g., `dist/your_project_name_game`).

## Development Conventions

*   **Language:** Primarily Python.
*   **Web Framework:** Flask is used for handling web requests and serving the game.
*   **Templating:** Jinja2 is used for rendering HTML templates, found in the `templates/` directory.
*   **Game Content:** Game stories and configurations are defined in `.tgame` files and `project.json` within the `game/` directory.
*   **Static Assets:** CSS and JavaScript files are located in the `static/` directory.
*   **Engine Logic:** Core game engine components (parser, executor, state management, storage) are encapsulated within the `engine/` directory.
