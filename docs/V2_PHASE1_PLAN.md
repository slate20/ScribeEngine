# Scribe Engine V2 - Phase 1 Implementation Plan

**Phase 1: Prototype/MVP - Core Engine Foundation**

This document provides a detailed implementation plan for Phase 1 of Scribe Engine V2 development.

## Overview

**Goal**: Build a working scene-based 2D game engine with basic platformer demo

**Timeline**: 4-6 weeks (depending on development pace)

**Success Criteria**:
- Scene system with lifecycle management
- Pygame-based rendering and game loop
- Sprite system with basic collision detection
- Input handling (keyboard/mouse)
- Simple built-in physics (gravity, velocity, AABB collision)
- Working platformer demo with player movement, platforms, and basic interactions
- Test runner for launching games

---

## Phase 1 File Structure

```
v2_engine/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── game.py              # Main Game class, initialization, game loop
│   ├── scene.py             # Scene base class and scene manager
│   ├── input.py             # Input handler (keyboard, mouse)
│   ├── camera.py            # Camera/viewport system
│   └── time.py              # Delta time, frame rate management
│
├── sprites/
│   ├── __init__.py
│   ├── sprite.py            # Base Sprite class
│   ├── group.py             # Sprite groups and layering
│   └── components.py        # Component base class for behaviors
│
├── physics/
│   ├── __init__.py
│   ├── collision.py         # AABB collision detection
│   ├── rigidbody.py         # Velocity, gravity, acceleration
│   └── tilemap.py           # Tilemap collision helpers
│
├── ui/
│   ├── __init__.py
│   ├── widget.py            # Base UI widget class
│   ├── text.py              # Text rendering
│   └── button.py            # Simple button widget
│
├── utils/
│   ├── __init__.py
│   ├── math.py              # Vector2, Rect helpers
│   ├── color.py             # Color utilities
│   └── assets.py            # Asset loading (images, sounds)
│
└── templates/
    └── platformer/          # Platformer demo template
        ├── 2d_project.json
        ├── scenes/
        │   ├── main_menu.py
        │   └── level_01.py
        └── assets/
            ├── sprites/
            └── placeholder_assets.txt

test_v2.py                   # Test runner script (project root)
```

---

## Week-by-Week Development Plan

### Week 1: Core Foundation
**Focus**: Game loop, Scene system, Input handling

**Tasks**:
1. Implement `Game` class with main game loop
2. Implement `Scene` base class and `SceneManager`
3. Implement `InputHandler` for keyboard/mouse
4. Implement `TimeManager` for delta time
5. Create basic test runner script
6. Test scene switching and basic rendering

**Deliverable**: Engine can load scenes, handle input, and run a game loop at 60 FPS

---

### Week 2: Sprite System
**Focus**: Sprite rendering, groups, basic transforms

**Tasks**:
1. Implement `Sprite` base class with transform, rendering
2. Implement `SpriteGroup` for batch rendering and updates
3. Implement `Camera` for viewport management
4. Add sprite layering and z-ordering
5. Test sprite rendering and camera movement

**Deliverable**: Engine can render multiple sprites with layering and camera control

---

### Week 3: Physics & Collision
**Focus**: AABB collision, velocity, gravity

**Tasks**:
1. Implement `RigidBody` component (velocity, acceleration, gravity)
2. Implement AABB collision detection
3. Implement collision response (solid, trigger, one-way platforms)
4. Add tilemap collision helpers
5. Test physics and collision with simple objects

**Deliverable**: Sprites can move with physics and collide with each other

---

### Week 4: Platformer Demo - Part 1
**Focus**: Player controller, level design

**Tasks**:
1. Create `Player` sprite with movement controller
2. Implement jump mechanics (with coyote time, jump buffering)
3. Create `Platform` sprite class
4. Design Level_01 scene with platforms
5. Test player movement and platforming feel

**Deliverable**: Playable character that can run, jump, and land on platforms

---

### Week 5: Platformer Demo - Part 2
**Focus**: UI, menus, polish

