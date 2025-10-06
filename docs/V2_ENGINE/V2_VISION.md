# Scribe Engine V2 - Vision & Design Philosophy

**Last Updated**: 2025-10-04
**Status**: Living Document - Source of Truth for Design Direction
**Branch**: `v2-native-editor-poc`

---

## Mission Statement

Create an **approachable 2D game engine** that abstracts Pygame complexity into intuitive visual tooling while remaining powerful enough for advanced developers. The engine should enable rapid game creation through a component-based architecture and professional IDE workflow.

---

## Core Design Principles

### 1. **Approachable for Beginners**
- **Visual-First Workflow**: Drag-drop sprites, point-click editing
- **Game-Friendly Terminology**: Use "Behavior" instead of "Component", "Entity" instead of "GameObject"
- **Clean, Modern UI**: Thoughtful tool placement, clear visual hierarchy
- **Discoverable Features**: Everything visible in the interface, no hidden shortcuts required
- **Contextual Help**: Inline tooltips and documentation

### 2. **Powerful for Advanced Users**
- **Component-Based Architecture**: Composition over inheritance
- **Custom Component Creation**: Full Python scripting access when needed
- **Component Inheritance/Templates**: Reusable entity templates (prefabs)
- **Direct Code Editing**: Code editor alongside visual tools
- **Extensibility**: Modify engine behavior without fighting the system

### 3. **Professional Workflow**
- **Fast Iteration Cycles**: Live preview, hot-reload scripts
- **Keyboard Shortcuts**: Power-user efficiency
- **Undo/Redo Throughout**: Non-destructive editing
- **Asset Management Built-In**: Visual asset browser and organization
- **One-Click Build & Test**: Instant playable builds

---

## Architecture Philosophy

### Component-Based Design

**Composition over Inheritance**: Instead of creating objects that *are* things (e.g., `Player` class inheriting from `PhysicsObject`), you create simple objects and *give them* behaviors by attaching components.

**Hierarchy**:
```
Game (master controller)
  └── Scene (container for game objects)
      └── Sprite (entity with transform)
          └── Component (modular behavior)
```

**Example Entity Construction**:
- Create blank Sprite
- Add RigidBody component → gives physics
- Add BoxCollider component → enables collision
- Add PlatformerController component → adds player input
- Result: Functional player character, zero custom classes needed

---

## Critical Features Roadmap

### Phase 1: Foundation (Current)

**P1.1: Game State System** ✅ **COMPLETE**
- Global state management
- Persistent entities across scenes
- Spawn point system
- Scene transition state preservation

**P1.2: Save/Load System** 🔄 **IN PROGRESS**
- Pygame-based save menu (runtime UI overlay)
- 6-slot save system with metadata display
- Component serialization/deserialization
- Quick save/load keyboard shortcuts (Ctrl+F5/F9)
- Game pause/unpause integration
- Export/import save files
- SaveData base class system (Python dataclasses)
- SaveData Designer visual tool (after editor UI overhaul)

**P1.3: Behavior/Template System** ⏳ **PLANNED**
- Component metadata (categories, descriptions, icons)
- Template/Prefab system (save sprite + components as reusable templates)
- Behavior library panel with search/filter
- Drag-drop template instantiation

**P1.4: Script Integration** ⏳ **PLANNED**
- Attach custom Python scripts to sprites (Godot-style)
- Hot-reload script changes without restart
- Split view: code editor + scene view
- Script templates for common patterns

**P1.5: Custom Tools - Dialogue System** ⏳ **PLANNED**
- Node-based dialogue tree editor
- Visual conversation flow creation
- Variable substitution and conditional branches
- Runtime dialogue manager integration

---

### Phase 2: Essential Systems

**Animation System**
- Sprite sheet importer (grid-based slicing)
- Animation editor (frame sequences, timing)
- Animation state machine (idle → walk → jump transitions)
- Animator component with visual state graph

**Audio System**
- Audio asset browser (music, SFX)
- AudioSource component (positional audio support)
- Audio mixer (volume, ducking, effects)
- Music playlist/crossfade system

**UI System**
- UI canvas system (screen-space overlay)
- UI components (Button, Text, Image, Panel, ProgressBar)
- Layout groups (horizontal, vertical, grid)
- UI editor mode (separate from gameplay viewport)
- Event system (onClick, onHover)

