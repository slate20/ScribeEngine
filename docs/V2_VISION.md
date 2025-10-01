# Scribe Engine v2: Vision & Development Plan

**Status**: Prototype/MVP Phase
**Branch**: v2-development
**Target**: Scene-based 2D game engine with Python-first approach
**Last Updated**: 2025-09-30

---

## Core Vision

Scribe Engine v2 is a **scene-based 2D game engine** that bridges the gap between text-based engines and complex tools like Godot. It maintains the Scribe Engine philosophy: **approachable for beginners, powerful for advanced users, with Python at its core.**

### Design Principles

1. **Python-First**: If you can write it in Python, you can build it
2. **Visual + Code**: Visual editor for layout, Python for logic
3. **No Setup Required**: Web IDE with one-click distribution
4. **Transparent Architecture**: No magic, readable generated code
5. **Flexible & Extensible**: From simple games to open-world 2D RPGs

### What Makes v2 Different from v1

| Aspect | v1 (Text-Based) | v2 (Scene-Based) |
|--------|----------------|------------------|
| **Structure** | Passage-based | Scene-based |
| **Flow** | Turn-based narrative | Frame-based gameplay |
| **Rendering** | HTML/CSS | 2D sprite rendering |
| **Interaction** | Click/choose | Real-time input |
| **Game Types** | IF, VN, text RPGs | Platformers, action, adventure, RPGs |
| **Physics** | None | Optional 2D physics |

**Note**: v1 remains available and supported - no compatibility needed between versions.

---

## Technical Architecture

### Scene System (Core Concept)

Scenes replace passages as the fundamental building block:

```python
# scenes/forest_level.py
class ForestLevel(Scene):
    """
    Scenes are Python classes that run in a game loop.
    Engine provides helpers to make this accessible.
    """

    def setup(self):
        """Called once when scene loads"""
        # Simple sprite creation
        self.player = self.add_sprite(
            'player.png',
            x=100, y=100,
            collision=True
        )

        self.enemy = self.add_sprite(
            'enemy.png',
            x=300, y=100,
            ai='patrol'  # Built-in AI behaviors
        )

        # Background
        self.background = 'forest_bg.png'

        # Physics (opt-in)
        self.player.gravity = True
        self.player.speed = 200

    def update(self, dt):
        """Called every frame (~60 FPS)"""
        # Handle input
        if self.input.key_down('space') and self.player.on_ground:
            self.player.jump()

        # Check collisions
        if self.player.collides_with(self.enemy):
            self.game_state.health -= 1
            self.switch_scene('game_over')
```

### Rendering Backend (TBD)

**Options Under Consideration:**
- **Pygame 2.x** (OpenGL support, well-documented, large community)
- **Pyglet** (Pure OpenGL, lighter weight, good performance)
- **Arcade** (Built on Pyglet, higher-level API, excellent for 2D)

**Selection Criteria:**
- Performance (60 FPS for complex scenes)
- Ease of distribution (bundling, cross-platform)
- API simplicity (matches our accessible philosophy)
- Community/documentation
- OpenGL support for future features

**Decision**: To be made during prototyping phase

### Project Structure

```
MyGame/
├── project.json              # Game configuration
├── scenes/                   # Scene Python files
│   ├── __init__.py
│   ├── main_menu.py
│   ├── level_1.py
│   └── level_2.py
├── sprites/                  # Sprite images
│   ├── player/
│   │   ├── idle.png
│   │   └── run_sheet.png
│   └── enemies/
├── tilemaps/                 # Level data (Tiled format)
│   └── level1.tmx
├── audio/
│   ├── music/
│   └── sfx/
├── scripts/                  # Shared Python code
│   ├── player_controller.py
│   └── enemy_ai.py
└── builds/                   # Distribution outputs
```

---

## Core Systems (MVP Scope)

### 1. Scene Management
- **Scene Loading**: Load/unload scenes dynamically
- **Scene Transitions**: Fade, slide, instant
- **Scene Stack**: Support for overlays (pause menus, dialogs)
- **Persistent State**: game_state carries across scenes

### 2. Sprite System
- **Sprite Loading**: Load images, sprite sheets
- **Transform**: Position, rotation, scale
- **Rendering**: Layer support, z-ordering
- **Animation**: Frame-based animation from sprite sheets
- **Collision**: AABB, circle, pixel-perfect options

### 3. Input Handling
- **Keyboard**: Key press, hold, release
- **Mouse**: Click, position, drag
- **Gamepad**: Basic support (stretch goal)
- **Input Mapping**: Customizable key bindings

