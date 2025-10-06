# Scribe Engine V2 - Architecture Overview for IDE Creation

The entire v2 engine is built on a **Component-Based Architecture**. The guiding principle is **Composition over Inheritance**. Instead of creating objects that *are* things (e.g., a `Player` class that inherits from `PhysicsObject`), you create simple objects and *give them* behaviors by attaching components.

This is the hierarchy of how it all fits together:

### 1. The `Game` Object
*   **What it is:** The highest-level object. It's the master controller that initializes Pygame, manages the window, and runs the main game loop.
*   **For IDE Creation:** Your IDE will need to interact with this `Game` object.
    *   When a user clicks "Play," your IDE will launch a process running `main.py`, telling it which project and scene to run.
    *   For an *integrated* editor viewport (where you see the live game inside the IDE), your IDE would create a Pygame display surface and then instantiate the `Game` object in `editor_mode=True`. The `Game` class is already set up to use an existing display surface in this mode, so it can render directly into a window controlled by your IDE.

### 2. The `Scene` Object
*   **What it is:** A container for a single "screen" of the game (e.g., Main Menu, Level 1, Shop). It holds all the game objects and manages the main `update` and `render` calls for everything in that level.
*   **For IDE Creation:** A `Scene` is the primary "document" your IDE will manage.
    *   Your IDE's "Project" panel would list scene files (`level1.json`, `main_menu.json`, etc.).
    *   The main window of your IDE would be a **Scene Editor**. This is where a user would visually place, move, and select game objects.
    *   When a user saves a scene, your IDE's job is to serialize the state of everything in that scene—every object, its position, and all of its components—into a file (likely a JSON file).

### 3. The `Sprite` Object (The "Game Object")
*   **What it is:** The fundamental entity that exists in a scene. It's not just an image; it's a container. By itself, a `Sprite` only has a **transform** (position, rotation, scale) and a visual representation (`image`, `layer`). It has no inherent behavior.
*   **For IDE Creation:** This is the "thing" that users will manipulate in the Scene Editor.
    *   In your IDE's visual editor, users will drag and drop Sprites.
    *   When a user selects a Sprite, your IDE's **"Inspector"** panel should display its properties: Position, Rotation, Scale, Image, Layer, etc.
    *   Crucially, the Inspector must also list the Sprite's **Components**.

### 4. The `Component` Object (The "Behavior")
*   **What it is:** This is the heart of the entire design. A Component is a modular, reusable piece of logic that can be attached to a Sprite to give it behavior. We saw this with `RigidBody`, which gives a Sprite physics properties.
*   **For IDE Creation:** This is how your IDE will expose game logic to the user without them having to write code for everything.
    *   The "Inspector" panel for a selected Sprite must have an **"Add Component"** button.
    *   Clicking this button should show a list of all available `Component` classes your engine has (`RigidBody`, `Animator`, `PlayerScript`, etc.).
    *   When a user adds a `RigidBody` component, a new section should appear in the Inspector showing all of `RigidBody`'s public properties (`mass`, `gravity_scale`, `is_kinematic`). Your IDE would allow the user to edit these values directly.
    *   This allows a game designer to create a "Player" by:
        1.  Creating a blank `Sprite`.
        2.  Adding a `RigidBody` component and tweaking its mass.
        3.  Adding an `Animator` component and assigning animations.
        4.  Adding a `PlayerScript` component (which you would write) and setting its `speed` property.