**Tilemap System**
- Tiled (.tmx) import support
- Built-in tilemap editor (paint tiles like Tiled)
- Automatic collision from tilemap layers
- Tileset management
- Multiple layers (background, collision, foreground)

---

### Phase 3: Advanced Features

**Particle System**
- Particle emitter component
- Visual particle editor with real-time preview
- Presets (fire, smoke, sparkles, rain)
- Custom particle sprites

**Visual Scripting OR Enhanced Python Workflow**
- Node-based behavior editor (optional)
- Advanced Python editor integration
- Debugger with breakpoints
- Variable inspection

**Advanced Game State Management**
- Visual variable inspector
- Data binding (UI shows game variables)
- Quest/flag management system

---

## IDE Vision

### Launcher & Project Creation

**Welcome Screen**:
- New Project (prominent)
- Open Existing Project
- Browse Example Projects
- Recent projects list
- Tutorials/Documentation links

**New Project Wizard**:
1. **Template Selection** (visual cards with previews):
   - Blank Project (empty scene)
   - Platformer Starter (player, platforms, example level)
   - Top-Down RPG (character, tilemap, basic movement)
   - Puzzle Game (grid system, example mechanics)

2. **Project Settings**:
   - Project name
   - Location (file browser)
   - Resolution presets (720p, 1080p, custom)
   - Target platform (Desktop, Web, Both)

3. **Create & Open**:
   - Progress indicator
   - Auto-open in editor when complete

---

### Editor Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ [Logo] File Edit Scene GameObject Component Build  [Play ▶] [?] │ ← Simplified menu
├─────────┬───────────────────────────────────────┬───────────────┤
│ PROJECT │         VIEWPORT                      │  INSPECTOR    │
│         │                                       │               │
│ Scenes  │  ┌─────────────────────────────────┐ │ [Sprite Name] │
│  ├ Main │  │                                 │ │               │
│  └ Level│  │     [Game View]                 │ │ Transform:    │
│         │  │                                 │ │  Position X:  │
│ Assets  │  │                                 │ │  Position Y:  │
│  ├ Spr..│  │                                 │ │               │
│  ├ Snd..│  │                                 │ │ Components:   │
│  └ Mus..│  └─────────────────────────────────┘ │  + Add        │
│         │  [Tools: Select Move Rotate Scale]  │               │
│ Prefabs │                                       │               │
│  + New  │  Scene: Main         FPS: 60         │               │
├─────────┴───────────────────────────────────────┴───────────────┤
│ CONSOLE                                         [Clear] [Filter]│
│ [Game] Initialized...                                           │
│ [SceneManager] Loaded scene: main                               │
└─────────────────────────────────────────────────────────────────┘
```

**Key Areas**:
- **Top Toolbar**: Simplified, icon-based, big Play button, help access
- **Left Panel**: Unified project browser (scenes, assets, prefabs)
- **Center Viewport**: Game view with tool palette
- **Right Panel**: Inspector (component editor)
- **Bottom Console**: Collapsible debug output

---

### Component Inspector Vision

**Inspector Panel** (when sprite selected):
```
Selected: Player

Transform
  Position: (100, 200)
  Rotation: 0°
  Scale: (1.0, 1.0)

Components:
┌─────────────────────────┐
│ ⚙️ RigidBody         [×]│
│  Mass: 1.0              │
│  Gravity Scale: 1.0     │
│  Is Kinematic: □        │
└─────────────────────────┘
┌─────────────────────────┐
│ 📦 BoxCollider       [×]│
│  Width: 32              │
│  Height: 32             │
│  Is Trigger: □          │
└─────────────────────────┘
┌─────────────────────────┐
│ 🎮 PlatformerController [×]│
│  Speed: 300             │
│  Jump Force: 500        │
│  Double Jump: ☑         │
└─────────────────────────┘