**Tasks**:
1. Implement basic UI text rendering
2. Create main menu scene with start button
3. Add collectibles and simple scoring
4. Implement scene transitions
5. Polish player movement and camera following

**Deliverable**: Complete platformer demo with menu, gameplay, and basic UI

---

### Week 6: Testing & Documentation
**Focus**: Bug fixes, code cleanup, documentation

**Tasks**:
1. Write API documentation for core classes
2. Create developer guide for making scenes
3. Fix bugs and optimize performance
4. Create example code snippets
5. Prepare for Phase 2 planning

**Deliverable**: Stable, documented Phase 1 engine ready for IDE integration

---

## Detailed Class Specifications

### 1. Game Class (`v2_engine/core/game.py`)

**Purpose**: Main engine controller, manages initialization, game loop, and scene management

```python
class Game:
    """
    Main game controller for Scribe Engine V2.

    Handles pygame initialization, game loop, scene management,
    and core engine services.
    """

    def __init__(self, project_path: str):
        """
        Initialize the game engine.

        Args:
            project_path: Path to the game project directory
        """
        self.project_path = project_path
        self.project_config = None  # Loaded from 2d_project.json
        self.screen = None
        self.clock = None
        self.running = False

        # Core systems
        self.scene_manager = None
        self.input_handler = None
        self.time_manager = None
        self.asset_manager = None

    def initialize(self) -> bool:
        """
        Initialize pygame and core engine systems.

        Returns:
            True if initialization successful, False otherwise
        """
        pass

    def load_project_config(self) -> dict:
        """
        Load and validate 2d_project.json configuration.

        Returns:
            Project configuration dictionary
        """
        pass

    def run(self):
        """
        Start the main game loop.

        Game loop handles:
        - Event processing
        - Fixed timestep updates
        - Variable framerate rendering
        - Scene management
        """
        pass

    def quit(self):
        """Clean shutdown of pygame and engine systems."""
        pass

    # Internal methods
    def _process_events(self):
        """Process pygame events and update input handler."""
        pass

    def _update(self, dt: float):
        """Update current scene with delta time."""
        pass

    def _render(self):
        """Render current scene to screen."""
        pass
```

**Key Features**:
- Fixed timestep updates (60 UPS) with variable framerate rendering
- Scene management delegation to SceneManager
- Centralized access to engine services
- Project configuration loading

---

### 2. Scene Classes (`v2_engine/core/scene.py`)

**Purpose**: Scene lifecycle management and scene switching

```python
class Scene:
    """
    Base class for all game scenes.

    Scenes represent distinct game states (menu, gameplay, etc.)
    and manage their own sprites, UI, and logic.
    """

    def __init__(self, game: 'Game'):
        """
        Initialize the scene.

        Args:
            game: Reference to the main Game instance
        """
        self.game = game
        self.sprite_groups = {}  # Named sprite groups
        self.ui_elements = []
        self.camera = None

    def on_enter(self):
        """Called when scene becomes active."""
        pass

    def on_exit(self):
        """Called when scene becomes inactive."""
        pass

    def handle_event(self, event):
        """
        Handle pygame events.

        Args:
            event: pygame event object
        """
        pass

    def update(self, dt: float):
        """
        Update scene logic.

        Args:
            dt: Delta time in seconds
        """
        pass

    def render(self, screen):
        """
        Render scene to screen.

        Args:
            screen: pygame Surface to render to
        """
        pass


class SceneManager:
    """
    Manages scene loading, switching, and lifecycle.
    """

    def __init__(self, game: 'Game'):
        self.game = game
        self.scenes = {}  # scene_name -> Scene instance
        self.current_scene = None
        self.next_scene = None

    def register_scene(self, name: str, scene: Scene):
        """
        Register a scene for later use.

        Args:
            name: Unique scene identifier
            scene: Scene instance
        """
        pass

    def load_scene(self, name: str):
        """
        Switch to a different scene.

        Args:
            name: Name of scene to load
        """
        pass

    def update(self, dt: float):
        """Update current scene."""
        pass

    def render(self, screen):
        """Render current scene."""
        pass

    def _perform_scene_transition(self):
        """Execute pending scene transition."""
        pass
```

