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
├── game_theme.css           # An empty CSS file for custom styling
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

**Next**: Now that you have a basic game running, let's get familiar with the tool you'll be using to build it. Continue to [Using the IDE](2.-Using-the-IDE).