[+ Add Component ▼]
```

**Features**:
- Component headers with icons (visual recognition)
- Collapsible sections
- Color-coded by type (physics=orange, rendering=blue, gameplay=green)
- Inline value sliders (not just text input)
- Visual property editors (color picker, sprite preview, etc.)
- Help icon (?) next to properties (tooltip on hover)

---

### Behavior Browser Vision

**Concept**: Modern, visual browser for discovering and adding behaviors to sprites. Replaces traditional dropdown menus with an intuitive, filterable card-based interface.

**Triggered by**: Clicking [+ Add Behavior] button in Inspector panel

**Interface Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│ Add Behavior                           [Behaviors] [Templates] [×]│
├─────────────────────────────────────────────────────────────────┤
│ [🔍 Search...]                                                   │
│                                                                  │
│ Filters: [Physics] [Rendering] [Gameplay] [AI] [Audio] [Custom] │
│          ^^^^^^^^   ^^^^^^^^^^  ^^^^^^^^^  ^^^^  ^^^^^^^  ^^^^^^ │
│          Orange     Blue        Green      Purple Yellow  Gray   │
│          (active pills with colored text, transparent background)│
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ ⚙️ RigidBody  │  │ 📦 BoxCollider│  │ 🎮 Platformer│          │
│  │              │  │              │  │  Controller  │          │
│  │ Physics      │  │ Physics      │  │ Gameplay     │          │
│  │ simulation   │  │ AABB         │  │ Player       │          │
│  │ with gravity │  │ collision    │  │ movement     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 📷 Camera    │  │ 🎯 Scene     │  │ 💚 Health    │          │
│  │  Follow      │  │  Trigger     │  │  System      │          │
│  │              │  │              │  │              │          │
│  │ Gameplay     │  │ Gameplay     │  │ Gameplay     │          │
│  │ Smooth       │  │ Level        │  │ Damage &     │          │
│  │ tracking     │  │ transitions  │  │ death        │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐                             │
│  │ 🔊 Audio     │  │ ⭐ My Custom │                             │
│  │  Source      │  │  Behavior    │                             │
│  │              │  │              │                             │
│  │ Audio        │  │ Custom       │  ← User-created behaviors  │
│  │ Playback     │  │ Project      │                             │
│  │ & effects    │  │ specific     │                             │
│  └──────────────┘  └──────────────┘                             │
│                                                                  │
│                                                [Cancel] [Add]    │
└─────────────────────────────────────────────────────────────────┘
```

**Templates Tab**:
```
┌─────────────────────────────────────────────────────────────────┐
│ Add Behavior                           [Behaviors] [Templates] [×]│
├─────────────────────────────────────────────────────────────────┤
│ [🔍 Search templates...]                                         │
│                                                                  │
│ Quick-start entity configurations with common behavior sets      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────┐  ┌──────────────────────────┐     │
│  │ 🎮 Platformer Player     │  │ 👾 Flying Enemy          │     │
│  │                          │  │                          │     │
│  │ • PlatformerController   │  │ • FlyingMovement         │     │
│  │ • RigidBody              │  │ • ChasePlayer (AI)       │     │
│  │ • BoxCollider            │  │ • Health                 │     │
│  │ • CameraFollow           │  │ • ContactDamage          │     │
│  │ • Health                 │  │ • Sprite Animator        │     │
│  │                          │  │                          │     │
│  │         [Add Template]   │  │         [Add Template]   │     │
│  └──────────────────────────┘  └──────────────────────────┘     │
│                                                                  │
│  ┌──────────────────────────┐  ┌──────────────────────────┐     │
│  │ 🚪 Scene Transition      │  │ 💰 Collectible Item      │     │
│  │                          │  │                          │     │
│  │ • BoxCollider (trigger)  │  │ • Collectible            │     │
│  │ • SceneTrigger           │  │ • SpinAnimation          │     │
│  │                          │  │ • AudioOnPickup          │     │
│  │                          │  │ • ParticleEffect         │     │
│  │                          │  │                          │     │
│  │         [Add Template]   │  │         [Add Template]   │     │
│  └──────────────────────────┘  └──────────────────────────┘     │
│                                                                  │
│  ┌──────────────────────────┐  ┌──────────────────────────┐     │
│  │ 💬 Interactive NPC       │  │ ⭐ My Custom Template    │     │
│  │                          │  │                          │     │
│  │ • DialogueComponent      │  │ • CustomBehavior1        │     │
│  │ • InteractionTrigger     │  │ • CustomBehavior2        │  ← User-saved │
│  │ • SpriteAnimator         │  │ • RigidBody              │  templates   │
│  │ • AudioSource            │  │                          │     │
│  │                          │  │                          │     │
│  │         [Add Template]   │  │         [Add Template]   │     │
│  └──────────────────────────┘  └──────────────────────────┘     │
│                                                                  │
│                                                [Cancel]          │
└─────────────────────────────────────────────────────────────────┘
```