**Key Features**:
- Clean lifecycle hooks (on_enter, on_exit)
- Scene switching with transition support
- Access to game services through self.game
- Sprite group management per scene

---

### 3. Input Handler (`v2_engine/core/input.py`)

**Purpose**: Unified input state management

```python
class InputHandler:
    """
    Centralized input state management.

    Provides convenient methods for checking key/button states
    without directly processing pygame events everywhere.
    """

    def __init__(self):
        # Keyboard state
        self._keys_down = set()      # Currently held keys
        self._keys_pressed = set()   # Keys pressed this frame
        self._keys_released = set()  # Keys released this frame

        # Mouse state
        self._mouse_pos = (0, 0)
        self._mouse_buttons_down = set()
        self._mouse_buttons_pressed = set()
        self._mouse_buttons_released = set()

    def update(self, events: list):
        """
        Process pygame events and update input state.

        Args:
            events: List of pygame events from this frame
        """
        pass

    def is_key_down(self, key) -> bool:
        """Check if key is currently held down."""
        pass

    def is_key_pressed(self, key) -> bool:
        """Check if key was pressed this frame (once)."""
        pass

    def is_key_released(self, key) -> bool:
        """Check if key was released this frame."""
        pass

    def get_mouse_pos(self) -> tuple:
        """Get current mouse position (x, y)."""
        pass

    def is_mouse_button_down(self, button: int) -> bool:
        """Check if mouse button is held down."""
        pass

    def is_mouse_button_pressed(self, button: int) -> bool:
        """Check if mouse button was clicked this frame."""
        pass

    def reset_frame_state(self):
        """Clear frame-specific input states (pressed/released)."""
        pass
```

**Key Features**:
- Distinction between "down" (held) and "pressed" (this frame only)
- Mouse position tracking
- Frame-based state clearing

---

### 4. Sprite System (`v2_engine/sprites/sprite.py`)

**Purpose**: Base sprite class with transform, rendering, components

```python
class Sprite:
    """
    Base class for all game objects with visual representation.

    Sprites have:
    - Transform (position, rotation, scale)
    - Visual representation (image, color)
    - Components (behaviors like RigidBody, Animator)
    - Lifecycle methods (update, render)
    """

    def __init__(self, x: float = 0, y: float = 0):
        # Transform
        self.position = Vector2(x, y)
        self.rotation = 0.0  # degrees
        self.scale = Vector2(1.0, 1.0)

        # Visual
        self.image = None  # pygame Surface
        self.color = (255, 255, 255)
        self.visible = True
        self.layer = 0  # Z-order

        # Components
        self.components = {}  # component_type -> component instance

        # Lifecycle
        self.active = True

    def add_component(self, component: 'Component'):
        """
        Add a behavior component to this sprite.

        Args:
            component: Component instance
        """
        pass

    def get_component(self, component_type: type) -> 'Component':
        """Get component by type."""
        pass

    def update(self, dt: float):
        """
        Update sprite and all components.

        Args:
            dt: Delta time in seconds
        """
        pass

    def render(self, screen, camera):
        """
        Render sprite to screen with camera offset.

        Args:
            screen: pygame Surface
            camera: Camera instance for viewport transform
        """
        pass

    def get_rect(self) -> 'pygame.Rect':
        """Get axis-aligned bounding box for collision."""
        pass
```

**Key Features**:
- Component-based behavior system
- Transform hierarchy support
- Camera-aware rendering
- Layering for draw order

---

### 5. Physics System (`v2_engine/physics/rigidbody.py`, `collision.py`)

**Purpose**: Built-in simple physics and AABB collision