### 4. Camera System
- **Follow**: Auto-follow target (player)
- **Bounds**: Constrain to level boundaries
- **Zoom**: Dynamic zoom in/out
- **Shake**: Screen shake effects
- **Manual Control**: Direct position control

### 5. Physics (Optional Per-Scene)
- **Gravity**: Configurable strength
- **Velocity**: Movement with acceleration
- **Collision Response**: Bounce, slide, stop
- **Ground Detection**: For platformer mechanics
- **Presets**: "platformer", "topdown", "spaceship"

### 6. Audio System
- **Music**: Background music with looping
- **SFX**: Sound effects with volume/pitch control
- **Channels**: Multiple simultaneous sounds
- **Fade**: Fade in/out transitions

### 7. Tilemap Support
- **Tiled Integration**: Import .tmx files
- **Layer Rendering**: Background, foreground, collision layers
- **Object Layers**: Spawn points, triggers from Tiled
- **Tile Properties**: Custom properties for game logic

---

## Visual Editor (IDE Integration)

### Scene Editor Interface

```
┌─────────────────────────────────────────────────────────────────┐
│ Scene: level_1.py                          [▶ Play] [⏹ Stop]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Canvas (Visual)          │  Code (Python)                      │
│  ┌──────────────────────┐ │                                     │
│  │                      │ │  class Level1(Scene):               │
│  │  [Grid/Visual View]  │ │      def setup(self):               │
│  │  [Drag sprites here] │ │          self.player = ...          │
│  │  [Click to select]   │ │                                     │
│  │                      │ │      def update(self, dt):          │
│  │                      │ │          if self.input.key('right'):│
│  └──────────────────────┘ │              self.player.x += 5     │
│                            │                                     │
├────────────────────────────┴─────────────────────────────────────┤
│ Assets        │ Sprite Inspector    │ Scene Hierarchy           │
├───────────────┼────────────────────┼───────────────────────────┤
│ Sprites       │ Selected: player   │ - Background              │
│  📁 player    │ Position: (100,100)│ - Player                  │
│  📁 enemies   │ Size: (32, 32)     │ - Enemies                 │
│  📄 coin.png  │ ☑ Collision        │   - Guard1                │
│               │ ☑ Physics          │   - Guard2                │
│ Tilemaps      │ Layer: 1           │ - Items                   │
│  📄 level1    │ Animation: idle    │   - Coin1                 │
│               │                    │   - Coin2                 │
└───────────────┴────────────────────┴───────────────────────────┘
```

### Editor Features

**Canvas View:**
- Visual scene preview with grid
- Drag-and-drop sprite placement
- Multi-select and transform tools
- Snap to grid option
- Zoom/pan controls

**Code Synchronization:**
- Visual changes update Python code
- Code changes update visual view
- Two-way binding (bidirectional sync)

**Asset Management:**
- Thumbnail previews
- Drag from asset panel to canvas
- Auto-import on file drop
- Sprite sheet splitter tool

**Live Preview:**
- Play scene directly in editor
- Hot-reload on code changes
- Debug overlay (FPS, collision boxes, etc.)

---

## Built-In Systems & Helpers

### Smart Sprite System

**Beginner-Friendly API:**
```python
# Simple sprite creation
self.player = self.add_sprite('player.png', x=100, y=100)

# Automatic movement
self.player.move_to(x=200, y=100, speed=100)

# Built-in animations
self.player.play_animation('run', loop=True)
```

**Advanced Control:**
```python
# Component-based for complex behavior
self.player.add_component(PlatformerController(
    jump_force=500,
    double_jump=True,
    wall_slide=True
))

# Custom collision response
self.player.on_collision = self.handle_player_collision

def handle_player_collision(self, other):
    if other.tag == 'enemy':
        self.take_damage(10)
    elif other.tag == 'powerup':
        self.apply_powerup(other.powerup_type)
```

### State Machine Helper

```python
class Enemy(Sprite):
    def __init__(self):
        super().__init__('enemy.png')

        # Built-in state machine
        self.states.add('idle', self.idle_state)
        self.states.add('patrol', self.patrol_state)
        self.states.add('chase', self.chase_state)
        self.states.start('idle')

    def idle_state(self, dt):
        if self.sees_player():
            self.states.switch('chase')

    def chase_state(self, dt):
        self.move_towards(self.player, speed=150)
```

### Physics Presets

```python
# One-line physics configuration
self.player.apply_physics('platformer')
# Includes: gravity, jump, ground detection, slope handling

self.car.apply_physics('topdown')
# Includes: friction, acceleration, rotation

self.bullet.apply_physics('projectile')
# Includes: constant velocity, lifetime, no gravity
```

