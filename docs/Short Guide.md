# A Streamlined Guide to Scribe Engine

Welcome to Scribe Engine, a modern engine for creating text-based games that blends simple interactive fiction with the power of Python and web technologies. This guide will walk you through the essential tools and concepts to get you started, from creating your first project to building complex, dynamic game systems.

## 1. Getting Started

First, let's get the engine running and create a new project.

### Installation and Project Creation

The easiest way to begin is by downloading the pre-built Scribe Engine executable, which requires no installation.

When you launch the application, follow these steps:

1. **Click "Create New Project"**.
    
2. Fill in your game's details, such as the **Project Name** and **Author**.
    
3. Select any initial features, like the **"Use Default Player Object,"** which gives you a ready-to-use player with health, energy, and inventory attributes.
    
4. **Click "Create Project"** to generate the necessary files.
    

### The Development Environment (IDE)

Once your project is created, the IDE will open. It has four key areas:

- **Header Bar**: Contains top-level actions like opening your game in a browser or building the final executable.
    
- **Sidebar**: Lets you navigate your project's files (`.tgame`, `.py`, `.css`) and access project settings.
    
- **Editor Panel**: Where you'll write your story and code, with syntax highlighting to help you.
    
- **Preview Panel**: A live preview of your game that updates as you save your work. It also includes a debug terminal to inspect game variables in real-time.
    

## 2. Writing Your Story

Your game's content lives in `.tgame` files, which combine story text, code, and navigation.

### Passages and Tags

The fundamental building block of your story is the **passage**. Each passage is a unique section of your game, like a room, a scene, or a dialogue block. You define a passage with two colons `::` followed by a unique, case-sensitive passage name that contains no spaces.

You can also add **tags** to a passage for metadata or styling. Tags are added on the same line, prefixed with a `#`.

```
:: start #opening #tutorial
This is the first passage players will see. It has two tags.

:: forest_path #dark #outdoor
The forest path is dark and winding.
```

#### Special Tags

Scribe Engine recognizes two special tags with built-in functionality:

- **`#silent`**: A passage tagged with `#silent` will execute its content without rendering any output. The screen will not clear or update. This is perfect for creating "logic-only" passages that run calculations in the background. **Crucially, a silent passage must end with a link to another passage, which the engine will automatically navigate to once the logic is complete.**
    
    ```
    :: check_for_ambush #silent
    {$-
    # This code runs silently to determine the next event
    import random
    ambushed = random.random() < 0.5 # 50% chance of ambush
    -$}
    
    {# The engine will automatically follow one of these links #}
    {% if ambushed %}
        [[->forest_ambush]]
    {% else %}
        [[->forest_path_clear]]
    {% endif %}
    ```
    
- **`#menu`**: The primary function of the `#menu` tag is to mark passages that should not be tracked by the engine's `last_passage` variable. This is essential for UI screens like an inventory or map, as it ensures that a "back" button will return the player to the last _story_ passage, not the menu they just viewed.
    
    ```
    :: inventory_screen #menu
    <h1>Inventory</h1>
    <ul>
    {% for item in player.inventory %}
        <li>{{ item.name }}</li>
    {% endfor %}
    </ul>
    [[Back->{{ last_passage }}]]
    ```
    

### Special Passages for UI

In addition to tags, Scribe Engine reserves three specific passage names for powerful, built-in UI functionality:

- **`::NavMenu`**: Any links placed within this passage will be automatically added to your game's main navigation bar.
    
    ```
    ::NavMenu
    [[Inventory->inventory_screen]]
    [[Map->map_screen]]
    ```
    
- **`::PrePassage`**: The content of this passage will be rendered _above_ every single passage in your game. It's ideal for creating a persistent Heads-Up Display (HUD).
    
    ```
    ::PrePassage
    <div class="hud">
        <span>HP: {{ player.health }}</span> | <span>Location: {{ player.location }}</span>
    </div>
    <hr>
    ```
    
- **`::PostPassage`**: The content of this passage is rendered _below_ every passage, which is useful for footers or persistent action bars.
    
    ```
    ::PostPassage
    <hr>
    <div class="footer">
        Current time: {{ world.time_of_day }}
    </div>
    ```
    

