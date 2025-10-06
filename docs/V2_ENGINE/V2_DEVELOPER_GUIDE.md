# Scribe Engine V2 - Developer Guide

**Version**: 2.0.0 (Phase 1)
**Last Updated**: 2025-09-30

This guide teaches you how to create games with Scribe Engine V2.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Creating Your First Scene](#creating-your-first-scene)
3. [Working with Sprites](#working-with-sprites)
4. [Adding Physics](#adding-physics)
5. [Building UI](#building-ui)
6. [Scene Management](#scene-management)
7. [Best Practices](#best-practices)
8. [Common Patterns](#common-patterns)

---

## Getting Started

### Project Structure

Every V2 game project has this structure:

```
my_game/
├── 2d_project.json       # Project configuration
├── scenes/               # Scene Python files
│   ├── main_menu.py
│   └── level_01.py
└── assets/               # Game assets
    ├── sprites/
    ├── sounds/
    └── music/
```

### Creating a New Project

1. Create a project directory
2. Create `2d_project.json`:

```json
{
  "title": "My Game",
  "version": "1.0.0",
  "engine_version": "2.0.0",

  "window": {
    "width": 800,
    "height": 600,
    "fullscreen": false,
    "title": "My Awesome Game"
  },

  "physics": {
    "gravity": {"x": 0, "y": 980}
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

3. Create your first scene (see next section)

4. Run with test runner:

```bash
python3 test_v2.py
```

---

## Creating Your First Scene

### Basic Scene Template

Create `scenes/main_menu.py`:

```python
import pygame
from v2_engine.core.scene import Scene
from v2_engine.ui.button import Button
from v2_engine.ui.text import TextLabel


class MainMenuScene(Scene):
    """Main menu with title and start button."""

    def __init__(self, game):
        super().__init__(game)
        self.title = None
        self.start_button = None

    def on_enter(self):
        """Initialize menu when scene loads."""
        # Get screen dimensions
        width = self.game.project_config['window']['width']
        height = self.game.project_config['window']['height']

        # Create title
        self.title = TextLabel(width // 2, 100, "MY GAME", font_size=64)
        self.title.align = "center"
        self.title.text_color = (255, 255, 0)

        # Create start button
        self.start_button = Button(width // 2, height // 2, 200, 60, "START")
        self.start_button.on_click = self.start_game

        # Add to UI list
        self.ui_elements = [self.title, self.start_button]

    def start_game(self):
        """Button callback - load game scene."""
        self.game.scene_manager.load_scene("level_01")

    def handle_event(self, event):
        """Handle input events."""
        for element in self.ui_elements:
            element.handle_event(event)

    def update(self, dt):
        """Update menu (60 times per second)."""
        for element in self.ui_elements:
            element.update(dt)

    def render(self, screen):
        """Draw menu to screen."""
        screen.fill((0, 0, 0))  # Black background

        for element in self.ui_elements:
            element.render(screen)
```

### Scene Lifecycle

Scenes have these lifecycle methods:

1. **`__init__(game)`** - Constructor, store references
2. **`on_enter()`** - Scene becomes active, create objects
3. **`update(dt)`** - Called every frame (60 FPS), update logic
4. **`render(screen)`** - Called every frame, draw graphics
5. **`on_exit()`** - Scene becomes inactive, cleanup

---

## Working with Sprites

### Creating Custom Sprites

Sprites are game objects with position, graphics, and behaviors.

```python
import pygame
from v2_engine.sprites.sprite import Sprite
from v2_engine.physics.rigidbody import RigidBody
from v2_engine.utils.math import Vector2


class Player(Sprite):
    """Player character sprite."""

    def __init__(self, x, y):
        super().__init__(x, y)

        # Visual appearance
        self.image = pygame.Surface((32, 48))
        self.image.fill((0, 150, 255))  # Blue rectangle
        self.layer = 10  # Render layer (higher = front)

        # Add physics
        self.rigidbody = RigidBody(self)
        self.add_component(self.rigidbody)

        # Custom properties
        self.health = 100
        self.speed = 200

    def update(self, dt):
        """Update player logic."""
        super().update(dt)  # Update components

        # Custom update logic here
        if self.health <= 0:
            self.active = False
```

### Using Sprites in Scenes

```python
from v2_engine.sprites.group import SpriteGroup

class Level01Scene(Scene):
    def on_enter(self):
        # Create sprite group
        self.all_sprites = SpriteGroup("all")

        # Create player
        self.player = Player(100, 100)
        self.all_sprites.add(self.player)

    def update(self, dt):
        # Update all sprites
        self.all_sprites.update(dt)

    def render(self, screen):
        screen.fill((135, 206, 235))  # Sky blue

        # Render all sprites
        self.all_sprites.render(screen, self.camera)
```

---

## Adding Physics

### RigidBody Component

The RigidBody component adds physics to sprites.

```python
class MovingPlatform(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.image = pygame.Surface((100, 20))
        self.image.fill((100, 100, 100))

        # Add physics
        rigidbody = RigidBody(self)
        rigidbody.is_kinematic = True  # Not affected by gravity
        rigidbody.gravity_scale = 0
        self.add_component(rigidbody)
```

### Collision Detection

```python
from v2_engine.physics.collision import CollisionSystem

class GameScene(Scene):
    def update(self, dt):
        # Apply physics
        world_gravity = Vector2(0, 980)
        self.player.rigidbody.update(dt, world_gravity)

        # Detect collisions
        collision_pairs = CollisionSystem.detect_collisions(
            list(self.solid_sprites)
        )

        # Resolve collisions
        CollisionSystem.resolve_collisions(collision_pairs)
```

### Platform Character Controller

```python
class Player(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y)

        # ... sprite setup ...

        self.move_speed = 300
        self.jump_force = 500

    def handle_input(self, input_handler, dt):
        """Handle player controls."""
        # Horizontal movement
        move_x = 0
        if input_handler.is_key_down(pygame.K_LEFT):
            move_x = -1
        if input_handler.is_key_down(pygame.K_RIGHT):
            move_x = 1

        self.rigidbody.velocity.x = move_x * self.move_speed

        # Jumping (only when grounded)
        if input_handler.is_key_pressed(pygame.K_SPACE):
            if self.rigidbody.grounded:
                self.rigidbody.velocity.y = -self.jump_force
```

---

## Building UI

### Creating Menus

```python
from v2_engine.ui.button import Button
from v2_engine.ui.text import TextLabel
from v2_engine.ui.panel import Panel

class PauseMenuScene(Scene):
    def on_enter(self):
        width = self.game.project_config['window']['width']
        height = self.game.project_config['window']['height']

        # Semi-transparent panel
        self.panel = Panel(
            width // 2 - 150,
            height // 2 - 100,
            300,
            200
        )

        # Title
        title = TextLabel(width // 2, height // 2 - 50, "PAUSED")
        title.align = "center"

        # Resume button
        resume_btn = Button(width // 2, height // 2, 150, 50, "RESUME")
        resume_btn.on_click = self.resume_game

        # Quit button
        quit_btn = Button(width // 2, height // 2 + 60, 150, 50, "QUIT")
        quit_btn.on_click = self.quit_to_menu

        self.panel.add_widget(title)
        self.panel.add_widget(resume_btn)
        self.panel.add_widget(quit_btn)

        self.ui_elements = [self.panel]

    def resume_game(self):
        self.game.scene_manager.load_scene("level_01")

    def quit_to_menu(self):
        self.game.scene_manager.load_scene("main_menu")
```

### HUD (Heads-Up Display)

```python
class GameScene(Scene):
    def _render_hud(self, screen):
        """Render game UI overlay."""
        try:
            font = pygame.font.Font(None, 36)

            # Health bar
            health_text = font.render(f"Health: {self.player.health}", True, (255, 255, 255))
            screen.blit(health_text, (10, 10))

            # Score
            score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
            screen.blit(score_text, (10, 50))

        except Exception as e:
            print(f"Error rendering HUD: {e}")

    def render(self, screen):
        # ... render game ...
        self._render_hud(screen)
```

---

## Scene Management

### Switching Scenes

```python
# From within a scene
self.game.scene_manager.load_scene("level_02")
```

### Passing Data Between Scenes

**Option 1: Store in Game instance**

```python
class Level01(Scene):
    def on_exit(self):
        # Save level state
        self.game.level_01_score = self.score

class Level02(Scene):
    def on_enter(self):
        # Load previous score
        if hasattr(self.game, 'level_01_score'):
            self.total_score = self.game.level_01_score
```

**Option 2: Use scene properties**

```python
class ResultsScene(Scene):
    def __init__(self, game, score=0):
        super().__init__(game)
        self.final_score = score

# When loading
results = ResultsScene(self.game, score=self.score)
self.game.scene_manager.register_scene("results", results)
self.game.scene_manager.load_scene("results")
```

---

## Best Practices

### Performance

**Use Sprite Groups**
```python
# Good - batch rendering
self.all_sprites.render(screen, camera)

# Bad - individual rendering
for sprite in sprites:
    sprite.render(screen, camera)
```

**Enable Camera Culling**
```python
def render(self, screen):
    for sprite in self.all_sprites:
        if self.camera.is_visible(sprite):
            sprite.render(screen, self.camera)
```

**Limit Collision Checks**
```python
# Only check solid objects, not UI or decorations
collision_pairs = CollisionSystem.detect_collisions(
    list(self.solid_sprites)  # Not all_sprites
)
```

### Code Organization

**Keep Scenes Simple**
- One scene class per file
- Use helper methods (`_render_ui`, `_handle_input`)
- Move complex sprites to separate files

**Component-Based Design**
```python
# Create reusable components
class HealthComponent(Component):
    def __init__(self, sprite, max_health=100):
        super().__init__(sprite)
        self.health = max_health
        self.max_health = max_health

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.sprite.active = False
```

### Error Handling

**Always wrap rendering code**
```python
def render(self, screen):
    try:
        # Rendering code
        font = pygame.font.Font(None, 36)
        text = font.render("Hello", True, (255, 255, 255))
        screen.blit(text, (10, 10))
    except Exception as e:
        print(f"Render error: {e}")
```

---

## Common Patterns

### Jump Buffering

Allow jumping shortly after pressing jump button:

```python
class Player(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.jump_buffer_time = 0
        self.jump_buffer_duration = 0.1  # 100ms

    def handle_input(self, input_handler, dt):
        # Record jump input
        if input_handler.is_key_pressed(pygame.K_SPACE):
            self.jump_buffer_time = self.jump_buffer_duration

        # Decay buffer
        if self.jump_buffer_time > 0:
            self.jump_buffer_time -= dt

            # Execute jump if grounded
            if self.rigidbody.grounded:
                self.rigidbody.velocity.y = -self.jump_force
                self.jump_buffer_time = 0  # Consume jump
```

### Coyote Time

Allow jumping shortly after leaving platform:

```python
class Player(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.coyote_time = 0
        self.coyote_duration = 0.15  # 150ms
        self.was_grounded = False

    def update(self, dt):
        super().update(dt)

        # Track grounded state
        if self.rigidbody.grounded:
            self.coyote_time = self.coyote_duration
            self.was_grounded = True
        elif self.was_grounded:
            self.coyote_time -= dt
            if self.coyote_time <= 0:
                self.was_grounded = False

    def can_jump(self):
        return self.rigidbody.grounded or self.coyote_time > 0
```

### Collectibles

```python
class Coin(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y)

        # Yellow circle
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 220, 0), (8, 8), 8)

        # Trigger collider (no physics response)
        rb = RigidBody(self)
        rb.is_trigger = True
        rb.is_kinematic = True
        rb.gravity_scale = 0
        self.add_component(rb)

class GameScene(Scene):
    def update(self, dt):
        # Check for collection
        for coin in self.coins[:]:
            if CollisionSystem.check_collision(
                self.player.get_rect(), coin.get_rect()
            ):
                self.score += 10
                self.coins.remove(coin)
                self.all_sprites.remove(coin)
```

### Camera Following

```python
from v2_engine.core.camera import Camera

class GameScene(Scene):
    def on_enter(self):
        # Create camera
        width = self.game.project_config['window']['width']
        height = self.game.project_config['window']['height']
        self.camera = Camera(width, height)

        # Set level bounds (optional)
        self.camera.set_bounds(0, 0, 1600, 600)

    def update(self, dt):
        # Camera follows player smoothly
        self.camera.follow(self.player, lerp_factor=0.1)

    def render(self, screen):
        # Render with camera offset
        self.all_sprites.render(screen, self.camera)
```

---

## Next Steps

- **Review the API Reference** (`V2_API_REFERENCE.md`) for detailed class documentation
- **Study the Platformer Demo** (`v2_engine/templates/platformer/`) for complete examples
- **Experiment!** Create your own sprites, scenes, and game mechanics

---

**Happy Game Development!**
