# PyVN - A Python-based Visual Novel Engine

This is a text-based game engine that allows creators to build interactive fiction games using a combination of plain text, HTML, Jinja2 templating, and embedded Python code. The engine is inspired by Twine but provides more programming flexibility through Python integration.

## Setup and Run

1.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Creating a New Game

To create a new game project, use the `create_game.py` script:

```bash
python create_game.py <your_project_name>
```

This will create a new directory under `games/` with the specified name, containing the basic project structure (e.g., `project.json`, `story.tgame`, `saves/`, `assets/`).

## Running Your Game

1.  **Set your project:** Open `app.py` and change the `GAME_PROJECT_PATH` variable to point to your new project (e.g., `GAME_PROJECT_PATH = 'games/your_project_name'`).

2.  **Run the application:**

    ```bash
    python app.py
    ```

3.  **Open your browser** and navigate to `http://127.0.0.1:5000` to play your game.