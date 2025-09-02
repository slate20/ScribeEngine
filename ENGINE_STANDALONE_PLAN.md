# PyVN Engine Standalone Executable Plan

## Project Goal

The primary goal is to transform the PyVN engine into a distributable, standalone executable application. This involves creating a user-friendly launcher, enabling dynamic game project loading, and implementing a robust build process using PyWebview and PyInstaller to generate platform-specific executables and installers.

## Intended User Flow

1.  **Launch:** User launches the PyVN application (either the engine directly or a dedicated launcher).
2.  **Project Selection/Creation:** The application presents an interface to:
    *   Create a new game project (initializing a skeleton directory).
    *   Select an existing game project.
3.  **Dynamic Loading:** The engine starts, dynamically loading the chosen game project.
4.  **Development:** The user develops their game by editing files directly, viewing changes in a web browser (via the Flask development server running from the terminal).
5.  **Build:** When ready, the user can trigger a build process to create a standalone executable of their game, bundled with the engine, using PyWebview. This build should ideally produce an installer for the target OS (Windows/Linux).

## Plan Overview

This plan is divided into several phases, addressing each aspect of the standalone executable requirement.

### Phase 1: Dynamic Project Loading & Launcher Development

**Objective:** Decouple the game project path from the `app.py` hardcoding and implement a basic launcher for project selection/creation.

**Tasks:**

1.  **Refactor `app.py` for Dynamic `GAME_PROJECT_PATH`:**
    *   Modify `app.py` to accept the `GAME_PROJECT_PATH` via a command-line argument or an environment variable. A command-line argument is preferred for direct control from the launcher.
    *   Update the `GameEngine` initialization to use this dynamic path.
    *   Example: `python app.py --project /path/to/your/game`
2.  **Develop `launcher.py`:**
    *   Create a new Python script `launcher.py` in the project root.
    *   **New Project Creation:**
        *   Implement functionality to prompt the user for a new game project name.
        *   Utilize or adapt the logic from `create_game.py` to create the new project directory structure (`game/<project_name>/`).
        *   Ensure `project.json`, `story.tgame`, `assets/`, and `saves/` are correctly initialized.
    *   **Existing Project Selection:**
        *   Implement functionality to list existing game projects within the `game/` directory.
        *   Allow the user to select one of these projects.
    *   **Launch Engine:**
        *   Once a project is created or selected, `launcher.py` will execute `app.py`, passing the chosen project's absolute path as an argument.
        *   This will likely involve using Python's `subprocess` module to run `app.py`.

### Phase 2: PyWebview Integration for Standalone Build

**Objective:** Prepare the application for packaging with PyWebview during the build process to create a desktop window for the final executable.

**Tasks:**

1.  **Install PyWebview:** Add `pywebview` to `requirements.txt`.
2.  **Create `webview_wrapper.py`:**
    *   Create a new Python script (e.g., `webview_wrapper.py`) that will serve as the entry point for the PyWebview-wrapped executable.
    *   This script will:
        *   Start the Flask application (from `app.py`) in a separate thread.
        *   Once the Flask server is running, use `webview.create_window()` to open a desktop window pointing to the Flask server's URL (`http://127.0.0.1:5000`).
        *   Handle graceful shutdown of both Flask and PyWebview when the window is closed.
3.  **Asset Pathing Review:**
    *   Verify that all static assets (CSS, JS, images) and game-specific assets (`game/assets/`) are correctly served and accessible when running through PyWebview. Flask's `static_folder` and `send_file` should handle this, but it's crucial to test within the built executable.

### Phase 3: Build Process with PyInstaller

**Objective:** Create a script to package the entire application (engine, launcher, game projects, assets) into a standalone executable using PyInstaller.

**Tasks:**