```python
class RigidBody:
    """
    Component that adds physics behavior to a sprite.

    Handles velocity, acceleration, gravity, and collision response.
    """

    def __init__(self, sprite: Sprite):
        self.sprite = sprite

        # Physics properties
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.gravity_scale = 1.0
        self.mass = 1.0

        # Collision properties
        self.is_kinematic = False  # If True, not affected by forces
        self.is_trigger = False    # If True, no collision response
        self.layer_mask = -1       # Which layers can collide with this

        # State
        self.grounded = False
        self.collisions = []  # Collisions this frame

    def apply_force(self, force: Vector2):
        """Apply instantaneous force."""
        pass

    def apply_impulse(self, impulse: Vector2):
        """Apply velocity change."""
        pass

    def update(self, dt: float, world_gravity: Vector2):
        """Update physics simulation."""
        pass


class CollisionSystem:
    """
    Handles AABB collision detection and resolution.
    """

    @staticmethod
    def check_collision(rect_a: 'pygame.Rect', rect_b: 'pygame.Rect') -> bool:
        """Check if two rectangles overlap."""
        pass

    @staticmethod
    def resolve_collision(sprite_a: Sprite, sprite_b: Sprite):
        """
        Resolve collision between two sprites with RigidBody components.

        Applies collision response (separation and velocity changes).
        """
        pass

    @staticmethod
    def get_collision_normal(rect_a: 'pygame.Rect', rect_b: 'pygame.Rect') -> Vector2:
        """Get surface normal of collision (which direction to push)."""
        pass

    @staticmethod
    def detect_collisions(sprites: list) -> list:
        """
        Broad-phase collision detection.

        Returns:
            List of (sprite_a, sprite_b) collision pairs
        """
        pass
```

**Key Features**:
- Velocity-based movement
- Gravity simulation
- AABB collision with response
- Trigger colliders (no physics response)
- Grounded detection for platformers

---

### 6. Camera System (`v2_engine/core/camera.py`)

**Purpose**: Viewport management and sprite culling

```python
class Camera:
    """
    Camera controls viewport and provides world-to-screen transforms.
    """

    def __init__(self, width: int, height: int):
        self.position = Vector2(0, 0)  # World position of camera center
        self.width = width
        self.height = height
        self.zoom = 1.0

        # Camera bounds (optional, for level boundaries)
        self.bounds = None  # pygame.Rect

    def follow(self, target: Sprite, lerp_factor: float = 1.0):
        """
        Smoothly follow a target sprite.

        Args:
            target: Sprite to follow
            lerp_factor: Interpolation speed (1.0 = instant, 0.1 = smooth)
        """
        pass

    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        """Convert world position to screen coordinates."""
        pass

    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        """Convert screen position to world coordinates."""
        pass

    def is_visible(self, sprite: Sprite) -> bool:
        """Check if sprite is within camera viewport (for culling)."""
        pass

    def apply_bounds(self):
        """Clamp camera position to bounds if set."""
        pass
```

**Key Features**:
- Smooth camera following with lerp
- World/screen coordinate conversion
- Frustum culling for off-screen sprites
- Camera bounds for level edges

---

## Example Scene Implementation

### Level 01 Scene (`templates/platformer/scenes/level_01.py`)

