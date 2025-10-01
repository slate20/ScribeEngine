# Welcome

Welcome to Scribe Engine, a powerful and modern text-based game engine that combines the simplicity of traditional interactive fiction with the flexibility of Python scripting and web technologies.

## What is Scribe Engine?

Scribe Engine is designed for developers who want to create rich, interactive text-based games without the complexity of traditional game engines. Whether you're building a simple branching story or a complex RPG with inventory systems, character stats, and dynamic storytelling, Scribe Engine provides the tools you need.

## Key Features

- **Modern IDE Integration**: Full-featured integrated development environment with syntax highlighting, live preview, and debugging.
    
- **Python-Powered Logic**: Embed Python code directly in your story passages for complex game mechanics.
    
- **Object-Oriented State Management**: Use custom Player classes and natural Python syntax for game state.
    
- **Live Preview**: See your changes instantly without rebuilding.
    
- **Flexible Theming**: Customize the look and feel with CSS or use built-in themes.
    
- **Desktop Distribution**: Build standalone executables for easy distribution.
    
- **Web-Based Runtime**: Games run in any modern web browser, using standard HTML and CSS.
    

## How to Use This Guide

This guide is organized to take you from your first project to advanced development techniques in a logical progression. We recommend reading the documents in order.

1. [**Getting Started**](https://www.google.com/search?q=01-Getting-Started.md "null") - Install the engine, create your first project, and run your first game.
    
2. [**Using the IDE**](https://www.google.com/search?q=02-Using-the-IDE.md "null") - Master the integrated development environment for a fast and efficient workflow.
    
3. [**Game Structure and Syntax**](https://www.google.com/search?q=03-Game-Structure-and-Syntax.md "null") - Learn the `.tgame` file format, passage structure, links, and special syntax.
    
4. [**Python and Templates**](https://www.google.com/search?q=04-Python-and-Templates.md "null") - Embed Python logic and use the Jinja2 templating engine to create dynamic content.
    
5. [**State Management and Classes**](https://www.google.com/search?q=05-State-Management-and-Classes.md "null") - Manage game state effectively with custom Python classes and objects.
    
6. [**Theming and Styling**](https://www.google.com/search?q=06-Theming-and-Styling.md "null") - Customize the visual appearance of your games with CSS.
    
7. [**Advanced Features**](https://www.google.com/search?q=07-Advanced-Features.md "null") - Explore custom Python modules, complex systems, and game distribution.
    
8. [**CLI Development Workflow**](https://www.google.com/search?q=08-CLI-Development.md "null") - Learn an alternative workflow for using external editors like VS Code or NeoVim.
    

---

# 1. Getting Started
This guide will help you install Scribe Engine, create your first project, and understand the basic concepts needed to get a game running.

## Installation

#### Option 1: Prebuilt Executable (Recommended)
1. Download the latest Scribe Engine executable for your operating system from the [releases page].
2. Run the executable. No installation is required.
3. The integrated development environment (IDE) will launch automatically.

#### Option 2: From Source (Advanced Users)
If you prefer to run from source or contribute to development:

```
git clone [repository-url]
cd ScribeEngine
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 gui_launcher.py
```

## Creating Your First Project
1. From the startup screen, click "Create New Project".
2. Fill in your project name.
3. Click "Create Project".

### The Project Structure
Scribe Engine will generate a folder for your project with the following files:
```
MyGame/
├── project.json         # Project configuration and metadata
├── start.tgame          # Your main story file
├── systems.py           # An empty Python file for custom logic
├── custom.css           # An empty CSS file for custom styling
└── assets/              # A folder for images, sounds, etc.
```
### Writing Your First Passages
1. After creating your project, the IDE will open automatically.
2. Click on start.tgame in the file sidebar to open it.
3. Replace the default content with the following:
```
:: start
{$ player.name = "Adventurer" $}
<h1>Chapter 1: The Crystal Caves</h1>

<p>Welcome to the Crystal Caves, <b>{{player.name}}</b>!</p>
<p>You have <i>{{player.health}} health</i> and <i>{{player.energy}} energy</i>.</p>

Your adventure begins at the mouth of an ancient cave system. Strange blue crystals embedded in the walls pulse with a soft, magical light.

What do you choose to do?

[[Examine the crystals->examine_crystals]]
[[Enter the cave immediately->cave_entrance]]


:: examine_crystals
{$ player.energy -= 5 $}
You study the crystals closely. They seem to respond to your touch, glowing brighter as you approach. You feel a slight warmth emanating from them.

<p><i>Your energy is now {{player.energy}}.</i></p>

[[Enter the cave with this new insight->cave_entrance]]


:: cave_entrance
The cave is dark, but the crystals you examined now seem to glow a little brighter, lighting your way forward. The air is cool and smells of damp earth.

[[Continue deeper->deeper_cave]]


:: deeper_cave
The adventure continues...

[[Start over->start]]
```
4. Click the (now blue) ‘Save File’ button to save the file. The **Preview Panel** on the right will instantly update. You can now click the links and play through your first scene!

### Key Concepts You Just Used
This simple example demonstrates the core features of Scribe Engine:

1. **Passages**: Sections of your story, defined with `:: passage_name`.
2. **HTML**: Standard HTML tags like `<h1>` and `<b>` for formatting your text.
3. **Python Code**: In-passage logic using `{$ ... $}` to change variables like `player.energy`.
4. **Jinja2 Templates**: `{{ ... }}` syntax to display the current value of variables.
5. **Links**: `[[ ... -> ... ]]` syntax to allow players to navigate between passages.
6. **State Persistence**: The `player.energy` variable kept its new value when you moved to the next passage.

**Next**: Now that you have a basic game running, let's get familiar with the tool you'll be using to build it.

---
# 2. Using the IDE
This guide covers all aspects of the Scribe Engine Integrated Development Environment (IDE), your primary tool for creating, testing, and distributing games.

## IDE Overview

The IDE is designed to provide everything you need in one window. It has four main components:


1. **Header Bar** - High-level project actions like building and closing.
    
2. **Sidebar** - File management and project settings.
    
3. **Editor Panel** - Where you write your story and code.
    
4. **Preview Panel** - A live, playable version of your game.
    

## Header Bar

The header bar provides quick access to essential functions.

- **Project Info**: Displays the name and file path of your current project.
    
- **Theme Toggle**: Switches the IDE between light and dark modes.
    
- **Open in Browser**: Opens your game in your default web browser for testing outside the IDE.
    
- **Preview Toggle**: Shows or hides the Preview Panel to maximize editor space.
    
- **Build Game**: Packages your game into a standalone executable for distribution. This creates a `builds` folder in your project directory containing a distribution-ready folder.
    
- **Project Actions**: A dropdown menu to **Reset Game State** (clearing all progress) or **Close Project**.
    

## Sidebar

The sidebar has two tabs for managing your project.


### Files Tab

This tab organizes all your project's files. Use the **+** button in each section to create new files and the **X** button to delete them.

- **Story Files (.tgame)**: Your primary game files containing passages, logic, and text.
    
- **Game Logic (.py)**: Optional Python files for creating complex, reusable systems (e.g., a combat engine or a custom player class).
    
- **Styling (.css)**: CSS files to customize your game's appearance.
    
- **Assets**: Your game's media, such as images, music, and sound effects.
    
    - ***NOTE*** Assets will need to be added to this directory on your device. When you open a project, any files found will show in this section and can be clicked on to copy the path for use in passages.
        

### Settings Tab

This tab allows you to configure your project's metadata and features. Key settings include:

- **Game Title / Author**: The metadata for your game.
    
- **Starting Passage**: The passage where the game begins.
    
- **Features**: Toggles for engine features like the default player object.
    
- **Development**: Toggles for debug mode.
    

## Editor Panel

This is where you'll do most of your writing and coding.


### Syntax Highlighting

The editor automatically color-codes your `.tgame` files to make them easy to read:

- **Passage Definitions**: `:: passage_name`
    
- **Python Code**: `{$ ... $}` and `{$- ... -$}`
    
- **Template Variables**: `{{ variable }}`
    
- **Template Logic**: `{% if ... %}`
    
- **Links**: `[[ text->target ]]`
    
- **Comments**: `{# comment #}`
    
- **HTML** will also have syntax highlighting
    

### Keyboard Shortcuts

- **Ctrl+S**: Save current file.
    
- **Ctrl+F**: Find text.
    
- **Ctrl+H**: Find and replace.
    
- **Tab / Shift+Tab**: Indent or unindent lines.
    

## Preview Panel

The preview panel provides a live, real-time version of your game.


### Live Preview

- **Instant Updates**: The preview automatically refreshes every time you save a file.
    
- **Full Interactivity**: You can click links and play your game exactly as a player would.
    
- **Error Display**: If you make a syntax error, the error message will be displayed in the preview if debug_mode is enabled.
    

### Debug Terminal

At the bottom of the preview is the debug terminal, one of the most powerful features of the IDE. It shows you the current value of **every variable** in your game in real-time.

- **State Visualization**: Watch variables change as you click links and progress through your story.
    
- **Object Inspection**: Expand objects (like the `player` object) to see all their properties.
    
- **Troubleshooting**: Instantly see if a variable isn't being set correctly or if a calculation is wrong.
    

## Building and Distributing Your Game

Once your game is ready to share, the IDE makes it simple to package it for distribution.

### The Build Process

1. Click the **"Build"** button in the IDE's header bar.
    
2. A progress window will appear, showing the status of the build. This process typically takes 10-20 seconds.
    
3. Once complete, a link to the output folder will be shown.
    

### Distribution Contents

The build process creates a distribution folder inside your project directory (in a new folder named `builds`). This folder contains:

- **YourGameTitle.exe** (or an equivalent for your OS): The standalone executable file for your game.
    
- **game.dat**: A file containing all your project's compressed and packaged assets (`.tgame` files, Python code, images, etc.).
    

### Sharing Your Game

To share your game with others:

1. Zip the **entire distribution folder**.
    
2. Share the resulting `.zip` file.
    

Players can then unzip the folder on their own computer and run the executable to play your game. No installation is required.

**Next:** You're now familiar with the tools. Let's dive deep into the syntax for creating your story.

---
# 3. Game Structure and Syntax
This guide covers the `.tgame` file format, passage structure, and all the syntax elements you'll use to build your game in Scribe Engine.

## The `.tgame` File Format

Scribe Engine uses plain text `.tgame` files to create your game. These files are a blend of five key components:

- **Passages**: Discrete sections of your game.
    
- **HTML**: For rich text formatting, layout, and media.
    
- **Links**: For navigation between passages.
    
- **Python code**: For game logic and state changes.
    
- **Jinja2 templates**: For displaying dynamic content.
    

## Passages: The Building Blocks of Your Story

### Defining Passages

A passage is a single screen or moment in your game. You define one using two colons `::` followed by a unique name.

```
:: start
This is the content of the starting passage.

:: forest_path
This is the content of another passage.

```

**Rules for passage names:**

- Must be unique across your entire project.
    
- Can contain letters, numbers, and underscores.
    
- **Should NOT contain spaces.** (technically can still work, but could potentially cause issues later)
    
- Are case-sensitive (`forest_path` is different from `Forest_Path`).
    

## Link Syntax: Navigation and Actions

Links are the primary way players interact with your game.

### Basic Links

The standard format is `[[Link Text->target_passage]]`.

```
The path splits in two. A sign points in each direction.
[[Go to the village->village_gate]]
[[Head into the forest->forest_path]]

```

If the link text is the same as the target passage name, you can use a shortcut: `[[cave_entrance]]`.

### Link Actions

You can execute a short piece of Python code when a link is clicked by adding `||` followed by an inline Python block. This is perfect for simple state changes that don't require a lot of logic.

```
:: treasure_chest
You see a wooden chest. A shiny gold coin rests on top.
<img src="assets/images/chest.png" alt="A treasure chest" width="200">

[[Pick up the coin->continue_exploring||{$ player.gold += 1 $}]]
[[Leave it be->continue_exploring]]

```

In this example, the player's gold will increase by 1 _only_ if they click the "Pick up the coin" link.

### Action Buttons

New in Scribe Engine: Action buttons use `<<...>>` syntax and work in two ways:
- **Without target**: Execute code and reload current passage
- **With target**: Execute code then navigate to target passage

```
:: village_shop
<h2>Village Shop</h2>
<p>Your Gold: {{ player.gold }}</p>

{% for item in shop_items %}
    <div>
        <strong>{{ item.name }}</strong> - {{ item.price }} gold
        <!-- Stay on current passage -->
        <<Quick Buy||{$
            if player.gold >= item.price:
                player.gold -= item.price
                player.inventory.append(item.name)
                shop_items.remove(item)
                message = f"Bought {item.name}!"
            else:
                message = "Not enough gold!"
        $}>>

        <!-- Navigate to different passage -->
        <<Examine->item_details||{$ selected_item = item $}>>
    </div>
{% endfor %}

{% if message %}
    <p><em>{{ message }}</em></p>
{% endif %}

:: item_details
{$-
# Process the selected item and show details
item_info = f"You're examining {selected_item.name}: {selected_item.description}"
delete_var('selected_item')
-$}

<h3>Item Details</h3>
<p>{{ item_info }}</p>
[[Back to shop->village_shop||{$ delete_var('item_info') $}]]
```

**Key differences:**
- `[[Navigation Links]]` - Go to different passages
- `[[Action Links||code]]` - Execute code then navigate
- `<<Action Buttons||code>>` - Execute code then reload current passage
- `<<Action Buttons->target||code>>` - Execute code then navigate to target

## Getting Player Input

To make your game more interactive, you can ask the player for input, such as their name or a password.

### The `input_field()` Function

You can render a text box and a submit button using the `input_field()` function directly within your passage content.

```
What is your name, adventurer?

{{ input_field('player_name') }}
```

When the player types into this box and clicks "Submit", the value they entered will be stored in the `player_name` variable.

### Customizing the Input Field

The function has several optional parameters to customize its behavior:

`{{ input_field(variable_name, input_type='text', placeholder='', button_text='Submit', next_passage=None) }}`

- **`variable_name`** (Required): The name of the variable where the player's input will be stored (e.g., `'player.name'`).
    
- **`input_type`**: The type of input field. Defaults to `'text'`, but you can use other HTML input types like `'password'` or `'number'`.
    
- **`placeholder`**: Faint text that appears in the input box before the user types anything.
    
- **`button_text`**: The text displayed on the submit button. Defaults to "Submit".
    
- **`next_passage`**: If provided, the game will automatically navigate to this passage after the player clicks the submit button.
    

### Example: Character Creation

Here's how you could use a customized input field to start your game.

```
:: character_creation
<h2>Character Creation</h2>
<p>Please enter your name to begin your journey.</p>

{{ input_field('player.name', placeholder='e.g., Elara', button_text='Begin Adventure', next_passage='start_adventure') }}

:: start_adventure
{$
# The player.name variable now holds the value the user entered
$}
<h1>Welcome, {{ player.name }}!</h1>
<p>Your story is about to begin...</p>

[[Continue->town_square]]
```


## Special Passage Tags

You can add tags to a passage on the same line as its definition using a `#`. Tags can be used for your own organization or for special engine functionality.

```
:: inventory_screen #ui #menu

```

Scribe Engine recognizes two special tags with built-in functionality:

### The `#silent` Tag

A passage tagged `#silent` will execute its Python code without rendering any output to the screen. This is perfect for "logic-only" passages that perform calculations or determine the next event behind the scenes.

**Important**: A `#silent` passage **must** contain a link that directs the engine to the next visible passage. This can be conditional as well:

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

### The `#menu` Tag

The `#menu` tag marks a passage as a UI screen (like an inventory or map) and tells the engine **not** to update its internal `last_passage` variable. This is essential for making "Back" buttons work correctly. It ensures the player returns to the last _story_ passage, not the menu they just viewed.

```
:: inventory_screen #menu
<h1>Inventory</h1>
<ul>
{% for item in player.inventory %}
    <li>{{ item.name }}</li>
{% endfor %}
</ul>

{# This link correctly returns the player to where they were #}
[[Back->{{ last_passage }}]]

```

## Special UI Passages

Scribe Engine reserves three specific passage names for built-in UI functionality.

- `::NavMenu`: Any links placed in this passage are automatically added to your game's main navigation bar. This is perfect for links to inventory, maps, or quest logs.
    
- `::PrePassage`: The content of this passage is rendered _above_ every single passage in your game. It's the ideal place to create a persistent Heads-Up Display (HUD).
    
- `::PostPassage`: The content of this passage is rendered _below_ every passage, useful for footers or persistent action bars.
    

```
::NavMenu
[[Inventory->inventory_screen]]
[[Map->map_screen]]

::PrePassage
<div class="hud">
    <span>HP: <b>{{ player.health }}</b></span> | <span>Location: <i>{{ player.location }}</i></span>
</div>
<hr>

::PostPassage
<hr>
<div class="footer">
    <span>Gold: {{ player.gold }}</span>
</div>

```

**Next:** Now you know how to structure your game. Let's explore how to bring it to life with logic.

---

# 4. Python and Templates
Scribe Engine's real power comes from its two-stage processing system. For every passage, the engine first executes all Python code, then it renders the output using the Jinja2 templating language. Understanding this separation is key to creating dynamic games.

**Execution Order:**

1. **Python First**: All Python blocks (`{$...$}` and `{$-...-$}`) are executed to calculate game logic and set variable states.
    
2. **Jinja2 Second**: The passage text and Jinja2 blocks (`{{...}}` and `{%...%}`) are rendered to display the final content to the player.
    

## Executing Python Code

You can embed Python code directly into your passages to handle game logic, manage variables, and create dynamic events.

### Inline Python: `{$ ... $}`

Use this for single statements and simple assignments. It's clean and easy to read.

```
:: forest_encounter
You defeat the goblin!
{$ player.experience += 10 $}
{$ player.gold += 5 $}
{$ goblins_defeated += 1 $}
```

### Multi-line Python: `{$- ... -$}`

Use this for more complex logic, such as calculations, function definitions, or importing modules.

```
:: combat_turn
{$-
import random

damage = player.get_attack_power()
modifier = random.uniform(0.8, 1.2) # Add some randomness
final_damage = int(damage * modifier)
enemy.health -= final_damage
-$}
```

### Global Scope

Variables created or modified in one passage persist and are available in all subsequent passages. You can initialize your main game variables in your `:: start` passage.

```
:: start
{$-
# Initialize all game variables here
if 'initialized' not in globals():
    player.health = 100
    player.gold = 50
    player.inventory = ["Rusty Sword", "Bread"]
    player.location = "Village Square"
    
    goblins_defeated = 0
    
    initialized = True
-$}
```

### Variable Management with delete_var()

Scribe Engine provides a `delete_var()` function to clean up temporary variables and keep your game state organized. This is especially useful when working with action buttons that create temporary variables for data passing.

```
:: inventory_manager
{$-
# Process item selection
temp_item = selected_items[0]  # Get first selected item
temp_value = calculate_item_value(temp_item)

# Apply the action
player.gold += temp_value
player.inventory.remove(temp_item.name)

# Clean up temporary variables to avoid clutter
delete_var('temp_item')
delete_var('temp_value')
delete_var('selected_items')
-$}

You sold the item for {{ temp_value }} gold.
```

**When to use delete_var():**
- After processing temporary calculation variables
- When passing data between action buttons and their target passages
- To prevent debug information from showing internal variables
- To keep your game state clean for save/load operations

## Rendering with Jinja2

After all Python code has been executed, the engine uses Jinja2 to display content.

### Displaying Variables: `{{ ... }}`

This is the most common Jinja2 syntax. It prints the final value of a variable.

```
<div class="status-bar">
    <span>Health: {{ player.health }}</span>
    <span>Gold: {{ player.gold }}</span>
</div>
```

### Conditional Content: `{% if ... %}`

You can show or hide entire blocks of text, links, or HTML based on the state of your variables.

```
{% if player.health < 25 %}
    <p class="warning"><b>You are badly wounded!</b></p>
{% endif %}

{% if "Magic Key" in player.inventory %}
    [[Use the Magic Key to unlock the ancient door->ancient_treasure_room]]
{% else %}
    <p>The ancient door is sealed by a powerful magic you cannot break.</p>
{% endif %}
```

You can also use `{% elif ... %}` and `{% else %}` for more complex conditions.

### Loops: `{% for ... %}`

Loops are perfect for displaying lists, like the items in a player's inventory or the goods in a shop.

```
:: shop_inventory
<h2>Merchant's Wares</h2>
<ul>
{% for item in shop_items %}
    <li>{{ item.name }} - {{ item.price }} gold</li>
{% endfor %}
</ul>
```

## When to Use Python vs. Custom `.py` Files

- **In-Passage Python** is excellent for passage-specific logic, prototyping ideas quickly, and simple state changes.
    
- **Custom `.py` Files** are better for complex, reusable systems that you want to use across many passages, such as a combat calculator, an inventory manager, or a quest system.
    

Scribe Engine **automatically discovers and loads all `.py` files** in your project folder. Any functions or classes you define in them are globally available in any passage without needing to be imported.

**Next:** You can now create dynamic logic. Let's learn how to organize your game's data cleanly. 

# 5. State Management and Classes
As your game grows, managing state with individual variables can become messy. Scribe Engine is built to handle object-oriented Python, allowing you to organize your game's data into clean, reusable classes.

## The Default Player Object

When you start a project Scribe Engine provides a ready-to-use `player` object. You can add any properties you want to it on the fly.

```
:: start
{$
# Add custom attributes to the default player object
player.name = "Elara"
player.level = 1
player.location = "Tavern"
player.skills = {"magic": 5, "stealth": 3}
$}

Welcome, {{ player.name }}! You are level {{ player.level }}.
```

This is great for smaller projects, but for larger games, creating your own custom classes is more powerful. You can disable the default player object by disabling 'Use Default Player Object' in your project settings.

## Creating Custom Classes

For better organization, you can define your own classes in separate `.py` files in your project directory. Scribe Engine automatically loads these files, making your classes available everywhere.

### Simple Example: A Custom Player Class

1. In the IDE sidebar, click the **+** button next to **Game Logic (.py)** and create a file named `player_class.py`.
    
2. Add the following code to `player_class.py`:
    

```python
# player_class.py

class Player:
    def __init__(self, name="Adventurer"):
        self.name = name
        self.level = 1
        self.health = 100
        self.max_health = 100
        self.inventory = []

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health
```

### Using Your Custom Class

Scribe Engine looks for a class named `Player` and, if it finds one, automatically creates an instance of it for you, also named `player`.

```
:: start
{# The 'player' variable is now an instance of our custom Player class #}
{$ player.name = "Sir Gideon" $}
<h2>Welcome, {{ player.name }}</h2>

:: goblin_attack
You are attacked by a goblin!
{$ player.take_damage(15) $}
<p>You took 15 damage! Your health is now {{ player.health }}.</p>
```

### The Save System Requirement (Very Important!)

For Scribe Engine's save/load system to work correctly with your custom classes, it must be able to create an object from scratch. This means your class's `__init__()` constructor **must be callable with no required arguments**.

✅ Correct (Works with Save/Load):

All parameters have default values.

```python
class GoodPlayer:
    def __init__(self, name="Adventurer", level=1):
        self.name = name
        self.level = level
```

❌ Incorrect (Will Break Save/Load):

The name parameter is required and has no default value.

```python
class BadPlayer:
    def __init__(self, name):
        self.name = name
        self.level = 1
```

## Building More Complex Systems

You can create classes for anything in your game, such as items, enemies, quests, or locations.

### Example: An Item System

Create a new file `items.py`:

```Python
# items.py 

class Item: 
	# This class follows the rule: all params have defaults.
	def __init__(self, name="Unknown Item", description=""):
		self.name = name
		self.description = description
		
class Weapon(Item):
	# This class also follows the rule.
	def __init__(self, name="Default Weapon", description="", damage=5):
		super().__init__(name, description)
		self.damage = damage 
		
class Potion(Item): 
	# This class also follows the rule.
	def __init__(self, name="Default Potion", description="", heal_amount=20):
		super().__init__(name, description)
		self.heal_amount = heal_amount
```

### Using the Item System in a Passage

```
:: found_treasure
{$- 
# Create instances of our item classes 
broadsword = Weapon(name="Broadsword", description="A sturdy steel sword.", damage=15)
health_potion = Potion(name="Health Potion", description="Restores a small amount of health.")

# Add the new objects to the player's inventory
player.inventory.append(broadsword) player.inventory.append(health_potion)
-$} 

You open the chest and find a **{{ broadsword.name }}** and a **{{ health_potion.name }}**! 

<h2>Inventory</h2> 
<ul> 
{% for item in player.inventory %}
	<li><b>{{ item.name }}</b>: <i>{{ item.description }}</i>
	{% if item.damage is defined %}
		(Damage: {{ item.damage }})
	{% endif %}
	</li>
{% endfor %}
</ul>
```

This object-oriented approach keeps your story files clean and your game logic organized and reusable.

**Next:** With your game logic and state organized, it's time to make it look good. 

---
# 6. Theming and Styling

This guide covers how to customize the visual appearance of your games using CSS.

## How Styling Works

Scribe Engine renders your game as a web page. This means you can use standard CSS to control every visual aspect, from colors and fonts to layout and animations.

There are two main ways to style your game:

1. **Override CSS Variables (Easy)**: The default theme is built with CSS variables for key properties like colors and fonts. Overriding these is the fastest way to create a new look.
    
2. **Write Custom CSS (Advanced)**: For full control, you can write your own CSS rules to target specific elements of the game's interface.
    

## Getting Started with `custom.css`

When you create a new project, Scribe Engine generates an empty `custom.css` file. Any styles you add to this file will be automatically loaded and applied to your game.

1. In the IDE sidebar, go to the **Files** tab.
    
2. Under the **Styling (.css)** section, click on `custom.css` to open it.
    

## Method 1: Overriding CSS Variables (Recommended)

This is the easiest way to create a new theme. Add a `:root` block to your `custom.css` file and redefine the variables you want to change.

### Example: A Dark "Cyberpunk" Theme

```css
/* custom.css */
:root {
    /* Main Colors */
    --primary-color: #00ffff;        /* Bright Cyan */
    --background-color: #0a0a0a;     /* Near Black */
    --content-bg: #1a1a1a;          /* Dark Gray */
    --text-color: #e0e0e0;          /* Light Gray Text */
    --link-color: #ff00ff;          /* Magenta */

    /* Typography */
    --font-family-body: 'Courier New', monospace;
    --font-family-heading: 'Verdana', sans-serif;
}
```

### Key CSS Variables to Override

|   |   |
|---|---|
|**Variable**|**Default Usage**|
|`--primary-color`|Main accent color, button hovers.|
|`--background-color`|The background of the entire game page.|
|`--content-bg`|The background of the main story content area.|
|`--text-color`|The main color for paragraphs and body text.|
|`--link-color`|The color of passage links.|
|`--border-color`|Color for borders and horizontal lines (`<hr>`).|
|`--font-family-body`|The font for the main story text.|
|`--font-family-heading`|The font for headings (`<h1>`, `<h2>`, etc.).|

## Method 2: Advanced Custom CSS

You can target specific elements of the game's UI for more detailed styling. The Live Preview in the IDE is a great way to inspect elements and test styles.

### Example: Styling Links as Buttons

By default, links are simple text. You can make them look like clickable buttons with a few CSS rules.

```css
/* custom.css */

/* Target all passage links, which have the class .passage-link */
.passage-link {
    display: block;
    padding: 12px;
    margin: 8px 0;
    border: 1px solid var(--border-color);
    background-color: var(--content-bg);
    color: var(--link-color);
    text-align: center;
    text-decoration: none;
    border-radius: 5px;
    transition: background-color 0.2s, color 0.2s;
}

/* Add a hover effect */
.passage-link:hover {
    background-color: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
}
```

### Using Custom Fonts

You can import web fonts (like Google Fonts) at the top of your `custom.css` file and then use them in your theme.

```css
/* custom.css */
@import url('[https://fonts.googleapis.com/css2?family=MedievalSharp&display=swap](https://fonts.googleapis.com/css2?family=MedievalSharp&display=swap)');

:root {
    --font-family-heading: 'MedievalSharp', cursive;
}

h1, h2, h3 {
    font-family: var(--font-family-heading);
}
```

## Save/Load Modal Styling

The save and load screens are also fully stylable. They use the same CSS variables as the main game, but also have their own specific variables you can override for more granular control.

### Key Modal CSS Variables

|   |   |
|---|---|
|**Variable**|**Usage**|
|`--save-slot-bg`|Background of an individual save slot.|
|`--save-slot-border`|Border of a save slot.|
|`--save-slot-hover`|Background of a slot when hovered.|
|`--save-slot-selected`|Accent color for the currently selected slot.|

**Next:** You've learned how to build and style your game. Let's look at more advanced features. 

---
# 7. Advanced Concepts

This guide covers advanced Scribe Engine concepts for building large, robust, and optimized games, including architectural patterns and complex Python modules.

## Modular Architecture

For complex games, organizing your code into a clear structure is essential. Instead of putting all your Python classes in one file, consider a modular approach using directories. Scribe Engine will automatically discover and load all `.py` files within your project folder, including those in subdirectories.

### Recommended Directory Structure

```
MyGame/
├── systems/                 # Folder for core game systems
│   ├── combat.py           # Combat mechanics
│   ├── quests.py           # Quest management system
│   └── items.py            # Item, weapon, and armor classes
├── data/                    # Folder for game data (e.g., JSON files)
│   ├── items.json          # Item definitions
│   └── npcs.json           # NPC data
├── utils/                   # Folder for utility functions
│   └── text_formatter.py   # Text processing helpers
└── start.tgame
```

This pattern keeps your code organized, reusable, and easier to manage, especially in a team environment.

## Event Management System

An event system (also known as a publish-subscribe pattern) is a powerful architecture for decoupling your game's systems. Instead of systems calling each other directly, they can emit an event (e.g., "player_leveled_up") and other systems can subscribe to that event to react accordingly.

### Example: A Simple Event Manager

Create a file `utils/events.py`:

```
# utils/events.py

class EventManager:
    def __init__(self):
        # A dictionary where keys are event names
        # and values are lists of functions (callbacks)
        self.listeners = {}

    def subscribe(self, event_type, callback):
        """Register a function to listen for an event."""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

    def emit(self, event_type, data=None):
        """Trigger an event and notify all listeners."""
        if event_type in self.listeners:
            # Call each subscribed function with the event data
            for callback in self.listeners[event_type]:
                callback(data)

# Create a single, global instance to be used everywhere
events = EventManager()
```

### Using the Event Manager

Now, different parts of your game can communicate without being directly linked.

**In `systems/player.py`:**

```
# systems/player.py
from utils.events import events # Import the global instance

class Player:
    # ... (other player methods) ...
    def level_up(self):
        self.level += 1
        # Instead of directly calling other systems, just emit an event.
        events.emit("player_leveled_up", {"new_level": self.level})
```

**In `systems/ui.py`:**

```
# systems/ui.py
from utils.events import events

class UIManager:
    def __init__(self):
        # Subscribe the show_level_up_animation method to the event.
        events.subscribe("player_leveled_up", self.show_level_up_animation)

    def show_level_up_animation(self, data):
        # This method now runs automatically whenever the player levels up.
        print(f"DISPLAYING ANIMATION: Player reached level {data['new_level']}!")

# Create an instance so it starts listening
ui_manager = UIManager()
```

This makes your code much cleaner. Your `Player` class doesn't need to know anything about the `UIManager`; it just announces that it leveled up.

## Custom Serialization for Complex Data

While Scribe Engine's save system handles most standard Python objects, you might occasionally need to save data types that it doesn't understand (like `datetime` objects). You can handle this by providing custom `to_dict()` and `from_dict()` methods.

```
# In your custom class file
from datetime import datetime

class Character:
    def __init__(self):
        self.name = "Hero"
        self.created_at = datetime.now() # This object is not natively savable

    def to_dict(self):
        """Return a savable dictionary representation of the object."""
        return {
            "name": self.name,
            # Convert the datetime object to a standard ISO format string
            "created_at": self.created_at.isoformat(),
            # Special key to help the engine know what class this is
            "__class_name__": "Character"
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Character instance from a loaded dictionary."""
        instance = cls()
        instance.name = data.get("name")
        # Convert the string back into a datetime object
        instance.created_at = datetime.fromisoformat(data.get("created_at"))
        return instance
```

The engine will automatically detect and use these methods during the save/load process.

**Next:** This concludes the main Scribe Engine guide. The next section, [**CLI Development Workflow**](8.-CLI-Development-Workflow), is for advanced users who wish to work outside the IDE.

---
# 8. CLI Development and Workflow

While the Scribe Engine IDE provides a powerful, all-in-one solution, some developers may prefer to use their own external code editors (like VS Code, Neovim, or Sublime Text) and command-line tools. The CLI (Command-Line Interface) workflow is designed for this purpose.

## When to Use the CLI Workflow

This workflow is ideal for developers who:

- Prefer their own configured code editor.
    
- Want to integrate Scribe Engine into a larger toolchain (e.g., using Git for version control).
    
- Are working in a team environment with specific development standards.
    
- Need to automate parts of the development or build process via scripts.
    

## The CLI Launcher

The core of this workflow is the CLI launcher (`main_engine.py` if running from source). It provides a menu-driven interface for managing your project from the terminal.

### Starting the CLI Launcher

```
# If running from source, navigate to the Scribe Engine directory
python3 main_engine.py
```

This will bring up the main menu with options for creating, opening, and managing projects.

## The Development Server

The most important feature for CLI development is the built-in web server. It runs your game and provides live reloading, so you can see your changes instantly in a web browser without needing the IDE's preview panel.

### Starting the Server

1. From the CLI launcher, open your project.
    
2. From the project menu, select **"Start Development Server"**.
    
3. The server will start, typically on `http://127.0.0.1:5000`.
    
4. Open this URL in your web browser to play and test your game.
    

Now, you can edit your project's files (`.tgame`, `.py`, `.css`) in your favorite editor. Every time you save a file, the development server will detect the change and automatically reload the game in your browser.

## External Editor Integration

You can enhance your experience by configuring your editor for Scribe Engine development.

### Visual Studio Code

We recommend telling VS Code to treat `.tgame` files as Markdown for good syntax highlighting. You can also add custom snippets.

1. Create a file at `.vscode/settings.json` in your project root:
```json
// .vscode/settings.json
{
    "files.associations": {
        "*.tgame": "markdown"
    },
    "editor.tabSize": 4,
    "editor.insertSpaces": true,
    "files.autoSave": "onFocusChange"
}
```

2. Create a file at `.vscode/tgame.json` to add custom snippets for common Scribe Engine syntax:
```json
// .vscode/snippets/tgame.json
{
    "Passage": {
        "prefix": "passage",
        "body": [
            ":: ${1:passage_name}",
            "${2:Content goes here...}",
            "",
            "[[${3:Link text}->${4:target_passage}]]"
        ],
        "description": "Create a new passage"
    },
    "Python Block": {
        "prefix": "pyblock",
        "body": [
            "{$-",
            "${1:# Python code here}",
            "-$}"
        ],
        "description": "Multi-line Python block"
    },
    "Inline Python": {
        "prefix": "py",
        "body": [
            "{$ ${1:python_code} $}"
        ],
        "description": "Inline Python code"
    }
}
```

#### Vim/Neovim
Custom syntax highlighting for .tgame files:

```lua
" ~/.vim/syntax/tgame.vim
if exists("b:current_syntax")
  finish
endif

" Passage definitions
syntax match tgamePassage "^:: .*$"
highlight link tgamePassage Title

" Python blocks
syntax region tgamePythonBlock start="{$-" end="-$}" contains=@pythonTop
syntax region tgamePythonInline start="{$" end="$}" contains=@pythonTop
highlight link tgamePythonBlock Special
highlight link tgamePythonInline Special

" Template variables
syntax region tgameVariable start="{{" end="}}"
highlight link tgameVariable Identifier

" Template logic
syntax region tgameLogic start="{%" end="%}"
highlight link tgameLogic Statement

" Links
syntax region tgameLink start="\[\[" end="\]\]"
highlight link tgameLink Underlined

" Comments
syntax region tgameComment start="{#" end="#}"
highlight link tgameComment Comment

let b:current_syntax = "tgame"
```

Add to your `.vimrc`:
```vim
autocmd BufRead,BufNewFile *.tgame set filetype=tgame
```

---
## Building from the CLI

You can also build your game for distribution without using the IDE's "Build" button.

1. From the CLI launcher, open your project.
    
2. Select **"Build Game"** from the project menu.
    
3. The build process will run in the terminal, and the final distribution folder will be created in your project's `builds` directory, just as it would when using the IDE.
    

This feature is particularly useful for automation and continuous integration (CI/CD) pipelines.

## Version Control (Git)

The CLI workflow is perfect for use with version control systems like Git. Since all project files are plain text, they are easy to track.

### Recommended `.gitignore`

Create a `.gitignore` file in your project's root directory to prevent temporary files from being committed to your repository.

```
# Scribe Engine specific
saves/
builds/
debug.log

# Python cache
__pycache__/
*.pyc

# OS-specific
.DS_Store
Thumbs.db
```