### Particle System

```python
# Simple particle effects
self.emit_particles('explosion', x=100, y=100, count=50)

# Custom particle configuration
self.create_particle_emitter(
    texture='particle.png',
    rate=10,  # Particles per second
    lifetime=2.0,
    velocity_range=(50, 150),
    direction_range=(0, 360),
    color_fade=(255,255,255) -> (255,0,0)
)
```

---

## Game State Management (Reuse from v1)

The v1 state management system works well and can be adapted:

```python
# Global game state (persistent across scenes)
game_state = {
    'player_name': 'Hero',
    'health': 100,
    'max_health': 100,
    'inventory': [],
    'current_level': 1,
    'score': 0,
}

# Access in any scene
class Level1(Scene):
    def update(self, dt):
        if self.game_state.health <= 0:
            self.switch_scene('game_over')
```

**Reusable from v1:**
- State serialization (JSON)
- Save/load system (with metadata)
- Object restoration (custom classes)
- Browser/server storage modes

---

## Distribution & Build System (Leverage v1)

**Reuse from v1:**
- Asset packer (obfuscated game.dat)
- One-click build system
- ScribePlayer architecture (universal runtime)
- Update checker system
- Version management

**Adaptations for v2:**
- Include rendering library in player bundle
- Larger ScribePlayer (~250-300MB due to pygame/pyglet)
- Same encryption/obfuscation for assets
- Scene files bundled like passage files

**Distribution Targets:**
- Desktop (Windows, Linux, macOS) - Day 1
- Web (Pygbag or similar) - Phase 2
- Mobile (Android/iOS) - Future consideration

---

## Example Game Types

### Achievable with MVP:

**Platformer:**
- Side-scrolling levels
- Jump mechanics
- Enemy AI (patrol, chase)
- Collectibles
- Simple combat

**Top-Down Adventure:**
- 8-directional movement
- Room-based exploration
- NPC interactions
- Inventory system
- Puzzle mechanics

**Puzzle Game:**
- Grid-based gameplay
- Object manipulation
- Win/lose conditions
- Level progression

### Achievable with Advanced Features:

**Action RPG:**
- Stats and leveling
- Equipment system
- Quest tracking
- Multiple abilities
- Save/load progression

**Metroidvania:**
- Interconnected world
- Ability-gated progression
- Map system
- Upgrades and unlocks

**Open-World 2D RPG:**
- Large tiled maps
- Dynamic world state
- Multiple NPCs
- Quest systems
- Crafting/trading

---

## Development Phases

### Phase 1: Core Engine (Prototype/MVP)
**Goal**: Prove the concept works

- [ ] Select rendering backend (Pygame/Pyglet/Arcade)
- [ ] Implement Scene base class
- [ ] Sprite loading and rendering
- [ ] Basic input handling
- [ ] Scene transitions
- [ ] Simple collision detection
- [ ] Game loop with fixed timestep
- [ ] Asset loading system
- [ ] Demo: Simple platformer prototype

**Success Criteria**: Can create a playable platformer level with sprites, collision, and input

### Phase 2: Visual Editor Integration
**Goal**: Web IDE for scene creation

- [ ] Extend existing Scribe Engine IDE
- [ ] Canvas view for sprite placement
- [ ] Drag-and-drop scene building
- [ ] Property inspector
- [ ] Live scene preview/testing
- [ ] Code ↔ Visual synchronization
- [ ] Asset manager integration

**Success Criteria**: Can create a scene visually without writing code, then enhance with Python

### Phase 3: Advanced Systems
**Goal**: Production-ready features

- [ ] Animation system (sprite sheets)
- [ ] Tilemap support (Tiled integration)
- [ ] Camera system (follow, zoom, shake)
- [ ] Physics presets
- [ ] Particle system
- [ ] Audio management
- [ ] State machine helpers
- [ ] Save/load adaptation from v1

**Success Criteria**: Can create a polished game demo (e.g., small Metroidvania)

### Phase 4: Distribution & Polish
**Goal**: Ship-ready engine

- [ ] Build system integration
- [ ] One-click distribution
- [ ] Template projects (platformer, puzzle, RPG)
- [ ] Comprehensive documentation
- [ ] Tutorial series
- [ ] Community assets/behaviors library

**Success Criteria**: External user can create and distribute a complete game

---

## Code Reuse from v1