```python
import pygame
from v2_engine.core.scene import Scene
from v2_engine.sprites.sprite import Sprite
from v2_engine.physics.rigidbody import RigidBody
from v2_engine.physics.collision import CollisionSystem
from v2_engine.core.camera import Camera
from v2_engine.utils.math import Vector2


class Player(Sprite):
    """Player character with platformer controls."""

    def __init__(self, x, y):
        super().__init__(x, y)

        # Visual (placeholder)
        self.image = pygame.Surface((32, 48))
        self.image.fill((0, 150, 255))

        # Physics
        self.rigidbody = RigidBody(self)
        self.add_component(self.rigidbody)

        # Movement
        self.move_speed = 200.0
        self.jump_force = 400.0

    def update(self, dt, input_handler):
        """Handle player input and update."""
        super().update(dt)

        # Horizontal movement
        move_x = 0
        if input_handler.is_key_down(pygame.K_LEFT) or input_handler.is_key_down(pygame.K_a):
            move_x = -1
        if input_handler.is_key_down(pygame.K_RIGHT) or input_handler.is_key_down(pygame.K_d):
            move_x = 1

        self.rigidbody.velocity.x = move_x * self.move_speed

        # Jumping
        if (input_handler.is_key_pressed(pygame.K_SPACE) or
            input_handler.is_key_pressed(pygame.K_w)) and self.rigidbody.grounded:
            self.rigidbody.apply_impulse(Vector2(0, -self.jump_force))


class Platform(Sprite):
    """Static platform."""

    def __init__(self, x, y, width, height):
        super().__init__(x, y)

        # Visual
        self.image = pygame.Surface((width, height))
        self.image.fill((100, 100, 100))

        # Physics (static)
        self.rigidbody = RigidBody(self)
        self.rigidbody.is_kinematic = True  # Not affected by forces
        self.add_component(self.rigidbody)


class Level01Scene(Scene):
    """First level - simple platforming."""

    def __init__(self, game):
        super().__init__(game)

        self.player = None
        self.platforms = []
        self.camera = None

    def on_enter(self):
        """Initialize level when scene loads."""
        # Create camera
        screen_width, screen_height = self.game.project_config['window']['width'], \
                                       self.game.project_config['window']['height']
        self.camera = Camera(screen_width, screen_height)

        # Create player
        self.player = Player(100, 100)

        # Create platforms
        self.platforms = [
            Platform(0, 500, 800, 50),      # Ground
            Platform(200, 400, 150, 20),    # Platform 1
            Platform(400, 300, 150, 20),    # Platform 2
            Platform(600, 400, 150, 20),    # Platform 3
        ]

        # Sprite groups
        self.sprite_groups['all'] = [self.player] + self.platforms

    def update(self, dt):
        """Update level logic."""
        # Update player with input
        self.player.update(dt, self.game.input_handler)

        # Update platforms (mostly static)
        for platform in self.platforms:
            platform.update(dt)

        # Apply gravity
        world_gravity = Vector2(0, 980)  # pixels/s^2
        self.player.rigidbody.update(dt, world_gravity)

        # Collision detection
        for platform in self.platforms:
            if CollisionSystem.check_collision(self.player.get_rect(), platform.get_rect()):
                CollisionSystem.resolve_collision(self.player, platform)
                self.player.rigidbody.grounded = True

        # Camera follow player
        self.camera.follow(self.player, lerp_factor=0.1)

    def render(self, screen):
        """Render level."""
        # Clear screen
        screen.fill((135, 206, 235))  # Sky blue

        # Render all sprites
        for sprite in self.sprite_groups['all']:
            if self.camera.is_visible(sprite):
                sprite.render(screen, self.camera)
```

**Key Concepts Demonstrated**:
- Scene lifecycle (on_enter initializes level)
- Player input handling through InputHandler
- Physics simulation with gravity and collision
- Camera following player smoothly
- Sprite groups for organization

---

## 2d_project.json Format

```json
{
  "title": "My Platformer Game",
  "version": "1.0.0",
  "engine_version": "2.0.0",

  "window": {
    "width": 800,
    "height": 600,
    "fullscreen": false,
    "resizable": false,
    "title": "My Platformer"
  },

  "physics": {
    "gravity": {
      "x": 0,
      "y": 980
    },
    "pixels_per_meter": 100
  },

  "scenes": {
    "entry_scene": "main_menu",
    "scenes": [
      {
        "name": "main_menu",
        "file": "scenes/main_menu.py",
        "class": "MainMenuScene"
      },
      {
        "name": "level_01",
        "file": "scenes/level_01.py",
        "class": "Level01Scene"
      }
    ]
  },

  "assets": {
    "sprites": "assets/sprites/",
    "sounds": "assets/sounds/",
    "music": "assets/music/",
    "fonts": "assets/fonts/"
  },

  "build": {
    "include_files": [
      "scenes/**/*.py",
      "assets/**/*"
    ],
    "exclude_files": [
      "**/__pycache__",
      "**/*.pyc"
    ]
  }
}
```

---

## Test Runner Script (`test_v2.py`)