**Features**:

**Behaviors Tab**:
- **Card Grid Layout**: Visual cards instead of dropdown list
- **Category Color Coding**: Physics (Orange), Rendering (Blue), Gameplay (Green), AI (Purple), Audio (Yellow), Custom (Gray)
- **Pill-Shaped Filters**: Clickable category buttons at top
  - Active: Colored text, transparent background, pill border
  - Inactive (excluded): Greyed out with reduced opacity
  - Click to toggle category visibility
- **Search Bar**: Real-time filtering by behavior name/description
- **Card Content**: Icon, name, category badge, short description
- **Hover Preview**: Expanded description and property list
- **Custom Behaviors**: User-created behaviors appear with "Custom" badge

**Templates Tab**:
- **Template Cards**: Larger cards showing behavior bundles
- **Behavior List**: Shows all behaviors included in template
- **One-Click Add**: Adds all behaviors at once
- **Built-in Templates**: Engine-provided common configurations
- **User Templates**: Developers can save current sprite's behavior set as custom template
- **Template Management**: Right-click to edit/delete custom templates

**Discoverability Benefits**:
- New users can **browse** to learn what's available
- Visual layout is more approachable than text lists
- Category filters help narrow down relevant behaviors
- Templates provide starting points for common entity types
- Custom behaviors/templates encourage project-specific reusability

**Technical Implementation**:
- Behaviors registered with metadata (name, description, category, icon)
- Templates stored as JSON (list of behavior names + default property values)
- User templates saved to `project/templates/` directory
- Custom behaviors auto-discovered from `project/behaviors/` directory
- Browser is a modal dialog (PyQt6 QDialog) with card widgets

---

## Custom Tool Concepts

### 0. SaveData Designer (P1.2)

**Vision**: Visual tool for designing game save data structures

**Purpose**: Help developers define what data should be saved without writing serialization code

**Interface**:
```
┌────────────────────────────────────────────────────┐
│ SaveData Designer - PlayerSaveData                 │
├────────────────────────────────────────────────────┤
│ [Add Field] [Generate Code] [Preview]             │
├─────────────┬──────────────────────────────────────┤
│ Fields      │  Preview                             │
│             │                                      │
│ + health    │  @dataclass                          │
│   int       │  class PlayerSaveData(SaveData):     │
│   default:  │      health: int = 100               │
│   [100]     │      max_health: int = 100           │
│             │      position: Vector2 = Vector2()   │
│ + max_health│      inventory: List[str] = []       │
│   int       │                                      │
│   default:  │      def to_dict(self) -> dict:      │
│   [100]     │          return asdict(self)         │
│             │                                      │
│ + position  │      @classmethod                    │
│   Vector2   │      def from_dict(cls, data):       │
│   default:  │          return cls(**data)          │
│   [0, 0]    │                                      │
│             │                                      │
│ + inventory │  [Copy Code] [Save to File]          │
│   List[str] │                                      │
│   default:  │                                      │
│   [[]]      │                                      │
└─────────────┴──────────────────────────────────────┘
```

**Features**:
- Visual field editor (add/remove/reorder fields)
- Type selection dropdown (int, float, str, bool, Vector2, List, Dict)
- Default value configuration
- Auto-generates Python dataclass code
- Preview pane shows generated code
- One-click copy or save to project file
- Validation (ensures SaveData base class compliance)

**Technical Approach**:
- Python dataclasses as base system (not custom Resource classes)
- SaveData base class provides to_dict/from_dict
- Generated classes automatically work with GameState serialization
- No manual serialization code needed by developers

**Benefits**:
- Beginner-friendly (no boilerplate code)
- Type-safe (uses Python type hints)
- Auto-complete friendly (real Python classes)
- Extensible (advanced users can edit generated code)

---

### 1. Dialogue Tool

**Vision**: Visual node-based dialogue tree editor

