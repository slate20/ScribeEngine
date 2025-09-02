# PyVN: Game Creation Guide

Welcome to PyVN, a Python-based visual novel engine designed for creating interactive fiction games with flexibility and power. This guide will walk you through everything you need to know to build your own games using PyVN.

## Table of Contents

1.  [Introduction to PyVN](#1-introduction-to-pyvn)
2.  [Getting Started](#2-getting-started)
    *   [Obtaining the PyVN Engine](#obtaining-the-pyvn-engine)
    *   [Running the Engine](#running-the-engine)
    *   [First-Run Experience: Setting Your Project Root](#first-run-experience-setting-your-project-root)
    *   [Main Menu Options](#main-menu-options)
3.  [Game Project Structure](#3-game-project-structure)
4.  [Understanding Game State (`game_engine.game_state`)](#4-understanding-game-state-game_enginegame_state)
5.  [Writing Your Story (.tgame files)](#5-writing-your-story-tgame-files)
    *   [Passages](#passages)
    *   [Links](#links)
    *   [Special Passages](#special-passages)
    *   [Text Formatting](#text-formatting)
    *   [HTML Integration](#html-integration)
    *   [Jinja2 Templating](#jinja2-templating)
6.  [Adding Logic (Python Files)](#6-adding-logic-python-files)
    *   [Introduction to Python Logic Files](#introduction-to-python-logic-files)
    *   [Accessing and Modifying Game State](#accessing-and-modifying-game-state)
    *   [Custom Functions](#custom-functions)
    *   [Player and Inventory Management](#player-and-inventory-management)
    *   [Creating Custom Game Objects](#creating-custom-game-objects)
    *   [Game Data and Databases](#game-data-and-databases)
    *   [Manipulating Game State Variables](#manipulating-game-state-variables)
    *   [Handling User Input with `update_game_state` Route](#handling-user-input-with-update_game_state-route)
    
    *   [Conditional Logic](#conditional-logic)
7.  [Assets (assets/ and custom.css)](#7-assets-assets-and-custom-css)
    *   [Images and Audio](#images-and-audio)
    *   [Custom CSS](#custom-css)
8.  [Saving and Loading](#8-saving-and-loading)
9.  [Debugging Your Game](#9-debugging-your-game)
10. [Building Your Game for Distribution](#10-building-your-game-for-distribution)
11. [Advanced Topics](#11-advanced-topics)
    *   [External Python Libraries](#external-python-libraries)
    *   [Custom Flask Routes](#custom-flask-routes)

---

## 1. Introduction to PyVN

PyVN is a powerful visual novel engine built with Python and Flask. It allows you to create interactive stories by combining simple text files (`.tgame`), HTML, and the full power of Python for complex logic. Unlike some other visual novel tools, PyVN emphasizes programming flexibility, making it ideal for developers who want deep control over their game's mechanics and narrative.

## 2. Getting Started

### Obtaining the PyVN Engine

The PyVN engine is distributed as a single, self-contained executable for Windows and Linux. You do not need to install Python or any dependencies separately.

*   **Download:** Obtain the latest `pyvn-engine` executable for your operating system from the official distribution channels (e.g., GitHub releases).

### Running the Engine

Simply run the `pyvn-engine` executable.

*   **Windows:** Double-click `pyvn-engine.exe`.
*   **Linux:** Make the executable runnable (`chmod +x pyvn-engine`) and then run `./pyvn-engine`.

The engine will launch in your terminal.

### First-Run Experience: Setting Your Project Root

The first time you run the `pyvn-engine`, or if your project root path is not configured, the engine will prompt you to set a directory where all your PyVN game projects will be stored.

```
No project root configured or found. Please specify one.
Enter the path for your PyVN game projects (e.g., ~/PyVN_Games):
```

Enter an absolute path (e.g., `/home/youruser/PyVN_Games` on Linux, or `C:\Users\YourUser\Documents\PyVN_Games` on Windows). The engine will create this directory if it doesn't exist and save it for future sessions.

You can change this project root at any time from the main menu (Option 4). You can also override it for a single session by running the engine with the `--project-root` or `-r` argument:

```bash
./pyvn-engine --project-root /path/to/another/games/folder
```

### Main Menu Options

Once the engine is running and a project root is set, you'll see the main menu:

```
--- PyVN Engine Launcher (Project Root: /path/to/your/PyVN_Games) ---

Options:
1. Create New Project
2. Load Existing Project
3. Build Standalone Game
4. Change Project Root Path
5. Exit
```

*   **1. Create New Project:** Guides you through creating a new game project with a basic skeleton structure.
*   **2. Load Existing Project:** Lists projects in your current project root and allows you to select one to load for development. This will start the Flask development server.
*   **3. Build Standalone Game:** Allows you to select an existing game project and build it into a distributable executable.
*   **4. Change Project Root Path:** Prompts you to set a new directory for your PyVN game projects.
*   **5. Exit:** Closes the engine.

## 3. Game Project Structure

### 3.1 `project.json` Configuration Reference

### 3.1.1 Available CSS Variables for Theming

When `theme.enabled` is `true` in your `project.json`, PyVN generates CSS variables (`--variable-name`) based on your `theme.colors` and `theme.fonts` configurations. These variables can then be used in your `custom.css` to ensure consistent styling throughout your game.

Additionally, the engine defines some default CSS variables that you can override in your `project.json` or `custom.css`.

#### Colors (from `theme.colors` in `project.json`):

For every key-value pair in `theme.colors`, a CSS variable `--<key>-color` is generated.
**Example:** If `project.json` has `"primary_color": "#FF0000"`, then `--primary-color: #FF0000;` is available.

Commonly used color variables (defined in `static/css/theme.css` and can be overridden):
*   `--primary-color`: Main accent color.
*   `--secondary-color`: Secondary accent color, often used for hover states.
*   `--background-color`: Main background color of the game.
*   `--content-bg`: Background color for main content areas.
*   `--text-color`: Default text color.
*   `--link-color`: Color for navigation and passage links.
*   `--nav-bg`: Background color for the navigation menu.
*   `--button-bg`: Background color for buttons.
*   `--button-text`: Text color for buttons.
*   `--border-color`: Color for borders and separators.
*   `--error-bg`: Background color for error messages.
*   `--error-text`: Text color for error messages.
*   `--success-text`: Text color for success messages.
*   `--info-text`: Text color for informational messages.
*   `--footer-text`: Text color for footer content.

#### Fonts (from `theme.fonts` in `project.json`):

For every key-value pair in `theme.fonts`, a CSS variable `--font-family-<key>` is generated.
**Example:** If `project.json` has `"body_font": "'Arial', sans-serif"`, then `--font-family-body_font: 'Arial', sans-serif;` is available.

Commonly used font variables (defined in `static/css/theme.css` and can be overridden):
*   `--font-family-body`: Font family for general body text.
*   `--font-family-heading`: Font family for headings and titles.

#### Other Default CSS Variables (defined in `static/css/engine.css`):

These variables are defined by the engine and are not directly controlled by `project.json`'s `theme` section, but you can override them in your `custom.css` if needed.
*   `--debug-bg`: Background color for the debug panel.
*   `--debug-text`: Text color for the debug panel.

**How to Use in `custom.css`:**

```css
/* Example custom.css */
body {
    background-color: var(--background-color); /* Use the background color from project.json */
    color: var(--text-color); /* Use the text color from project.json */
    font-family: var(--font-family-body); /* Use the body font from project.json */
}

h1, h2, h3 {
    font-family: var(--font-family-heading); /* Use the heading font from project.json */
    color: var(--primary-color); /* Use the primary color from project.json */
}

.my-custom-element {
    border: 1px solid var(--border-color);
    background-color: var(--content-bg);
}
```

The `project.json` file is the central configuration file for your game. It defines various game-wide settings, features, and theme options. Below are the key fields you can configure:

*   **`title`** (string, required): The title of your game. This will be displayed in the browser tab and can be accessed in templates via `{{ game_title }}`.
    *   **Example:** `"title": "My Epic Adventure"`
*   **`author`** (string, optional): The author(s) of the game.
    *   **Example:** `"author": "Jane Doe"`
*   **`main_story_file`** (string, optional): Specifies the primary `.tgame` file that contains the `:: start` passage. If omitted, the engine will look for `story.tgame` by default.
    *   **Example:** `"main_story_file": "my_game_story.tgame"`
*   **`features`** (object, optional): Configures various engine features.
    *   **`use_default_player`** (boolean, default: `true`): If `true`, the engine initializes a default `player` object with `name`, `health`, `score`, `experience`, and `level` attributes. If `false`, you are responsible for defining and managing the `player` object in your Python logic.
        *   **Example:** `"use_default_player": true`
    *   **`use_default_inventory`** (boolean, default: `true`): If `true`, the engine initializes a default `inventory` list within the `player` object and enables helper functions like `add_to_inventory`, `remove_from_inventory`, `has_item`, and `get_item_count`. Requires `use_default_player` to be `true`. If `false`, you manage inventory manually.
        *   **Example:** `"use_default_inventory": true`
*   **`nav`** (object, optional): Configures the navigation menu.
    *   **`enabled`** (boolean, default: `true`): If `true`, the `:: NavMenu` passage content will be rendered as a navigation menu.
        *   **Example:** `"enabled": true`
    *   **`position`** (string, default: `"horizontal"`): Specifies the position of the navigation menu. Currently supports `"horizontal"`, `"vertical-left"`, and `"vertical-right"`.
        *   **Example:** `"position": "horizontal"`
*   **`theme`** (object, optional): Configures the game's visual theme.
    *   **`enabled`** (boolean, default: `true`): If `true`, custom theme colors and fonts defined here will be applied via CSS variables.
        *   **Example:** `"enabled": true`
    *   **`use_engine_defaults`** (boolean, default: `true`): If `true`, the engine's default CSS styles will be applied. If `false`, only your custom CSS (from `custom.css` and `theme` settings) will be used.
        *   **Example:** `"use_engine_defaults": true`
    *   **`colors`** (object, optional): A dictionary of custom color variables. These are converted into CSS variables (e.g., `primary_color` becomes `--primary_color`). You can then use these in your `custom.css`.
        *   **Example:**
            ```json
            "colors": {
                "primary_color": "#4CAF50",
                "background_color": "#212121",
                "text_color": "#E0E0E0"
            }
            ```
    *   **`fonts`** (object, optional): A dictionary of custom font families. These are converted into CSS variables (e.g., `body_font` becomes `--font-family-body_font`).
        *   **Example:**
            ```json
            "fonts": {
                "body_font": "'Roboto', sans-serif",
                "heading_font": "'Georgia', serif"
            }
            ```

**Example `project.json`:**

```json
{
    "title": "My First PyVN Game",
    "author": "Game Creator",
    "main_story_file": "story.tgame",
    "features": {
        "use_default_player": true,
        "use_default_inventory": true
    },
    "nav": {
        "enabled": true,
        "position": "horizontal"
    },
    "theme": {
        "enabled": true,
        "use_engine_defaults": true,
        "colors": {
            "primary_color": "#4CAF50",
            "background_color": "#212121",
            "text_color": "#E0E0E0"
        },
        "fonts": {
            "body_font": "'Roboto', sans-serif",
            "heading_font": "'Georgia', serif"
        }
    }
}
```

When you create a new project (e.g., `MyGame`), PyVN sets up a basic directory structure. However, the engine is flexible and allows for more organized structures:

```
MyGame/
├── project.json
├── story.tgame             # Main story file
├── custom.css              # Optional custom CSS
├── systems.py              # Optional custom Python logic
├── assets/                 # Media assets (images, audio, video)
├── saves/                  # Game save files
└── # You can add subdirectories for:
    # ├── story/              # More .tgame files (e.g., chapter1.tgame, chapter2.tgame)
    # ├── scripts/            # More Python logic files (e.g., quests.py, combat.py)
    # └── data/               # Data files (e.g., items.py, npcs.json)
```

*   **`project.json`**: The main configuration file for your game. It defines the game's title, author, and various features and theme settings.
*   **`.tgame` files**: These are your story files. The engine automatically discovers and parses all `.tgame` files within your project directory and its subdirectories. This allows you to organize your narrative into multiple files and folders (e.g., `story/chapter1.tgame`, `story/chapter2.tgame`).
*   **Python (`.py`) files**: These files contain your custom game logic. The engine automatically loads all `.py` files found within your project directory and its subdirectories. This means you are not limited to `systems.py`; you can create separate files like `quests.py`, `combat.py`, `data.py`, etc., to keep your code organized.
*   **`custom.css`**: An optional CSS file for custom styling of your game's web interface.
*   **`assets/`**: A directory to store all your game's media assets, such as images, audio files, and videos.
*   **`saves/`**: This directory is automatically managed by the engine to store game save files.

## 4. Understanding Game State and Direct Access

The game state is the central nervous system of your PyVN game. It's a dynamic Python dictionary that holds all the mutable data representing the current state of your game. Think of it as the game's memory, where everything from player attributes to quest progress and NPC locations is stored.

**What's Stored in the Game State?**
The game state is structured to hold key game data:
*   **`player`:** An object (accessible via `player.attribute`) containing player-specific data like `name`, `health`, `inventory`, `score`, and any custom attributes you add.
*   **`flags`:** A dictionary (accessible via `flags['flag_name']` or `get_flag('flag_name')`) for boolean states (e.g., `door_unlocked: True`, `quest_started: False`).
*   **`variables`:** A dictionary (accessible via `variables['var_name']` or `get_variable('var_name')`) for general game data (e.g., `day_count: 5`, `current_location: 'forest'`).
*   **Any Custom Data:** You can add any Python-compatible data structure (dictionaries, lists, numbers, strings, booleans) to the game state to track anything relevant to your game.

**How it Works:**
*   When your game starts, the game state is initialized based on your `project.json` (e.g., default player/inventory).
*   As the player makes choices, interacts with the world, or progresses through the story, your Python logic modifies this game state.
*   Jinja2 templates in your `.tgame` files then read from the game state to display dynamic content (e.g., `{{ player.name }}`, `{% if flags.door_unlocked %}`).
*   When a game is saved, the entire game state is serialized (converted to JSON) and stored. When loaded, it's deserialized back, restoring the game to its exact previous state.

**Accessing and Modifying Game State:**
Crucially, PyVN makes interacting with the game state **direct and concise** from your Python logic files and Jinja2 templates. You **do not** need to import or reference a `game_engine` object. Instead, `player`, `flags`, `variables`, and a set of helper functions are automatically available in the global scope of your game's Python code.

**Note on Accessing Nested Data:**
While `player.attribute`, `flags['flag_name']`, and `variables['var_name']` provide direct access, for deeply nested data within `variables` (or other dictionaries you add to the game state), using the `get_variable('path.to.data', default_value)` helper function is recommended. This function supports dot notation for nested access and allows you to provide a default value if the path does not exist, preventing errors.

## 5. Writing Your Story (.tgame files)

PyVN stories are written in `.tgame` files, which are plain text files using a simple markup language.

### Passages

Your story is divided into "passages." Each passage represents a distinct section of your narrative or a screen in your game. Passages begin with `::` followed by the passage name.

```
:: Start
Welcome to my first PyVN game!

:: ForestPath
You are on a path in a dark forest.
```

### Links

You can create links between passages using double square brackets `[[ ]]`. The format is `[[Link Text->PassageName]]`.

```
:: Start
Welcome to my first PyVN game!
[[Begin Adventure->ForestPath]]

:: ForestPath
You are on a path in a dark forest.
[[Go deeper->DeepForest]]
[[Return to start->Start]]
```

### Special Passages

PyVN recognizes a few special passage names that serve specific functions:

*   **`:: NavMenu`**: Content in this passage is rendered as a navigation menu, typically at the top or side of the screen. It's ideal for global links like "Inventory," "Stats/Skills," or "Journal/Quests."
*   **`:: PrePassage`**: Content in this passage is rendered *before* every other passage. Useful for HUD elements, persistent banners, or global scripts.
*   **`:: PostPassage`**: Content in this passage is rendered *after* every other passage. Useful for footers, copyright notices, or global scripts.

Example `NavMenu` (from a new project):

```
:: NavMenu
[[Home->start]]
```

### Text Formatting

PyVN supports basic text formatting within passages. These are interpreted as HTML:

*   **Bold:** `**bold text**` or `<b>bold text</b>`
*   **Italics:** `*italic text*` or `<i>italic text</i>`
*   **Underline:** `<u>underline text</u>`
*   **Line Breaks:** Use a blank line for a paragraph break, or `<br>` for a single line break.

### HTML Integration

You can embed raw HTML directly within your `.tgame` passages. This gives you full control over layout and styling.

```
:: MyCustomPassage
<h1>Chapter 1: The Beginning</h1>
<p style="color: blue;">This is a paragraph with custom styling.</p>
<img src="/game/assets/my_image.png" alt="A beautiful scene">
```

### Jinja2 Templating

PyVN uses Jinja2, a powerful templating engine, to render your `.tgame` passages. This allows for dynamic content based on your game's state.

*   **Displaying Variables:** Use double curly braces `{{ }}` to display the value of a variable from the game state.

    ```
    :: Welcome
    Hello, {{ player.name }}! You have {{ player.health }} health points.
    ```

*   **Control Structures:** Use `{% %}` for logic like `if` statements and `for` loops.

    ```
    :: CheckItem
    {% if player.has_item('key') %}
    You have the key!
    {% else %}
    You need a key to proceed.
    {% endif %}

    :: Inventory
    Your items:
    {% for item in player.inventory %}
    - {{ item.name }}
    {% endfor %}
    ```

*   **Accessing Game State:** Common variables like `player` (for player attributes like `name`, `health`, `inventory`), `flags`, `variables`, and `game_title` are directly available.
    *   **Note on Nested Data:** While direct access like `{{ variables.some_key }}` works for top-level keys, for deeply nested data (e.g., `variables = {'quest': {'main_quest': {'status': 'started'}}}`), you cannot use `{{ variables.quest.main_quest.status }}` directly. Instead, use dictionary-style access (`{{ variables['quest']['main_quest']['status'] }}`) or, more robustly, the `get_variable` helper function (`{{ get_variable('quest.main_quest.status', 'not_started') }}`). The `get_variable` function also allows you to specify a default value if the variable path does not exist, preventing errors.

### Python Code Blocks

You can embed Python code directly within your `.tgame` passages using `{%- python %}` and `{%- endpython %}` tags. This allows you to execute complex game logic, modify the game state, or call custom functions defined in your Python logic files directly from your story.

Any Python code placed within these blocks will be executed when the passage is rendered. The `player` object, `flags` dictionary, `variables` dictionary, and all helper functions (like `set_flag`, `get_flag`, `set_variable`, `get_variable`, `add_to_inventory`, `debug`, etc.) are directly available in the scope of these blocks.

**Syntax:**

```
{%- python %}
# Your Python code here
player.health -= 10
set_flag('took_damage', True)
debug("Player took 10 damage!")
{%- endpython %}
```

**Example Usage:**

```
:: DarkCave
You enter a dark cave.

{%- python %}
import random
if random.randint(1, 10) > 7:
    set_flag('found_torch', True)
    add_to_inventory('torch', 1)
    debug("Player found a torch!")
{%- endpython %}

{% if get_flag('found_torch') %}
<p class="success">You found a torch on the ground!</p>
{% endif %}

The cave extends deeper into darkness.

[[Continue deeper->CaveDepths]]
```

## 6. Adding Logic (Python Files)

### 6.1 Engine-Provided Functions and Objects

PyVN automatically makes several functions and objects available in the global scope of your game's Python code (both within `{%- python %}` blocks in `.tgame` files and in your external `.py` logic files). These are designed to simplify interaction with the game state and engine features.

#### Directly Accessible Objects:

*   **`player`**: An object representing the player character. Its attributes (e.g., `player.name`, `player.health`, `player.score`, `player.experience`, `player.level`) are automatically initialized based on `project.json` settings (`use_default_player`). You can add custom attributes to `player` directly (e.g., `player.mana = 100`).
    *   **Example:**
        ```python
        player.health -= 10
        debug(f"Player's health is now {player.health}")
        ```
*   **`flags`**: A dictionary for managing boolean (true/false) states in your game. Useful for tracking events that have occurred.
    *   **Example:**
        ```python
        flags['door_unlocked'] = True
        if flags['quest_completed']:
            debug("Quest is done!")
        ```
*   **`variables`**: A dictionary for storing general game data that doesn't fit into `player` or `flags`. Can hold any Python-compatible data structure.
    *   **Example:**
        ```python
        variables['day_count'] = 5
        variables['current_location'] = 'forest'
        variables['npcs'] = {'guard': {'health': 50}}
        ```
*   **`project_path`**: A string containing the absolute path to the current game project's root directory. Useful for loading external data files (e.g., JSON, CSV) relative to your project.
    *   **Example:**
        ```python
        import os
        data_file = os.path.join(project_path, 'data', 'items.json')
        debug(f"Loading items from: {data_file}")
        ```

#### Helper Functions:

*   **`set_flag(name: str, value: bool = True)`**: Sets the value of a flag.
    *   `name`: The name of the flag (string).
    *   `value`: The boolean value to set (defaults to `True`).
    *   **Example:**
        ```python
        set_flag('puzzle_solved')
        set_flag('door_locked', False)
        ```
*   **`get_flag(name: str, default: bool = False)`**: Retrieves the value of a flag.
    *   `name`: The name of the flag (string).
    *   `default`: The value to return if the flag is not found (defaults to `False`).
    *   **Example:**
        ```python
        if get_flag('puzzle_solved'):
            debug("Puzzle was already solved.")
        ```
*   **`set_variable(key: str, value: Any)`**: Sets a variable in the game state. Supports dot notation for nested dictionaries (e.g., `'player.mana'`, `'quest.status'`). Automatically creates intermediate dictionaries if they don't exist.
    *   `key`: The variable path using dot notation (string).
    *   `value`: The value to set.
    *   **Example:**
        ```python
        set_variable('player.mana', 100)
        set_variable('quest.main_quest.status', 'started')
        ```
*   **`get_variable(key: str, default: Any = None)`**: Retrieves a variable from the game state. Supports dot notation for nested dictionaries.
    *   `key`: The variable path using dot notation (string).
    *   `default`: The value to return if the variable path is not found (defaults to `None`).
    *   **Example:**
        ```python
        current_mana = get_variable('player.mana', 0)
        quest_status = get_variable('quest.main_quest.status', 'not_started')
        ```
*   **`add_to_inventory(item: str, quantity: int = 1)`**: Adds an item to the player's inventory. If the item already exists, its quantity is updated. Requires `use_default_inventory` to be `true` in `project.json`.
    *   `item`: The name of the item (string).
    *   `quantity`: The amount to add (integer, defaults to `1`).
    *   **Example:**
        ```python
        add_to_inventory('gold_coin', 5)
        add_to_inventory('healing_potion')
        ```
*   **`remove_from_inventory(item: str, quantity: int = 1)`**: Removes an item from the player's inventory. If the quantity to remove is greater than or equal to the current quantity, the item is removed entirely. Requires `use_default_inventory` to be `true` in `project.json`.
    *   `item`: The name of the item (string).
    *   `quantity`: The amount to remove (integer, defaults to `1`).
    *   **Example:**
        ```python
        remove_from_inventory('gold_coin', 2)
        remove_from_inventory('healing_potion')
        ```
*   **`has_item(item: str)`**: Checks if the player has a specific item in their inventory. Requires `use_default_inventory` to be `true` in `project.json`.
    *   `item`: The name of the item (string).
    *   **Example:**
        ```python
        if has_item('key'):
            debug("Player has the key!")
        ```
*   **`get_item_count(item: str)`**: Returns the quantity of a specific item in the player's inventory. Requires `use_default_inventory` to be `true` in `project.json`.
    *   `item`: The name of the item (string).
    *   **Example:**
        ```python
        num_potions = get_item_count('healing_potion')
        debug(f"Player has {num_potions} healing potions.")
        ```
*   **`debug(message: Any)`**: Prints a debug message to the Flask server console (where the engine is running). Only active when `debug_mode` is enabled.
    *   `message`: The message to print. Can be any Python object.
    *   **Example:**
        ```python
        debug("A critical event occurred!")
        debug(player.health)
        ```
*   **`now()`**: A function that returns the current `datetime` object. Useful for timestamping or time-based logic.
    *   **Example:**
        ```python
        current_time = now()
        debug(f"Current game time: {current_time.strftime('%H:%M:%S')}")
        ```

For more complex game mechanics, custom functions, or interaction with external data, you'll use Python files within your game project. The engine automatically loads all `.py` files found in your project directory and its subdirectories. This means you are not limited to a single `systems.py` file; you can create multiple Python files (e.g., `quests.py`, `combat.py`, `data.py`) to organize your game logic.

### Introduction to Python Logic Files

Any `.py` file in your game project is where you define Python functions and classes that can manipulate the game state or perform actions. These functions can then be called directly from your `.tgame` passages using Jinja2's `{% do %}` tag or from within Python code blocks (`{%- python %}`).

Example `systems.py` (or any other Python file):

```python
# systems.py (or quests.py, combat.py, etc.)
def give_item(item_name):
    # Directly access player and helper functions
    # Note: player, flags, variables, and helper functions like add_to_inventory, debug
    # are automatically available in the global scope of your game's Python files.
    add_to_inventory(item_name)
    debug(f"Player received: {item_name}") # Use debug() for console output

def check_health():
    # Directly access player
    return player.health
```

### Accessing and Modifying Game State

Within `systems.py` (or any Python code loaded by the engine), you can directly access and modify the game state using the `player` object, `flags` dictionary, `variables` dictionary, and the provided helper functions.

```python
# Example of modifying game state
def decrease_health(amount):
    player.health = max(0, player.health - amount)
    debug(f"Player health decreased by {amount}. New health: {player.health}")

def set_player_name(name):
    player.name = name
    debug(f"Player name set to: {player.name}")
```

### Custom Functions

To call a function from `systems.py` within a `.tgame` passage, use the `{% do %}` tag:

```
:: Encounter
A monster attacks!
{% do decrease_health(10) %}
Your health is now {{ player.health }}.

:: Start
What is your name?
{% do set_player_name(input_from_form) %} {# Assuming input_from_form is a variable from a web form #}
```

### Player and Inventory Management

PyVN provides basic `player` and `inventory` objects in the game state by default if `use_default_player` and `use_default_inventory` are set to `true` in your game's `project.json` file.

*   **Using Default Objects:** If enabled, you can interact with these directly:
    *   `player.name`
    *   `player.health`
    *   `player.inventory` (a list of dictionaries, e.g., `[{'name': 'Sword'}, {'name': 'Shield'}]`)
    You can add custom attributes to the `player` object as needed (e.g., `player.mana = 100`).

*   **Replacing Default Objects:** If you wish to implement your own custom player or inventory system, you can disable the default objects by setting `use_default_player` and/or `use_default_inventory` to `false` in your `project.json`:

    ```json
    "features": {
        "use_default_player": false,
        "use_default_inventory": false
    }
    ```
    When disabled, the engine will not initialize these objects. You are then free to define your own `player` and `inventory` (or any other custom objects) within your Python logic files and manage them directly.

### Creating Custom Game Objects

The game state is a flexible Python dictionary that serves as the central storage for all your game's dynamic data. You can add any new key-value pairs to it from your Python logic files (`systems.py` or any other `.py` file you create). This allows you to define and manage custom objects like NPCs, quests, locations, or any other game-specific data.

**Example: Creating an `npcs` object**

```python
# In your game's systems.py or a new file like npcs.py
# You can directly modify the 'variables' dictionary for custom top-level objects
def initialize_npcs():
    ### Creating Custom Game Objects

The game state is a flexible Python dictionary that serves as the central storage for all your game's dynamic data. You can add any new key-value pairs to it from your Python logic files (`systems.py` or any other `.py` file you create). This allows you to define and manage custom objects like NPCs, quests, locations, or any other game-specific data.

**Example: Creating an `npcs` object**

```python
# In your game's systems.py or a new file like npcs.py
# You can directly modify the 'variables' dictionary for custom top-level objects
def initialize_npcs():
    variables['npcs'] = {
        'guard': {'name': 'Guard', 'health': 50, 'dialogue': 'Halt!'},
        'merchant': {'name': 'Merchant', 'gold': 100, 'inventory': ['potion', 'map']}
    }

# Call this function once, perhaps at the start of your game or a specific chapter
# For example, in a passage: {% do initialize_npcs() %}
```

Once `npcs` is added to the game state (e.g., via `variables['npcs']`), you can access its properties in your `.tgame` files using Jinja2:

```
:: TownSquare
You see {{ variables.npcs.guard.name }} standing by the gate. He says: "{{ variables.npcs.guard.dialogue }}"
The merchant has {{ variables.npcs.merchant.gold }} gold.
```

You can also modify these objects from your Python logic:

```python
# In your game's systems.py or a new file
def give_gold_to_merchant(amount):
    if 'merchant' in variables.get('npcs', {}):
        variables['npcs']['merchant']['gold'] += amount
        debug(f"Merchant now has {variables['npcs']['merchant']['gold']} gold.")
    else:
        debug("Merchant not found!")
```

### Game Data and Databases

For managing larger sets of static game data, such as item definitions, NPC templates, quest details, or skill trees, it's highly recommended to use dedicated Python files (or JSON files) rather than embedding them directly in `.tgame` passages. This keeps your data organized, easily maintainable, and separate from your narrative.

**Recommended Approach: Python Data Files**

Create a new Python file (e.g., `game_data.py`, `items.py`, `npcs.py`) within your game project directory (or a subdirectory like `data/`). In this file, you can define your data using Python dictionaries, lists, or classes.

Example `game/my_game/items.py`:

```python
# game/my_game/items.py
ITEM_DATABASE = {
    "sword": {"name": "Sword", "damage": 10, "weight": 5, "description": "A sharp blade."},
    "shield": {"name": "Shield", "defense": 8, "weight": 7, "description": "A sturdy shield."},
    "potion": {"name": "Healing Potion", "heal_amount": 25, "consumable": True, "description": "Restores health."}
}

def get_item_details(item_id):
    return ITEM_DATABASE.get(item_id)
```

Then, in your `systems.py` (or other logic files), you can import and use this data:

```python
# game/my_game/systems.py
from items import get_item_details # Import from your new items.py file

def give_item_to_player(item_id):
    item_data = get_item_details(item_id)
    if item_data:
        # Add a copy of the item data to the player's inventory
        add_to_inventory(item_data['name'], 1) # Use helper for inventory
        debug(f"Player received: {item_data['name']}")
    else:
        debug(f"Item '{item_id}' not found in database.")

def get_npc_dialogue(npc_id, dialogue_key):
    # Assuming you have an NPC_DATABASE similar to ITEM_DATABASE
    from npcs import NPC_DATABASE # Example import
    npc = NPC_DATABASE.get(npc_id)
    if npc and dialogue_key in npc:
        return npc[dialogue_key]
    return ""
```

**Using JSON Files for Data**

Alternatively, for purely data-driven content, you can store your data in JSON files (e.g., `data/items.json`, `data/npcs.json`). You would then load these files in your Python logic using Python's built-in `json` module.

Example `game/my_game/data/items.json`:

```json
{
    "sword": {"name": "Sword", "damage": 10, "weight": 5},
    "shield": {"name": "Shield", "defense": 8, "weight": 7}
}
```

Example of loading in Python:

```python
# In your game's systems.py or a dedicated data loading file
import json
import os

# Note: project_path is available in the global scope of your game's Python files
def load_item_data():
    data_path = os.path.join(project_path, 'data', 'items.json')
    with open(data_path, 'r') as f:
        variables['item_definitions'] = json.load(f) # Store in variables

# Call load_item_data() at game start or when needed.
```

Choose the method that best suits your data structure and workflow. Python files offer more flexibility for complex data structures and functions, while JSON files are simpler for static, hierarchical data.

### Manipulating Game State Variables

Understanding how to directly manipulate the game state is crucial for dynamic gameplay. PyVN provides convenient helper functions that are directly available in your game's Python code to simplify setting and getting variables, especially for nested data using dot notation.

#### `set_variable(key, value)`

This function allows you to set a value in the game state using a string `key` that can include dot notation for nested dictionaries (e.g., `'player.name'`, `'quest.main_quest.status'`). It will automatically create intermediate dictionaries if they don't exist.

**Example: Setting Player Health and Name**

Let's say you want to set the player's health and name at the start of a passage or after an event.

**1. In your `systems.py` (or another Python logic file):**

```python
# systems.py
def initialize_player_stats():
    set_variable('player.health', 100)
    set_variable('player.name', 'Hero')
    set_variable('player.inventory', []) # Initialize inventory as a list
    debug(f"Player initialized: {get_variable('player.name')} with {get_variable('player.health')} health.")

def decrease_player_health(amount):
    current_health = get_variable('player.health', 0) # Get current health, default to 0 if not set
    set_variable('player.health', max(0, current_health - amount))
    debug(f"Player health decreased by {amount}. New health: {get_variable('player.health')}")
```

**2. In your `.tgame` file:**

You can call these functions using the `{% do %}` tag.

```
:: StartGame
{% do initialize_player_stats() %}
Your adventure begins, {{ player.name }}! You have {{ player.health }} health points.

:: TrapRoom
You fall into a trap!
{% do decrease_player_health(20) %}
Your health is now {{ player.health }}.
[[Continue->NextRoom]]
```

#### `get_variable(key, default=None)`

This function allows you to retrieve a value from the game state using a string `key` that can include dot notation. You can also provide a `default` value to be returned if the key is not found, preventing errors.

**Example: Displaying a Variable**

```
:: StatusScreen
Name: {{ get_variable('player.name', 'Unknown') }}
Health: {{ get_variable('player.health', 0) }}
Gold: {{ get_variable('player.currency.gold', 0) }} {# Accessing a nested variable #}
```

This simplifies accessing deeply nested values without multiple dictionary lookups and error handling.

Combine `systems.py` functions with Jinja2 for powerful conditional narratives:

```
:: PathChoice
{% if check_health() < 50 %}
You are too weak to continue this way.
[[Go back->SafePath]]
{% else %}
You feel strong enough to face the challenge.
[[Proceed->DangerousPath]]
{% endif %}
```


## 7. Assets (assets/ and custom.css)

### Images and Audio

Place all your image, audio, and video files into the `assets/` directory within your game project. You can then reference them in your `.tgame` files (or any embedded HTML) using a path relative to the `assets/` directory, prefixed with `/game/assets/`.

Example: If you have `MyGame/assets/background.png`, you'd reference it as:

```html
<img src="/game/assets/background.png" alt="Background">
```

For audio:

```html
<audio controls src="/game/assets/music.mp3"></audio>
```

### Custom CSS

The `custom.css` file in your game project allows you to override or add new CSS rules to style your game's web interface. This is useful for changing fonts, colors, layout, and more.

```css
/* MyGame/custom.css */
body {
    font-family: 'Georgia', serif;
    background-color: #1a1a1a;
    color: #f0f0f0;
}

.passage {
    max-width: 800px;
    margin: 20px auto;
    padding: 20px;
    background-color: #333;
    border-radius: 8px;
}

a {
    color: #4CAF50;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}
```

## 8. Saving and Loading

PyVN provides built-in save and load functionality.

*   **How it works:** The engine automatically saves the entire game state dictionary to a JSON file in the `saves/` directory of your project.
*   **Triggering Saves/Loads:** You can trigger save and load operations from your game's web interface. The default `NavMenu` often includes "Save" and "Load" links. These typically send AJAX requests to the `/save` and `/load` endpoints.

Example of a save link in a `.tgame` file (often in `NavMenu`):

```html
<a href="#" onclick="fetch('/save', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({slot: 1})}).then(response => response.json()).then(data => alert(data.message)); return false;">Save Game</a>
```

You can customize the save slot by changing the `slot` value in the JSON body.

## 9. Debugging Your Game

PyVN provides debug routes to inspect your game's state and passages, which are invaluable during development. These are only active when `debug_mode` is enabled (which it is by default when running via the launcher).

*   **`/debug/state`**: Access `http://127.0.0.1:5000/debug/state` in your browser to view the current game state as a JSON object. This is extremely useful for checking variable values, player attributes, and inventory.
*   **`/debug/passages`**: Access `http://127.0.0.1:5000/debug/passages` to get a list of all passages found in your `.tgame` files.
*   **`/debug/passage/<name>`**: Access `http://127.0.0.1:5000/debug/passage/Start` (replace `Start` with any passage name) to view the raw data of a specific passage.

**Troubleshooting Tips:**

*   **Check the terminal:** Any `print()` statements in your `systems.py` or errors in your Flask app will appear in the terminal where the engine is running.
*   **Syntax Errors:** Jinja2 syntax errors or Python errors in `systems.py` will often lead to server errors. Check the terminal output.
*   **Pathing Issues:** Ensure all asset paths (`/game/assets/your_image.png`) are correct.

## 10. Building Your Game for Distribution

Once your game is complete and tested, you can build it into a standalone executable that can be distributed to players.

1.  **Run the PyVN Engine:** Launch the `pyvn-engine` executable.
2.  **Select "Build Standalone Game":** Choose option `3` from the main menu.
3.  **Select Your Project:** Choose the game project you want to build from the list.
4.  **Build Process:** The engine will invoke PyInstaller to package your game. This process can take several minutes, depending on your game's size and your system's performance. Progress will be shown in the terminal.
5.  **Locate the Executable:** Once the build is complete, a new directory named `dist/` will be created in the same location where you ran the `pyvn-engine` executable. Inside `dist/`, you will find your game's executable (e.g., `MyGame_game.exe` on Windows, or `MyGame_game` on Linux).

This executable is self-contained and includes the PyVN engine, your game's content, and all necessary dependencies. Players can simply run this executable to play your game without needing to install Python or any other software.

## 11. Advanced Topics

### External Python Libraries

If your `systems.py` requires external Python libraries not included by default (e.g., `numpy`, `requests`), you will need to ensure these are available during the build process.

*   **Add to `requirements.txt`:** Add the library to the `requirements.txt` file in the PyVN engine's source directory.
*   **Rebuild the PyVN Engine:** You will then need to rebuild the `pyvn-engine` executable itself using `python3 build_engine_single.py` to include these new dependencies.
*   **Rebuild Your Game:** After rebuilding the engine, rebuild your game executable using the new engine.

### Custom Flask Routes

For highly advanced use cases, you might want to add custom Flask routes to your game. This is generally not recommended for typical game logic but can be useful for integrating with external services or complex web-based features.

*   **Modify `app.py`:** You would need to directly modify the `app.py` file in the PyVN engine's source code to add new `@app.route` definitions.
*   **Rebuild the PyVN Engine:** After modifying `app.py`, you would need to rebuild the `pyvn-engine` executable.

**Note:** Modifying core engine files like `app.py` requires rebuilding the engine executable and is intended for advanced users.


