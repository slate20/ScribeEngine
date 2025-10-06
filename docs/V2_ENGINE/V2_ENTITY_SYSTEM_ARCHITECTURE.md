# V2 Entity System Architecture

**Created**: 2025-10-05
**Status**: Design Document - For Discussion & Approval
**Purpose**: Define entity hierarchy, behavior organization, script integration, and editor workflow

---

## 1. Core Concepts (Aligned with V2_VISION.md)

### Entity Hierarchy

```
Game (master controller)
  └── Scene (container for game objects)
      ├── Sprite Object (entity with transform + visual representation)
      │   └── Behavior/Component (modular functionality)
      │         ├── Built-in behaviors (provided by engine)
      │         └── Custom behaviors (created by user)
      └── Logic Object (entity with no visual - game logic/managers)
          └── Behavior/Component (modular functionality)
                ├── Built-in behaviors (provided by engine)
                └── Custom behaviors (created by user)
```

### Key Principles

**1. All behaviors are equal**
- Built-in behaviors (RigidBody, BoxCollider) are written using the same Component API users have access to
- Engine behaviors live in `v2_engine/components/`
- User behaviors live in `<project>/behaviors/`
- No special treatment - both use identical base class and lifecycle

**2. "We eat our own dog food"**
- Every engine-provided behavior could have been written by a user
- If we need special APIs for built-in behaviors, those APIs should be public
- This ensures the component system is powerful enough for real use cases

**3. Terminology**
- **Code/Docs**: Use "Component" (technical term, matches class name)
- **UI**: Use "Behavior" (user-friendly, more intuitive)
- **Interchangeable**: Both refer to same concept - modular functionality attached to sprites

### Definitions

**Sprite Object**: Visual entity with rendering capabilities
- Has transform (position, rotation, scale, origin)
- Has visual representation (image, color, visibility)
- Has component attachment system
- Has update/render lifecycle
- Can be persistent across scenes

**Logic Object**: Non-visual entity for game logic
- No transform or rendering (invisible)
- Used for game managers, controllers, systems
- Has component attachment system
- Has update lifecycle (no render)
- Can be persistent across scenes
- Examples: WaveSpawner, ScoreTracker, AudioManager

**Behavior/Component**: Modular functionality attached to any object (Sprite or Logic)
- Inherits from `Component` base class
- Has reference to parent object (`self.sprite` for now - will be `self.entity`)
- Has `update(dt)` lifecycle method
- Can be enabled/disabled
- Can access scene and game state through parent reference

**Template**: Behavior bundle for quick entity setup
- Saved as `.template` JSON file
- Contains ONLY: list of behaviors + their property values
- Does NOT contain: sprite transform, image, or visual properties
- Can be applied to any Sprite Object or Logic Object
- User creates by right-clicking object → "Save as Template"
- Engine provides common templates (Platformer Player, Flying Enemy, etc.)

---

## 2. Behavior System Architecture

### How Behaviors Work

**All behaviors follow the same pattern:**

```python
# v2_engine/components/rigidbody.py (Engine-provided)
from v2_engine.components.component import Component

class RigidBody(Component):
    def __init__(self, sprite):
        super().__init__(sprite)
        self.velocity = Vector2(0, 0)
        self.gravity = 980.0

    def update(self, dt):
        # Apply gravity
        self.velocity.y += self.gravity * dt
        # Update position
        self.sprite.position += self.velocity * dt
```

```python
# <project>/behaviors/enemy_patrol.py (User-created)
from v2_engine.components.component import Component

class EnemyPatrol(Component):
    def __init__(self, sprite):
        super().__init__(sprite)
        self.speed = 50
        self.distance = 200
        self.direction = 1
        self.start_x = sprite.position.x

    def update(self, dt):
        # Move back and forth
        self.sprite.position.x += self.speed * self.direction * dt

        # Reverse at patrol distance
        if abs(self.sprite.position.x - self.start_x) > self.distance:
            self.direction *= -1
```

**Both behaviors**:
- Inherit from same `Component` base class
- Have access to same `self.sprite` reference
- Use same `update(dt)` lifecycle
- Can be attached/detached identically
- Appear in Behavior Browser together

### Behavior Discovery

**Engine behaviors** (`v2_engine/components/*.py`):
- Auto-discovered on engine startup
- Registered with metadata (category, description, icon)
- Always available in Behavior Browser