```python
#!/usr/bin/env python3
"""
Scribe Engine V2 - Test Runner

Simple script to launch V2 games for testing during development.
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from v2_engine.core.game import Game


def main():
    # For now, hardcode the platformer demo path
    demo_path = os.path.join(project_root, 'v2_engine', 'templates', 'platformer')

    if not os.path.exists(demo_path):
        print(f"Error: Demo project not found at {demo_path}")
        return 1

    print("=" * 60)
    print("Scribe Engine V2 - Test Runner")
    print("=" * 60)
    print(f"Loading project: {demo_path}")
    print()

    # Create and run game
    game = Game(demo_path)

    if not game.initialize():
        print("Error: Failed to initialize game engine")
        return 1

    print("Starting game loop... (Press ESC or close window to quit)")
    game.run()

    print("\nGame ended. Goodbye!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

---

## Simple Platformer Demo Specification

### Gameplay

**Objective**: Reach the goal platform at the end of the level

**Controls**:
- **Arrow Keys / WASD**: Move left/right
- **Space / W**: Jump
- **ESC**: Return to main menu

**Features**:
- Player character with smooth movement
- Multiple platforms at different heights
- Simple collectibles (coins/gems)
- Goal platform that triggers level complete
- Score display in UI
- Main menu with "Start Game" button

### Placeholder Assets

For Phase 1, use colored rectangles:
- **Player**: 32x48px blue rectangle
- **Platforms**: Gray rectangles (variable sizes)
- **Collectibles**: 16x16px yellow circles
- **Goal**: 64x64px green rectangle with flag icon (text "GOAL")
- **Background**: Gradient sky blue to light cyan

### Level Design

**Level 01 Layout**:
```
                           [GOAL]

                  [====]
       [C]
  [====]           [C]        [====]
            [====]       [====]

[P]
[========================================] (Ground)

P = Player start
[====] = Platform
[C] = Collectible
[GOAL] = Goal platform
```

### UI Elements

- **Top-left**: Score counter ("Score: 0")
- **Top-right**: Timer ("Time: 00:00")
- **Main Menu**: Title text, "Start Game" button, "Quit" button

---

## Development Best Practices

### Code Style
- Follow PEP 8 conventions
- Type hints for all public methods
- Docstrings for all classes and public methods
- Keep files under 500 lines (split when larger)

### Testing Strategy
- Manual testing with test_v2.py script
- Test each system in isolation first
- Build platformer demo incrementally
- Test on both 60Hz and 144Hz displays

### Performance Targets
- Maintain 60 FPS with 100+ sprites
- Scene transitions under 100ms
- Memory usage under 200MB for simple games

### Git Workflow
- Commit after each completed task
- Use descriptive commit messages
- Branch: `v2-development` (already created)
- Keep development on v2-development branch (do not merge to main)

---

## Phase 1 Completion Checklist

- [ ] Core game loop runs at stable 60 FPS
- [ ] Scenes can be created, loaded, and switched
- [ ] Input handler provides keyboard and mouse state
- [ ] Sprites render with correct layering
- [ ] Camera follows player smoothly
- [ ] AABB collision detection works
- [ ] Collision response prevents overlapping
- [ ] Gravity and velocity physics work
- [ ] Player can walk and jump on platforms
- [ ] Collectibles can be picked up
- [ ] UI text renders on screen
- [ ] Main menu scene works
- [ ] Gameplay scene works with platformer demo
- [ ] Test runner launches games successfully
- [ ] Code is documented and clean

---

## Next Steps (Phase 2 Preview)

Once Phase 1 is complete, Phase 2 will focus on:

1. **IDE Integration**: Web interface for visual scene editing
2. **Tilemap Editor**: Design levels with tilemap tools
3. **Animation System**: Sprite sheets and animation controllers
4. **Audio System**: Sound effects and background music
5. **Particle System**: Visual effects (explosions, trails, etc.)
6. **UI System Expansion**: Menus, health bars, dialogs

---

## Questions or Issues?

If you encounter design decisions or technical challenges during implementation:
1. Document the issue and potential solutions
2. Make a practical decision that unblocks development
3. Add a TODO comment for future refinement
4. Keep moving forward - perfection is the enemy of progress

**Remember**: Phase 1 is about proving the concept works. Polish comes later.

---

**Last Updated**: 2024-09-30
**Status**: Ready to implement