**Interface**:
```
┌─────────────────────────────────────────────┐
│ Dialogue Editor - NPC_Merchant              │
├─────────────────────────────────────────────┤
│ [Save] [Test] [Export]                      │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────┐                            │
│  │   START     │                            │
│  └──────┬──────┘                            │
│         │                                   │
│  ┌──────▼──────────────┐                    │
│  │ "Hello traveler!"   │                    │
│  │ [NPC speaks]        │                    │
│  └──────┬──────────────┘                    │
│         │                                   │
│    ┌────┴────┐                              │
│    │         │                              │
│ ┌──▼──┐   ┌─▼──┐                            │
│ │Buy  │   │Leave│                           │
│ └──┬──┘   └────┘                            │
│    │                                        │
│ ┌──▼─────────────┐                          │
│ │ [Check: Gold]  │                          │
│ │ if gold >= 100 │                          │
│ └────┬────┬──────┘                          │
│      │    │                                 │
│   [Yes] [No]                                │
```

**Features**:
- Node types: NPC speech, player choice, conditional, action
- Bezier curve connections
- Inline conditions (check inventory, flags, stats)
- Actions (give item, set flag, start quest)
- Variable insertion `{player.name}` in text
- Preview/test mode

---

### 2. UI Builder

**Vision**: WYSIWYG editor for in-game UI

**Interface**:
```
┌──────────────────────────────────────────────────────┐
│ UI Canvas Editor - MainHUD                           │
├──────────────────────────────────────────────────────┤
│ [Elements] [Layouts] [Preview]                       │
├─────────────┬────────────────────────┬───────────────┤
│ UI Elements │  [1280x720 Canvas]     │  Properties   │
│             │                        │               │
│ Text        │  ┌─────────────────┐   │  Text:        │
│ Image       │  │ HP: 100/100     │   │  "HP: {hp}"   │
│ Button      │  └─────────────────┘   │               │
│ ProgressBar │                        │  Font: Arial  │
│ Panel       │        ╔═══════╗       │  Size: 24     │
│ Slider      │        ║       ║       │  Color: #FFF  │
│             │        ║ PLAY  ║       │               │
│ Drag →      │        ╚═══════╝       │  Anchor:      │
│             │                        │  [Top-Left ▼] │
│             │  ▓▓▓▓▓▓▓▓░░░░░░        │               │
│             │  [Progress Bar]        │  Data Binding:│
│             │                        │  player.hp    │
└─────────────┴────────────────────────┴───────────────┘
```

**Features**:
- Drag UI elements onto canvas
- Anchor system (top-left, center, bottom-right, etc.)
- Layout groups (auto-arrange children)
- Data binding (`{player.hp}` updates in real-time)
- Preview mode (test different resolutions)
- Event binding (button → pause game)

---

### 3. Split Scene/Code View

**Vision**: Code editor attached to selected entity (Godot-inspired)

**Interface**:
```
┌────────────────────────────────────────────────────────────┐
│ Scene View                                                 │
├──────────────────┬─────────────────────────────────────────┤
│ Hierarchy        │  Viewport                               │
│                  │                                         │
│ ├─ Player ◄──────┼─  [Selected: Player sprite]            │
│ │  └─ Scripts    │                                         │
│ │     └─ player..│                                         │
│ ├─ Enemy         │                                         │
│ └─ Platform      │                                         │
├──────────────────┴─────────────────────────────────────────┤
│ Code Editor - player_controller.py                         │
├────────────────────────────────────────────────────────────┤
│ 1  class PlayerController(Component):                      │
│ 2      def __init__(self, sprite):                         │
│ 3          super().__init__(sprite)                        │
│ 4          self.speed = 300                                │
│ 5                                                          │
│ 6      def update(self, dt):                               │
│ 7          # Handle input                                  │
│ 8          if self.sprite.scene.input.key_held('a'):       │
│ 9              self.sprite.position.x -= self.speed * dt   │
│ 10                                                         │
│    [Save] [Run] [Debug]                                    │
└────────────────────────────────────────────────────────────┘
```

**Features**:
- Select sprite → shows attached scripts
- Click script → opens in code panel
- Auto-complete aware of sprite/scene context
- Inline documentation (hover over methods)
- Breakpoint support (click line numbers)
- Hot-reload (save → immediately updates running game)

---

## Terminology Philosophy

**Use game-familiar terms, not programmer jargon**:

| Instead of... | Use... | Why? |
|---------------|--------|------|
| GameObject | **Sprite** or **Entity** | "GameObject" feels Unity-specific |
| Component | **Behavior** | More intuitive ("what does it do?") |
| Prefab | **Template** | Clearer for beginners |
| Transform | **Position/Rotation/Scale** | Don't hide behind technical term |
| Rigidbody | **Physics Behavior** | Descriptive, not jargon |