### Directly Reusable:
✅ **Asset Packer** (`engine/asset_packer.py`)
✅ **Build System** (`build_player.py`, `build_engine.py`)
✅ **Storage System** (`engine/storage.py`, `engine/browser_storage.py`)
✅ **State Management** (`engine/state.py`)
✅ **Update Checker** (`update_checker.py`)
✅ **Version Management** (`version_info.py`)
✅ **Config Manager** (`config_manager.py`)
✅ **Loading Window** (`loading_window.py`)

### Adaptable with Modifications:
🔄 **Game Server** - Needs scene rendering instead of passage rendering
🔄 **Web Layer** - Different templates, same HTMX approach
🔄 **Executor** - Scene update() instead of passage code blocks

### Not Applicable:
❌ **Parser** - Scenes are Python classes, not .tgame files
❌ **Passage System** - Replaced by Scene system

**Estimated Code Reuse**: ~40-50% of v1 codebase directly applicable

---

## Open Questions & Decisions Needed

### Technical Decisions:
1. **Rendering Backend**: Pygame 2.x vs Pyglet vs Arcade library?
   - Prototype with all three to evaluate?
   - Performance benchmarks needed

2. **Tilemap Format**: Tiled (.tmx) or custom format?
   - Tiled is industry standard, good tools
   - Adds dependency but worth it?

3. **Physics Engine**: Built-in simple physics or integrate library (Pymunk)?
   - Simple: Easier, lighter, limited
   - Pymunk: Complex, more realistic, heavier

4. **Scene File Format**: Pure Python or custom format that generates Python?
   - Pure Python: Transparent, flexible
   - Custom format: More beginner-friendly?

5. **Web IDE Architecture**: Extend v1 IDE or separate app?
   - Extend: Code reuse, unified experience
   - Separate: Cleaner separation, different needs

### Design Decisions:
1. **Visual Editor Scope**: How much can be done without code?
   - 80/20 rule: 80% visual, 20% code for advanced features?

2. **Template Projects**: Which game types to prioritize?
   - Platformer, top-down adventure, puzzle game?

3. **Beginner Path**: Tutorial structure?
   - Interactive tutorial game?
   - Video series?
   - Documentation-first?

4. **Advanced Features**: What's in v2.0 vs v2.x?
   - Multiplayer?
   - Advanced shaders?
   - Dialogue system (bridge to v1)?

---

## Success Metrics

### For MVP:
- [ ] Can create a playable platformer in < 1 hour (for experienced user)
- [ ] Generated Python code is readable and modifiable
- [ ] 60 FPS performance with 100+ sprites on screen
- [ ] One-click build produces working executable

### For v2.0 Release:
- [ ] 3 complete template projects
- [ ] Full documentation coverage
- [ ] 10+ community-created games
- [ ] Build time < 30 seconds for typical game
- [ ] Cross-platform builds (Windows, Linux, macOS)

---

## Next Steps

1. **Prototype Rendering Backends** (Week 1-2)
   - Create simple demos with Pygame, Pyglet, Arcade
   - Benchmark performance
   - Evaluate API ergonomics
   - Make selection

2. **Design Scene API** (Week 2-3)
   - Define Scene base class
   - Design sprite/collision API
   - Create example scenes
   - Validate against use cases

3. **Build Core Engine** (Week 3-6)
   - Implement scene management
   - Sprite system
   - Input handling
   - Basic collision
   - Create platformer demo

4. **Document & Iterate** (Ongoing)
   - Update this vision document
   - Document API decisions
   - Create dev blog/changelog
   - Gather feedback

---

## Resources & References

### Inspiration:
- **Pygame**: Python game development baseline
- **LÖVE**: Lua-based 2D engine (excellent API design)
- **Phaser**: JavaScript 2D engine (web-based workflow)
- **GDevelop**: Visual + code approach
- **Ren'Py**: Python-based, accessible (our v1 peer)

### Technical References:
- **Game Programming Patterns** (Robert Nystrom)
- **Pygame Documentation**: https://www.pygame.org/docs/
- **Pyglet Documentation**: https://pyglet.readthedocs.io/
- **Arcade Documentation**: https://api.arcade.academy/
- **Tiled Documentation**: https://doc.mapeditor.org/

---

## Community & Feedback

This is a living document. As prototyping progresses, decisions will be documented here.

**Discussion Topics:**
- Rendering backend selection
- Scene API design
- Visual editor capabilities
- Template project ideas

**Feedback Channels:**
- GitHub Issues (for v2-development branch)
- Community Discord (future)
- Development blog (future)

---

**Last Updated**: 2025-09-30
**Current Phase**: Planning → Prototyping
**Next Milestone**: Rendering backend selection