**User behaviors** (`<project>/behaviors/*.py`):
- Auto-discovered when project loads
- Scanned for classes inheriting from `Component`
- Appear in Behavior Browser under "Custom" category
- Can optionally include metadata for better organization

**Metadata format** (optional for user behaviors, required for engine behaviors):
```python
class EnemyPatrol(Component):
    __metadata__ = {
        'category': 'AI',
        'icon': '🤖',
        'description': 'Patrol back and forth between two points',
        'requires': [],  # List of component types this depends on
        'conflicts': []  # List of component types this conflicts with
    }
```

---

## 3. Template System

### What Templates Are

Templates are **saved sprite configurations** - nothing more, nothing less.

**Template file structure** (`<project>/templates/platformer_player.template`):
```json
{
  "name": "Platformer Player",
  "behaviors": [
    {
      "type": "RigidBody",
      "properties": {
        "gravity": 980.0,
        "mass": 1.0
      }
    },
    {
      "type": "BoxCollider",
      "properties": {
        "width": 32,
        "height": 48
      }
    },
    {
      "type": "PlatformerController",
      "properties": {
        "move_speed": 300,
        "jump_force": -500,
        "can_double_jump": true
      }
    },
    {
      "type": "CameraFollow",
      "properties": {
        "smooth_speed": 5.0
      }
    }
  ]
}
```

### Template Workflow

**Creating templates**:
1. Configure sprite with desired behaviors
2. Right-click sprite in hierarchy → "Save as Template"
3. Enter template name → Saved to `<project>/templates/`
4. Template appears in Behavior Browser "Templates" tab

**Using templates**:
1. Click "Add Behavior" in Inspector
2. Switch to "Templates" tab
3. Click template card → Adds all behaviors with configured settings
4. User can then adjust individual behavior properties

**Built-in templates**:
- Engine provides common templates in `v2_engine/templates/`
- Platformer Player, Flying Enemy, Collectible Item, etc.
- Users can customize and save their own variations

---

## 4. Code Editor Integration (Phase 1.4)

### Editor Layout with Code Panel

**Main panel serves three purposes:**

```
┌─────────────────────────────────────────────────────────────────┐
│ [File] [Edit] [Scene] [Build]                    [▶ Play] [?]   │
├──────────┬──────────────────────────────────────┬───────────────┤
│ Hierarchy│                                      │  Properties   │
│          │                                      │               │
│ 🎮 Player│         MAIN PANEL                   │  Transform    │
│ 🎨 Enemy │                                      │  Position: .. │
│ 📦 Platf.│  ┌────────────────────────────────┐  │               │
│          │  │  [Scene View]                  │  │  Behaviors:   │
│ [+ Add]  │  │                                │  │  ☑ RigidBody  │
│          │  │                                │  │  ☑ BoxCollider│
│          │  │    Viewport renders here       │  │  📜 Custom... │
│          │  │                                │  │   [Edit Code] │
│          │  │                                │  │               │
│          │  └────────────────────────────────┘  │  [+ Add]      │
│          │                                      │               │
│          │  OR (when code editing)              │               │
│          │                                      │               │
│          │  ┌────────────────────────────────┐  │               │
│          │  │ # custom_behavior.py       [×] │  │               │
│          │  │ from v2_engine.components ...  │  │               │
│          │  │                                │  │               │
│          │  │ class CustomBehavior(Comp...): │  │               │
│          │  │     def __init__(self, spr..): │  │               │
│          │  │         super().__init__(...   │  │               │
│          │  │         self.speed = 100       │  │               │
│          │  │                                │  │               │
│          │  │     def update(self, dt):      │  │               │
│          │  │         # Move sprite           │  │               │
│          │  │         self.sprite.posit...   │  │               │
│          │  │                                │  │               │
│          │  │ [Save] [Save & Reload]         │  │               │
│          │  └────────────────────────────────┘  │               │
│          │                                      │               │
│          │  OR (split view - future)            │               │
│          │                                      │               │
│          │  ┌──────────┬──────────────────────┐ │               │
│          │  │ Scene    │  Code Editor         │ │               │
│          │  │ (50%)    │  (50%)               │ │               │
│          │  └──────────┴──────────────────────┘ │               │
├──────────┴──────────────────────────────────────┴───────────────┤
│ Console: [Game initialized] [Scene loaded: main]      [Clear]   │
└─────────────────────────────────────────────────────────────────┘
```

### View Modes

**Scene View** (default):
- Pygame viewport rendering
- Visual sprite editing with gizmos
- Click sprites to select and edit properties

