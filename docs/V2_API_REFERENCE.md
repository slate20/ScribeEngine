# Scribe Engine V2 - API Reference

**Version**: 2.0.0 (Phase 1)
**Last Updated**: 2025-09-30

This document provides complete API documentation for Scribe Engine V2's core classes and systems.

---

## Table of Contents

1. [Core Systems](#core-systems)
   - [Game](#game-class)
   - [Scene](#scene-class)
   - [SceneManager](#scenemanager-class)
   - [InputHandler](#inputhandler-class)
   - [TimeManager](#timemanager-class)
   - [Camera](#camera-class)

2. [Sprite System](#sprite-system)
   - [Sprite](#sprite-class)
   - [SpriteGroup](#spritegroup-class)
   - [Component](#component-class)

3. [Physics System](#physics-system)
   - [RigidBody](#rigidbody-component)
   - [CollisionSystem](#collisionsystem-class)

4. [UI System](#ui-system)
   - [Widget](#widget-class)
   - [Button](#button-class)
   - [TextLabel](#textlabel-class)
   - [Panel](#panel-class)

5. [Utilities](#utilities)
   - [Vector2](#vector2-class)
   - [Math Helpers](#math-helpers)
   - [Color Constants](#color-constants)

---

## Core Systems

### Game Class

**Location**: `v2_engine/core/game.py`

Main game controller that handles pygame initialization, game loop, and core engine services.

#### Constructor

```python
Game(project_path: str)
```

**Parameters**:
- `project_path`: Absolute path to the game project directory

**Example**:
```python
game = Game('/path/to/my_game')
```

#### Methods

##### `initialize() -> bool`

Initialize pygame and core engine systems.

**Returns**: `True` if successful, `False` otherwise

**Example**:
```python
if not game.initialize():
    print("Failed to initialize")
    return
```

##### `run()`

Start the main game loop. Runs until `quit()` is called or window is closed.

**Example**:
```python
game.run()
```

##### `quit()`

Clean shutdown of pygame and engine systems.

**Example**:
```python
game.quit()
```

#### Properties

- `project_config`: Dictionary containing project configuration from `2d_project.json`
- `screen`: Pygame display surface
- `scene_manager`: SceneManager instance
- `input_handler`: InputHandler instance
- `time_manager`: TimeManager instance

---

### Scene Class

**Location**: `v2_engine/core/scene.py`

Base class for all game scenes (menus, levels, etc.).

#### Constructor

```python
Scene(game: Game)
```

**Parameters**:
- `game`: Reference to main Game instance

#### Methods

##### `on_enter()`

Called when scene becomes active. Override to initialize scene.

**Example**:
```python
def on_enter(self):
    self.player = Player(100, 100)
    self.enemies = [Enemy(200, 200), Enemy(400, 200)]
```

##### `on_exit()`

Called when scene becomes inactive. Override for cleanup.

**Example**:
```python
def on_exit(self):
    print("Cleaning up level...")
```

##### `update(dt: float)`

Update scene logic. Override to implement game logic.

**Parameters**:
- `dt`: Delta time in seconds

**Example**:
```python
def update(self, dt):
    self.player.update(dt)
    for enemy in self.enemies:
        enemy.update(dt)
```

##### `render(screen)`

Render scene to screen. Override to draw graphics.

**Parameters**:
- `screen`: Pygame Surface to render to

**Example**:
```python
def render(self, screen):
    screen.fill((135, 206, 235))  # Sky blue
    self.player.render(screen, self.camera)
```

##### `handle_event(event)`

Handle pygame events. Override for custom event handling.

**Parameters**:
- `event`: Pygame event object

#### Properties

- `game`: Reference to Game instance
- `sprite_groups`: Dictionary of named sprite groups
- `ui_elements`: List of UI widgets
- `camera`: Camera instance (optional)

---

### SceneManager Class

**Location**: `v2_engine/core/scene.py`

Manages scene loading, switching, and lifecycle.

#### Methods

##### `register_scene(name: str, scene: Scene)`

Register a scene for later use.

**Parameters**:
- `name`: Unique scene identifier
- `scene`: Scene instance

**Example**:
```python
main_menu = MainMenuScene(game)
game.scene_manager.register_scene("main_menu", main_menu)
```

##### `load_scene(name: str)`

Switch to a different scene.

**Parameters**:
- `name`: Name of scene to load

**Example**:
```python
self.game.scene_manager.load_scene("level_01")
```

---

### InputHandler Class

**Location**: `v2_engine/core/input.py`

Centralized input state management for keyboard and mouse.

#### Methods

##### `is_key_down(key) -> bool`

Check if key is currently held down.

**Parameters**:
- `key`: Pygame key constant (e.g., `pygame.K_SPACE`)

**Returns**: `True` if key is held

**Example**:
```python
if input_handler.is_key_down(pygame.K_LEFT):
    player.move_left()
```

##### `is_key_pressed(key) -> bool`

Check if key was pressed this frame (once).

**Parameters**:
- `key`: Pygame key constant

**Returns**: `True` if key was just pressed

**Example**:
```python
if input_handler.is_key_pressed(pygame.K_SPACE):
    player.jump()
```

##### `is_key_released(key) -> bool`

Check if key was released this frame.

**Parameters**:
- `key`: Pygame key constant

**Returns**: `True` if key was just released

##### `get_mouse_pos() -> tuple`

Get current mouse position.

**Returns**: Tuple of (x, y) screen coordinates

**Example**:
```python
mouse_x, mouse_y = input_handler.get_mouse_pos()
```

##### `is_mouse_button_down(button: int) -> bool`

Check if mouse button is held down.

**Parameters**:
- `button`: Mouse button number (1=left, 2=middle, 3=right)

**Returns**: `True` if button is held

##### `is_mouse_button_pressed(button: int) -> bool`

Check if mouse button was clicked this frame.

**Parameters**:
- `button`: Mouse button number

**Returns**: `True` if button was just clicked

---

### TimeManager Class

**Location**: `v2_engine/core/time.py`

Manages delta time and frame timing.

#### Constructor

```python
TimeManager(target_fps: int = 60)
```

**Parameters**:
- `target_fps`: Target frames per second (default: 60)

#### Properties

- `delta_time`: Delta time in seconds since last frame
- `fps`: Current frames per second

**Example**:
```python
dt = game.time_manager.delta_time
current_fps = game.time_manager.fps
```

---

### Camera Class

**Location**: `v2_engine/core/camera.py`

Camera controls viewport and provides world-to-screen transforms.

#### Constructor

```python
Camera(width: int, height: int)
```

**Parameters**:
- `width`: Viewport width in pixels
- `height`: Viewport height in pixels

#### Methods

##### `follow(target, lerp_factor: float = 1.0)`

Smoothly follow a target sprite or position.

**Parameters**:
- `target`: Sprite or Vector2 to follow
- `lerp_factor`: Interpolation speed (1.0 = instant, 0.1 = smooth)

**Example**:
```python
self.camera.follow(self.player, lerp_factor=0.1)
```

##### `world_to_screen(world_pos: Vector2) -> Vector2`

Convert world position to screen coordinates.

##### `screen_to_world(screen_pos: Vector2) -> Vector2`

Convert screen position to world coordinates.

##### `is_visible(sprite) -> bool`

Check if sprite is within camera viewport (for culling).

##### `set_bounds(x: float, y: float, width: float, height: float)`

Set camera bounds in world coordinates.

**Example**:
```python
self.camera.set_bounds(0, 0, 1600, 600)  # Level bounds
```

---

## Sprite System

### Sprite Class

**Location**: `v2_engine/sprites/sprite.py`

Base class for all game objects with visual representation.

#### Constructor

```python
Sprite(x: float = 0, y: float = 0)
```

**Parameters**:
- `x, y`: Initial position

#### Methods

##### `add_component(component: Component)`

Add a behavior component to sprite.

**Example**:
```python
rigidbody = RigidBody(self)
self.add_component(rigidbody)
```

##### `get_component(component_type: type) -> Component`

Get component by type.

**Example**:
```python
rb = self.get_component(RigidBody)
if rb:
    rb.velocity.x = 100
```

##### `update(dt: float)`

Update sprite and all components.

##### `render(screen, camera=None)`

Render sprite to screen.

##### `get_rect() -> pygame.Rect`

Get axis-aligned bounding box for collision.

#### Properties

- `position`: Vector2 position
- `rotation`: Rotation in degrees
- `scale`: Vector2 scale
- `image`: Pygame Surface for rendering
- `color`: RGB color tuple
- `visible`: Boolean visibility flag
- `layer`: Integer z-order for rendering
- `active`: Boolean active state

---

### SpriteGroup Class

**Location**: `v2_engine/sprites/group.py`

Container for sprites with batch update and render.

#### Methods

##### `add(sprite: Sprite)`

Add sprite to group.

##### `remove(sprite: Sprite)`

Remove sprite from group.

##### `clear()`

Remove all sprites from group.

##### `update(dt: float)`

Update all sprites in group.

##### `render(screen, camera=None)`

Render all sprites sorted by layer.

**Example**:
```python
all_sprites = SpriteGroup("all")
all_sprites.add(player)
all_sprites.add(enemy)
all_sprites.update(dt)
all_sprites.render(screen, camera)
```

---

### Component Class

**Location**: `v2_engine/sprites/components.py`

Base class for sprite components (modular behaviors).

#### Constructor

```python
Component(sprite: Sprite)
```

#### Methods

##### `update(dt: float)`

Update component logic. Override in subclasses.

##### `on_destroy()`

Called when component is removed.

#### Properties

- `sprite`: Reference to parent sprite
- `enabled`: Boolean enabled state

---

## Physics System

### RigidBody Component

**Location**: `v2_engine/physics/rigidbody.py`

Component that adds physics behavior to sprites.

#### Constructor

```python
RigidBody(sprite: Sprite)
```

#### Methods

##### `apply_force(force: Vector2)`

Apply instantaneous force (F = ma).

**Example**:
```python
wind_force = Vector2(100, 0)
rigidbody.apply_force(wind_force)
```

##### `apply_impulse(impulse: Vector2)`

Apply velocity change directly.

**Example**:
```python
jump_impulse = Vector2(0, -500)
rigidbody.apply_impulse(jump_impulse)
```

##### `update(dt: float, world_gravity: Vector2 = None)`

Update physics simulation.

**Parameters**:
- `dt`: Delta time
- `world_gravity`: Gravity vector (default: Vector2(0, 980))

#### Properties

- `velocity`: Vector2 velocity
- `acceleration`: Vector2 acceleration
- `gravity_scale`: Float multiplier for gravity (default: 1.0)
- `mass`: Float mass (default: 1.0)
- `is_kinematic`: Boolean - if True, not affected by forces
- `is_trigger`: Boolean - if True, no collision response
- `grounded`: Boolean - true if sprite is on ground
- `friction`: Float ground friction (default: 0.1)
- `air_resistance`: Float air drag (default: 0.01)

---

### CollisionSystem Class

**Location**: `v2_engine/physics/collision.py`

AABB collision detection and resolution.

#### Static Methods

##### `check_collision(rect_a: pygame.Rect, rect_b: pygame.Rect) -> bool`

Check if two rectangles overlap.

##### `resolve_collision(sprite_a: Sprite, sprite_b: Sprite)`

Resolve collision between two sprites with RigidBody components.

**Example**:
```python
if CollisionSystem.check_collision(player.get_rect(), platform.get_rect()):
    CollisionSystem.resolve_collision(player, platform)
```

##### `detect_collisions(sprites: list) -> list`

Broad-phase collision detection.

**Returns**: List of (sprite_a, sprite_b) collision pairs

**Example**:
```python
collision_pairs = CollisionSystem.detect_collisions(all_sprites)
CollisionSystem.resolve_collisions(collision_pairs)
```

---

## UI System

### Widget Class

**Location**: `v2_engine/ui/widget.py`

Base class for UI elements (screen-space, not affected by camera).

#### Constructor

```python
Widget(x: float, y: float, width: float, height: float)
```

#### Methods

##### `handle_event(event)`

Handle pygame events.

##### `update(dt: float)`

Update widget logic.

##### `render(screen)`

Render widget to screen.

#### Properties

- `position`: Vector2 screen position
- `width, height`: Float dimensions
- `visible`: Boolean visibility
- `enabled`: Boolean enabled state
- `on_click`: Callback function for click events

---

### Button Class

**Location**: `v2_engine/ui/button.py`

Clickable button with hover and click states.

#### Constructor

```python
Button(x: float, y: float, width: float, height: float, text: str, font_size: int = 24)
```

**Parameters**:
- `x, y`: Center position
- `width, height`: Button size
- `text`: Button label
- `font_size`: Font size in pixels

**Example**:
```python
start_button = Button(400, 300, 200, 60, "START GAME")
start_button.on_click = self.start_game
```

---

### TextLabel Class

**Location**: `v2_engine/ui/text.py`

Simple text label widget.

#### Constructor

```python
TextLabel(x: float, y: float, text: str, font_size: int = 24)
```

#### Methods

##### `set_text(text: str)`

Update label text.

#### Properties

- `text`: String text content
- `text_color`: RGB color tuple
- `align`: String alignment ("left", "center", "right")

**Example**:
```python
title = TextLabel(400, 100, "MY GAME", font_size=64)
title.align = "center"
title.text_color = (255, 255, 0)
```

---

### Panel Class

**Location**: `v2_engine/ui/panel.py`

Container panel for grouping widgets.

#### Methods

##### `add_widget(widget: Widget)`

Add widget to panel.

##### `remove_widget(widget: Widget)`

Remove widget from panel.

**Example**:
```python
panel = Panel(100, 100, 300, 200)
label = TextLabel(150, 120, "Score: 0")
panel.add_widget(label)
```

---

## Utilities

### Vector2 Class

**Location**: `v2_engine/utils/math.py`

2D vector for positions, velocities, and directions.

#### Constructor

```python
Vector2(x: float = 0, y: float = 0)
```

#### Operators

- `+`, `-`: Vector addition/subtraction
- `*`, `/`: Scalar multiplication/division
- `-vec`: Negation

**Example**:
```python
pos = Vector2(100, 200)
vel = Vector2(50, -100)
new_pos = pos + vel * dt
```

#### Methods

##### `length() -> float`

Calculate vector magnitude.

##### `normalized() -> Vector2`

Return unit vector in same direction.

##### `dot(other: Vector2) -> float`

Dot product.

##### `distance_to(other: Vector2) -> float`

Calculate distance to another vector.

##### `lerp(other: Vector2, t: float) -> Vector2`

Linear interpolation.

#### Static Methods

- `Vector2.zero()`: Return (0, 0)
- `Vector2.one()`: Return (1, 1)
- `Vector2.up()`: Return (0, -1)
- `Vector2.down()`: Return (0, 1)
- `Vector2.left()`: Return (-1, 0)
- `Vector2.right()`: Return (1, 0)

---

### Math Helpers

**Location**: `v2_engine/utils/math.py`

##### `clamp(value: float, min_value: float, max_value: float) -> float`

Clamp value between min and max.

##### `lerp(a: float, b: float, t: float) -> float`

Linear interpolation.

---

### Color Constants

**Location**: `v2_engine/utils/color.py`

Pre-defined color constants (RGB tuples):

- `WHITE`, `BLACK`, `RED`, `GREEN`, `BLUE`
- `YELLOW`, `CYAN`, `MAGENTA`
- `GRAY`, `LIGHT_GRAY`, `DARK_GRAY`
- `SKY_BLUE`, `GRASS_GREEN`, `PLATFORM_GRAY`

**Functions**:
- `hex_to_rgb(hex_color: str) -> tuple`
- `rgb_to_hex(r: int, g: int, b: int) -> str`

---

## Project Configuration

### 2d_project.json Format

```json
{
  "title": "My Game",
  "version": "1.0.0",
  "engine_version": "2.0.0",

  "window": {
    "width": 800,
    "height": 600,
    "fullscreen": false,
    "resizable": false,
    "title": "My Game Window Title"
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
      }
    ]
  }
}
```

---

**End of API Reference**