**In UI**:
- Inspector panel → **Properties** panel
- Hierarchy → **Scene Objects** or **Objects**
- Add Component button → **Add Behavior**

**Progressive Disclosure**: Advanced users can toggle "Show Technical Names" in preferences

---

## Genre-Specific Features

### Top-Down RPG Needs
- Pathfinding (NPCs navigate around obstacles)
- Dialogue System (conversation trees, choice branches)
- Inventory System (item management, equipment slots)
- Quest System (objectives, tracking, rewards)
- Turn-Based Combat (if applicable)

### Side-Scroller Adventure Needs
- Checkpoints (respawn points)
- Moving Platforms (waypoint-based movement)
- Ladders/Ropes (climbable surfaces)
- Water/Swimming (physics zones)
- Cutscene System (camera control, scripted events)

### Puzzle Game Needs
- Grid System (snap-to-grid movement)
- Undo/Redo for Moves (gameplay undo, not just editor)
- Win Condition System (level complete detection)
- Level Select (progression, unlocking)

---

## Open Design Questions

### 1. Visual Scripting vs. Python-First?
- **Option A**: Build node-graph system (Unreal Blueprints style)
- **Option B**: Embrace Python with better editor integration (autocomplete, debugging)
- **Option C**: Both (visual generates Python)

### 2. Web Export Priority?
- How important is "Play in Browser" vs. desktop-only?
- Pygame → Pygbag for web export (is this viable?)

### 3. 3D Support in Future?
- Keep it 2D forever?
- Or plan architecture for eventual 2.5D/3D?

### 4. Target Audience Clarity?
- Hobbyists making first game?
- Educators teaching game dev?
- Indie studios prototyping?
- All of the above?

### 5. Component Marketplace?
- Should users be able to share/sell components?
- Built-in asset store?

---

## Success Metrics

### MVP Success (Phase 1 Complete)
- ✅ Multi-scene games with persistent player state
- ✅ Reusable entity templates (prefabs)
- ✅ Custom behaviors via Python scripts
- ✅ Dialogue system without coding
- ✅ Professional save/load system
- ✅ One-click build to executable

### Production Ready
- Can build complete platformer game in under 1 hour
- Can build top-down RPG with dialogue/quests in under 3 hours
- Can build puzzle game with custom mechanics in under 2 hours
- 60+ FPS with 100+ sprites on screen
- Comprehensive documentation and tutorials
- Example games demonstrating all features

---

## Architecture Requirements for Tools

To support the vision, we need:

### 1. Plugin/Tool API
- Tools register with editor
- Access to scene data
- Can spawn windows/panels
- Event system (onSpriteSelected, onSceneSaved)

### 2. Data Formats
- `.template` files (JSON sprite + component configurations)
- `.dialogue` files (JSON dialogue trees)
- `.ui` files (UI canvas layouts)
- `.anim` files (animation data)

### 3. Component Metadata
- Behaviors need descriptions (for tooltips)
- Categories (Movement, Combat, AI, Interaction)
- Icons (visual recognition)
- Example usage snippets

### 4. Hot-Reload System
- File watcher for scripts
- Module reloading without restart
- State preservation during reload

### 5. Data Binding System
- UI elements → game variables
- Two-way binding (game changes → UI updates)
- Expression evaluation (`{player.hp}/{player.max_hp}`)

---

## Development Philosophy

### Core Tenets

1. **Components are First-Class Citizens**: Everything visible in inspector
2. **Inspector Drives Everything**: If it's not in inspector, it doesn't exist to users
3. **No Code Required for Basics**: Physics, collision, triggers should be visual
4. **Code is for Advanced Users**: Custom components, complex logic
5. **Templates Enable Reuse**: Don't make users rebuild same sprite 20 times
6. **Visual-First, Code When Needed**: Start with visual tools, drop to code for power

### Design Patterns

- **Composition over Inheritance**: Use components, not class hierarchies
- **Data-Driven Design**: Game content in JSON, not hard-coded
- **Immediate Feedback**: Live preview, instant updates
- **Discoverability**: Browse components to learn what's possible
- **Progressive Complexity**: Simple by default, powerful when needed

---

*This vision document is the source of truth for design direction. Implementation status is tracked separately in V2_DEVELOPMENT_STATUS.md*