### Links for Navigation and Actions

Players move between passages using **links**.

#### Link Formats

There are two primary formats:

1. **Standard Link**: `[[Link Text->target_passage]]` displays "Link Text" to the player and navigates to the `target_passage` when clicked.
    
2. **Self-Descriptive Link**: `[[cave_entrance]]` is a shortcut that uses the passage name itself as the link text.
    

#### Link Actions

You can execute a small piece of Python code when a player clicks a link. Attach an inline Python block after the target passage using a `||` separator.

```
:: treasure_chest
You see a shiny gold coin on the ground.

[[Pick up the coin->continue_exploring||{$ player.gold += 1 $}]]
[[Leave it be->continue_exploring]]
```

### Using HTML for Rich Content

Because Scribe Engine renders games with web technology, you can embed standard HTML tags directly into your passages to format text, create layouts, and display images.

```
:: rich_content_example
<h1>Chapter 1: The Journey Begins</h1>
<p>Welcome, <b>{{player_name}}</b>!</p>
<img src="assets/village.png" alt="The village square" width="400">
```

## 3. Adding Dynamic Logic

Scribe Engine's real power comes from its layered system of Python for logic and Jinja2 for rendering.

### The Execution Order: Python First, Then Jinja2

It's critical to understand that Scribe Engine processes passages in two stages:

1. **Python Execution**: The engine first executes _all_ Python code blocks (`{$ ... $}` and `{$- ... -$}`) in the passage.
    
2. **Jinja2 Rendering**: After all Python code has finished, the engine uses the Jinja2 templating language to display content, handle conditions (`{%...%}`), and print variables (`{{...}}`).
    

### Executing Python Code

- **Inline Python: `{$ ... $}`** is for single statements.
    
- **Block Python: `{$- ... -$}`** is for multi-line scripts.
    

### Rendering with Jinja2

- **Displaying Variables: `{{ ... }}`** is the syntax to print the value of a variable.
    
- **Conditional Content: `{% if ... %}`** allows you to show or hide content based on the final state of your variables.
    

```
You dealt {{damage_dealt}} damage!

{% if player.health < 25 %}
    <p><b>You are badly wounded!</b></p>
{% endif %}
```

## 4. Building Complex Systems

As your game grows, move reusable logic into dedicated Python files.

### In-Passage Python vs. Custom `.py` Files

- **In-Passage Python** is great for quick, passage-specific logic and prototyping.
    
- **Custom `.py` Files** are better for complex, reusable systems like combat or inventory.
    

Scribe Engine **automatically discovers and loads all `.py` files** in your project folder. Their functions and classes are globally available in any passage.

### Creating Custom Classes for State Management

You can create your own Python classes (e.g., in a `player.py` file) to manage state in an organized way.

**Example `player.py` file:**

```
# player.py
class Player:
    def __init__(self, name=""):
        self.name = name
        self.level = 1
        self.health = 100
```

### Making Custom Objects Savable

The engine's save/load system works seamlessly with custom classes whose `__init__()` constructor can be called with **no required arguments** (i.e., it has default values for all parameters).

✅ **Correct Design (works with save/load):**

```
class GoodPlayer:
    def __init__(self, name="Adventurer", level=1):
        self.name = name
        self.level = level
```

## 5. Customizing the Look and Feel

You can change your game's visual appearance using CSS. The easiest method is to override the engine's default CSS variables in a `custom.css` file.

**Example `custom.css` for a Cyberpunk Theme:**

```
/* custom.css */
:root {
    --primary-color: #00ffff;        /* Cyan */
    --background-color: #0a0a0a;     /* Very dark background */
    --content-bg: #1a1a1a;          /* Dark content background */
    --text-color: #00ff00;          /* Bright green text */
}
```

## 6. Building and Distributing Your Game

Once you're ready to share your game, click the **"Build"** button in the IDE's header bar. Scribe Engine will compile your project into a standalone executable file (`.exe`) and package all necessary game data. You can then zip the entire distribution folder and share it with players.