1.  **Install PyInstaller:** Add `pyinstaller` to `requirements.txt`.
2.  **Develop `build.py` Script:**
    *   Create a new Python script `build.py` in the project root.
    *   This script will be responsible for invoking PyInstaller.
    *   **PyInstaller Configuration:**
        *   Determine the main entry point for PyInstaller (now `webview_wrapper.py` for the standalone build, or `launcher.py` if building the launcher itself).
        *   Configure PyInstaller to include all necessary files and directories:
            *   `engine/` directory
            *   `templates/` directory
            *   `static/` directory
            *   `game/` directory (including all default game skeletons and potentially user-created ones for distribution)
            *   `app.py`, `config.py`, `create_game.py`, `launcher.py`, `webview_wrapper.py`, `requirements.txt` (or relevant parts)
            *   Any other Python modules or data files.
        *   Use PyInstaller's `--onefile` or `--onedir` option. `--onedir` is often easier for debugging and including complex directory structures.
        *   Use `--add-data` to correctly bundle non-Python files (e.g., `templates`, `static`, `game`).
        *   Consider platform-specific options (e.g., `--windowed` for GUI applications on Windows).
    *   **Installer Generation (Future Consideration):**
        *   While PyInstaller creates an executable, generating a full OS-specific installer (e.g., MSI for Windows, .deb/.rpm for Linux) is a more advanced step. This plan will focus on getting a working executable first. Tools like NSIS (Windows) or `fpm` (Linux) could be explored in a later phase. For now, the output will be a self-contained directory or a single executable.

### Phase 4: Testing and Refinement

**Objective:** Thoroughly test the new functionalities and ensure a smooth user experience.

**Tasks:**

1.  **Unit/Integration Testing:**
    *   Test the dynamic `GAME_PROJECT_PATH` loading in `app.py`.
    *   Test the new project creation and existing project selection in `launcher.py`.
    *   Test the `launcher.py`'s ability to correctly launch `app.py` with the chosen project.
2.  **Standalone Executable Testing:**
    *   Verify that the Flask application runs correctly within the PyWebview window of the *built executable*.
    *   Check all routes, asset loading, and game functionality (saving/loading) within the standalone window.
3.  **PyInstaller Build Testing:**
    *   Perform builds on target operating systems (Windows, Linux).
    *   Test the generated executables:
        *   Do they launch correctly?
        *   Can new projects be created (if the launcher is also built)?
        *   Can existing projects be loaded?
        *   Does the game run as expected?
        *   Are all assets and dependencies correctly bundled?
4.  **Documentation:** Update `README.md` and `GEMINI.md` with instructions for running the launcher, developing games, and building standalone executables.

## Dependencies

*   `pywebview`
*   `pyinstaller`

## Potential Challenges & Considerations

*   **Pathing in Bundled Executables:** PyInstaller changes the execution environment. Absolute and relative paths for assets and game files will need careful handling, often requiring `sys._MEIPASS` for PyInstaller's temporary extraction directory.
*   **Flask Server in PyWebview Wrapper:** Ensuring the Flask server starts in a separate thread and is accessible to PyWebview, and that it shuts down cleanly when the PyWebview window is closed.
*   **Cross-Platform Compatibility:** While Python and PyWebview are cross-platform, specific build configurations and installer generation will be OS-dependent.
*   **User Experience of Launcher:** A simple CLI launcher will suffice for now, but a GUI launcher could be considered for a more polished experience in a future phase.
*   **Game Project Bundling:** Deciding whether to bundle all `game/` projects into the executable or allow users to specify external game project directories. For a "build your game into an executable" feature, the user's specific game project would need to be bundled.
    *   Add a conditional block in `app.py`'s `if __name__ == '__main__':` section.
    *   If a specific flag (e.g., `--standalone` argument) is present, instead of `app.run()`, start the Flask server in a separate thread and then launch `webview.create_window()` pointing to the Flask server's URL (`http://127.0.0.1:5000`).
    *   Ensure the Flask server is accessible from the PyWebview window.
    *   Handle graceful shutdown of both Flask and PyWebview.
