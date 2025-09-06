
This document outlines the high-level plan for developing a new, GUI-based executable for Scribe Engine. This new version is intended to be an alternative to the existing command-line interface (CLI) and will offer a more intuitive user experience with a built-in editor and live preview.

## Objectives

The primary goals of this project are to:

1. **Offer a new user option:** Provide a separate, GUI-based executable that runs alongside the existing CLI version. Users can choose the interface that best suits their workflow.
    
2. **Enhance usability:** The GUI will provide a user-friendly way to manage projects (create, load, build) without needing to type commands.
    
3. **Integrate a code editor:** The GUI will include a built-in editor with syntax highlighting for `.tgame` files.
    
4. **Provide a live preview:** The editor will be paired with a live, in-app preview of the game, creating a powerful, real-time development loop.
    
5. **Maintain architectural separation:** The new GUI will leverage the existing Flask backend and core engine logic without modifying the CLI's `main_engine.py` script.
    

## Core Concepts

The new GUI will be built on the following architectural principles:

- **HTML/CSS/JS Frontend:** The user interface will be created using standard web technologies. This approach is made possible by the existing `pywebview` integration, which wraps the web frontend in a native desktop window.
    
- **HTMX for UI/UX:** For the launcher's user interface (e.g., the project list and menus), HTMX will be used to handle dynamic updates. This reduces the amount of complex JavaScript needed for managing UI state and allows the server to serve HTML fragments.
    
- **Client-Side Editor:** The `.tgame` editor itself will be a client-side JavaScript component (e.g., CodeMirror). This ensures a responsive and performant editing experience.
    
- **Flask as a Unified Backend:** The Flask application (`app.py`) will serve as the backend for both the GUI and the game itself. It will handle API requests from the GUI to manage files and projects, while also serving the game content for the live preview.
    

## New Files

This plan requires the creation of several new files:

- **`gui_launcher.py`**: A new Python script that will be the entry point for the GUI executable.
    
- **`templates/launcher.html`**: The main HTML file for the GUI's project management interface.
    
- **`templates/editor.html`**: The HTML file containing the in-app editor and live preview.
    
- **`static/css/gui.css`**: CSS for styling the new GUI components.
    
- **`static/js/gui.js`**: JavaScript for handling client-side editor logic.
    
- **`_fragments` directory**: A new directory within `templates` to hold HTML fragments returned by HTMX requests (e.g., `_project_list.html`, `_project_menu.html`).
    

## Updated Files

The following existing files will be modified to support the new GUI:

- **`app.py`**: New Flask routes will be added to handle GUI-specific API requests (e.g., listing, creating, and saving files).
    
- **`build_engine.py`**: The PyInstaller build script will be updated to handle the creation of a separate GUI executable.
    

## Conclusion

By implementing this plan, Scribe Engine will offer a professional, modern development environment for creators who prefer a graphical interface, while retaining the powerful and flexible CLI for advanced users. The architectural design ensures that both versions of the engine remain cohesive and easy to maintain.