**Code View** (when editing behavior):
- Code editor replaces viewport in main panel
- Triggered by "Edit Code" button in Properties panel (for custom behaviors)
- Triggered by "New Behavior" button in Behavior Browser
- Syntax highlighting, code completion
- "Save & Reload" button to hot-reload changes

**Split View** (future enhancement):
- Half viewport, half code editor side-by-side
- Live preview while editing code
- Phase 2+ feature

### Code Editor Features (Phase 1.4 MVP)

**Essential**:
- Syntax highlighting (Python)
- Line numbers
- Auto-indentation
- Code completion (keywords, `self.sprite.`, common patterns)
- "Save" and "Save & Reload" buttons
- File tabs (if editing multiple behaviors)
- Font size controls in preferences
- Search/replace

**Implementation**: QsciScintilla (preferred for code completion) or QTextEdit with syntax highlighting (fallback)

---

## 5. Behavior Browser (Aligned with V2_VISION.md)

The Behavior Browser design is **already defined in V2_VISION.md lines 263-395**. Key points:

### Two-Tab Interface

**Behaviors Tab**:
- Card-based grid layout
- Category filters (Physics, Rendering, Gameplay, AI, Audio, Custom)
- Pill-shaped filter buttons (colored, transparent background)
- Search bar for filtering
- Shows **all behaviors equally** (built-in and custom)
- Click card to add behavior to selected sprite

**Templates Tab**:
- Template cards showing behavior bundles
- One-click to add all behaviors in template
- Built-in templates + user-saved templates
- Shows list of included behaviors on each card

### No Hierarchy - Flat Discovery

- All behaviors appear in single browsable list
- Categories are just **filters**, not hierarchies
- Custom behaviors appear alongside built-in ones
- Search across all behaviors simultaneously

**Triggered by**: "Add Behavior" button in Properties panel (opens as modal dialog)

---

## 6. Implementation Phases

### Phase 1.3: Behavior Browser & Templates (Current Priority)

**Tasks**:
1. Component metadata system
   - Add `__metadata__` to all engine components
   - Auto-discover user components from `<project>/behaviors/`
   - Category registration (Physics, Rendering, Gameplay, AI, Audio, Custom)
2. Behavior Browser modal dialog
   - Two-tab interface (Behaviors, Templates)
   - Card grid layout with category pill filters
   - Search functionality
   - Modal dialog (PyQt6 QDialog)
3. Template system
   - Save sprite as template (JSON format)
   - Load template and apply behaviors
   - Built-in template library (5+ common configurations)
4. Properties panel integration
   - "Add Behavior" opens browser
   - List attached behaviors with expand/collapse
   - Enable/disable toggles per behavior

**Estimated effort**: 2-3 sessions

### Phase 1.4: Script Integration & Code Editor

**Tasks**:
1. Code editor panel
   - Embed QsciScintilla (or QTextEdit fallback) in main panel
   - Python syntax highlighting
   - Code completion (if QsciScintilla)
   - View switcher (Scene ↔ Code buttons)
   - Font size and editor preferences
2. Behavior script creation
   - "New Behavior" button in browser → template selection
   - Creates `<project>/behaviors/<name>.py`
   - Auto-opens in code editor
   - Script templates (basic, physics-aware, AI state machine)
3. Hot-reload system
   - File watcher for behavior scripts
   - "Save & Reload" re-imports module
   - Updates running sprites with new code
   - Error handling and rollback on failure
4. Integration
   - "Edit Code" button for custom behaviors in Properties panel
   - Auto-detect and list custom behaviors in browser

**Estimated effort**: 3-4 sessions

### Future: Logic Objects (Phase 1.5+)

Add support for non-visual entities (game managers, audio controllers, systems):
- Create `Entity` base class (extract shared logic from Sprite)
- `Sprite Object` inherits from `Entity` (adds transform + rendering)
- `Logic Object` inherits from `Entity` (no transform or rendering)
- Shows in hierarchy with ⚙️ icon (vs 🎮 for sprites)
- Can have behaviors attached (same as Sprite Objects)
- Templates work identically for both object types

**Implementation tasks**:
1. Refactor `Sprite` class → extract base `Entity` class
2. Create `LogicObject` class (inherits `Entity`, skips render)
3. Update editor hierarchy to show both types
4. Update Properties panel to work with both
5. "Add Logic Object" context menu in hierarchy

---

## 7. File Structure After Implementation