3.  **Asset Pathing Review:**
    *   Verify that all static assets (CSS, JS, images) and game-specific assets (`game/assets/`) are correctly served and accessible when running through PyWebview. Flask's `static_folder` and `send_file` should handle this, but it's crucial to test.

### Phase 3: Build Process with PyInstaller

**Objective:** Create a script to package the entire application (engine, launcher, game projects, assets) into a standalone executable using PyInstaller.

**Tasks:**

1.  **Install PyInstaller:** Add `pyinstaller` to `requirements.txt`.
2.  **Develop `build.py` Script:**
    *   Create a new Python script `build.py` in the project root.
    *   This script will be responsible for invoking PyInstaller.
    *   **PyInstaller Configuration:**
        *   Determine the main entry point for PyInstaller (likely `launcher.py` or a new `main.py` that orchestrates the launcher and engine).
        *   Configure PyInstaller to include all necessary files and directories:
            *   `engine/` directory
            *   `templates/` directory
            *   `static/` directory
            *   `game/` directory (including all default game skeletons and potentially user-created ones for distribution)
            *   `app.py`, `config.py`, `create_game.py`, `launcher.py`, `requirements.txt` (or relevant parts)
            *   Any other Python modules or data files.
        *   Use PyInstaller's `--onefile` or `--onedir` option. `--onedir` is often easier for debugging and including complex directory structures.
        *   Use `--add-data` to correctly bundle non-Python files (e.g., `templates`, `static`, `game`).
        *   Consider platform-specific options (e.g., `--windowed` for GUI applications on Windows).
    *   **Installer Generation (Future Consideration):**
        *   While PyInstaller creates an executable, generating a full OS-specific installer (e.g., MSI for Windows, .deb/.rpm for Linux) is a more advanced step. This plan will focus on getting a working executable first. Tools like NSIS (Windows) or `fpm` (Linux) could be explored in a later phase. For now, the output will be a self-contained directory or a single executable.

### Phase 4: Testing and Refinement

**Objective:** Thoroughly test the new functionalities and ensure a smooth user experience.

**Tasks:**

1.  **Unit/Integration Testing:**
    *   Test the dynamic `GAME_PROJECT_PATH` loading in `app.py`.
    *   Test the new project creation and existing project selection in `launcher.py`.
    *   Test the `launcher.py`'s ability to correctly launch `app.py` with the chosen project.
2.  **PyWebview Functionality Testing:**
    *   Verify that the Flask application runs correctly within the PyWebview window.
    *   Check all routes, asset loading, and game functionality (saving/loading) within the standalone window.
3.  **PyInstaller Build Testing:**
    *   Perform builds on target operating systems (Windows, Linux).
    *   Test the generated executables:
        *   Do they launch correctly?
        *   Can new projects be created?
        *   Can existing projects be loaded?
        *   Does the game run as expected?
        *   Are all assets and dependencies correctly bundled?
4.  **Documentation:** Update `README.md` and `GEMINI.md` with instructions for running the launcher, developing games, and building standalone executables.

## Dependencies

*   `pywebview`
*   `pyinstaller`

## Potential Challenges & Considerations

*   **Pathing in Bundled Executables:** PyInstaller changes the execution environment. Absolute and relative paths for assets and game files will need careful handling, often requiring `sys._MEIPASS` for PyInstaller's temporary extraction directory.
*   **Flask Development Server in PyWebview:** Ensuring the Flask server starts and is accessible to PyWebview, and that it shuts down cleanly.
*   **Cross-Platform Compatibility:** While Python and PyWebview are cross-platform, specific build configurations and installer generation will be OS-dependent.
*   **User Experience of Launcher:** A simple CLI launcher might suffice initially, but a GUI launcher could be considered for a more polished experience.
*   **Game Project Bundling:** Deciding whether to bundle all `game/` projects into the executable or allow users to specify external game project directories. For a "build your game into an executable" feature, the user's specific game project would need to be bundled.

This plan provides a roadmap for achieving the standalone executable goal. Each phase will involve coding, testing, and refinement.