```
MyGame/
├── project.json
├── scenes/
│   ├── level_1.scene          # Scene data (sprites, behaviors, properties)
│   └── level_2.scene
├── behaviors/                  # User-created behaviors
│   ├── enemy_patrol.py
│   ├── player_inventory.py
│   └── door_controller.py
├── templates/                  # User-saved templates
│   ├── my_enemy.template
│   ├── power_up.template
│   └── platform_moving.template
└── assets/
    ├── sprites/
    ├── sounds/
    └── music/
```

**Engine structure**:
```
v2_engine/
├── components/                 # Built-in behaviors
│   ├── component.py           # Base class
│   ├── rigidbody.py
│   ├── box_collider.py
│   └── platformer_controller.py
├── templates/                  # Built-in templates
│   ├── platformer_player.template
│   ├── flying_enemy.template
│   └── collectible.template
└── sprites/
    └── sprite.py              # Sprite class with component system
```

---

## 8. Design Decisions

### 1. Hot-Reload Behavior ✅ DECIDED

**User Flow Context**:
User is testing game in Play Mode. Enemy is mid-patrol. User notices speed is too slow:
1. Clicks "Edit Code" on EnemyPatrol behavior
2. Changes `self.speed = 50` to `self.speed = 150`
3. Clicks "Save & Reload"

**What happens to the running enemy?**

**Option A: Re-instantiate (Fresh Start)** ✅ **CHOSEN**
- Remove old component instance, create new one from scratch
- Enemy resets to initial state (runs `__init__` again)
- **Pros**: Simple, predictable, reliable, no edge cases
- **Cons**: Runtime state is lost (enemy position resets)
- **UX**: User sees behavior reset to initial state - acceptable tradeoff

**Option B: Hot-swap Methods (Preserve State)** ❌ **REJECTED**
- Complex implementation (update `__class__`, re-bind methods)
- Potential for bugs and weird edge cases
- Minor convenience not worth the complexity

**Decision**: Implement Option A (re-instantiate). Clean slate is more reliable. If this becomes a major pain point in practice, we can revisit hot-swapping in a future phase.

### 2. Entity Type Terminology ✅ DECIDED

**Two entity types**:
- **Sprite Object** - Has visual representation (image, transform, rendering)
- **Logic Object** - No visual representation (game managers, controllers, systems)

**Rationale**: Self-explanatory terminology, clear distinction
- "Sprite Object" → obviously has a sprite
- "Logic Object" → obviously for logic/code only

### 3. Code Editor Choice ✅ DECIDED

**QsciScintilla** - Full-featured code editor widget
- Code completion (essential for productivity)
- Excellent syntax highlighting
- Industry-standard features
- Worth the setup complexity

**Decision**: Use QsciScintilla for Phase 1.4

### 4. Template Scope ✅ DECIDED

**Templates include ONLY**:
- ✅ List of behaviors
- ✅ Behavior property values

**Templates do NOT include**:
- ❌ Sprite transform settings (position, rotation, scale)
- ❌ Sprite visual properties (image, color)
- ❌ Child sprites or nested entities

**Rationale**: Templates are behavior bundles, nothing more
- For full sprite duplication → user can copy sprite in hierarchy and tweak
- Keeps templates simple and focused on their purpose

---

## 9. Success Criteria

### Phase 1.3 Complete When:
- ✅ User can browse all behaviors (built-in + custom) in visual browser
- ✅ User can filter by category and search by name
- ✅ User can add behaviors via browser (replaces manual component selection)
- ✅ User can save current sprite as template
- ✅ User can apply template to add multiple behaviors at once
- ✅ Engine provides 5+ built-in templates for common entity types

### Phase 1.4 Complete When:
- ✅ User can create new behavior from template
- ✅ User can edit behavior code in embedded editor
- ✅ Code editor has syntax highlighting and code completion
- ✅ User can hot-reload behavior changes
- ✅ Custom behaviors auto-appear in Behavior Browser
- ✅ "Edit Code" button opens custom behavior in editor

---

## Next Steps

1. **Review & approve** this architecture (confirms alignment with V2_VISION.md)
2. **Answer open questions** (hot-reload approach, code editor choice, template scope)
3. **Begin Phase 1.3 implementation** (Behavior Browser + Templates)
4. **Test workflow** with sample project
5. **Iterate** based on usability findings
6. **Proceed to Phase 1.4** (Code Editor + Script Integration)

---

*This document defines the entity/behavior system architecture in line with the vision established in V2_VISION.md*
