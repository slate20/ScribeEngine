# Scribe Engine V2 - Revised Development Plan: IDE-First Approach

**Created**: 2025-10-02
**Status**: Active Development Plan
**Focus**: Component-based architecture with complete IDE workflow

---

## Architecture Validation ✅

The component-based architecture is confirmed:
- **Game** → **Scene** → **Sprite** → **Component**
- **Composition over inheritance** (sprites get behaviors from components)
- **Components** are modular, reusable behaviors
- **Sprites** are just containers with transforms by default

This architecture must drive how we build the IDE.

---

## Critical Gaps Identified

### 1. **Project Management UI** (Missing Entirely)
Currently there's NO way for users to:
- Set game resolution (800x600, 1920x1080, etc.)
- Toggle fullscreen/windowed mode
- Set entry scene (which scene loads first)
- Configure project title
- Set physics defaults (gravity)

**What exists**: JSON file (`2d_project.json`) with these settings
**What's missing**: UI to edit them

### 2. **Scene Transition API** (Exists but not exposed in IDE)
- Code works: `self.game.scene_manager.load_scene("level_2")`
- But users have no IDE helper to add this
- No visual "trigger" system (e.g., "when player touches door → load level_2")

### 3. **Background System** (Doesn't exist at all)
- Scenes have no background property
- No way to set scene background color or image in IDE
- Currently scenes just have default pygame fill

### 4. **Build System** (Not integrated)
- Can't build/export games from IDE
- V1 build system exists but not hooked up to IDE
- One-click export is a core feature we're missing

### 5. **Component Inspector** (Critical for IDE)
- Sprites have component support in code (`sprite.add_component()`)
- But IDE has no "Add Component" button
- No component property inspector
- **This is THE core of the component architecture**

### 6. **Sprite Templates/Prefabs** (Doesn't exist)
- No way to save a sprite with preset components
- Can't create reusable "Player" template
- Manual recreation every time

---

## Revised Priority List

### **PRIORITY 1: Core IDE Functionality** (Must Have Before Anything Else)

These are the **basic IDE features** that enable users to configure and build games. Without these, users can't even set their game resolution or build an executable.

#### 1.1 Project Settings Panel (~4 hours)
**What**: Dialog window to edit `2d_project.json` visually

**Features**:
- Window settings (resolution, fullscreen, title)
- Physics defaults (gravity X/Y)
- Entry scene dropdown (which scene loads first)
- Asset path configuration

**UI Location**: File → Project Settings...

**File**: `v2_engine/editor/project_settings_dialog.py`

---

#### 1.2 Scene Background System (~2 hours)
**What**: Ability to set scene backgrounds (color or image)

**Features**:
- Add `background_color` property to Scene
- Add `background_image` property to Scene
- UI in properties panel when nothing selected: "Scene Background"
- Serialize to scene files

**Implementation**:
- Modify `v2_engine/core/scene.py` (add properties)
- Modify `qt_editor.py` properties panel (show when no sprite selected)
- Modify `scene_serializer.py` (save background settings)

---

#### 1.3 Component Inspector (~8 hours)
**What**: The heart of the component system - add/edit components on sprites

**Features**:
- "Add Component" button in properties panel
- Dropdown list of available components
- Show all components attached to selected sprite
- Edit component properties (mass, gravity_scale, etc.)
- Remove component button
- Serialize components to scene files

**UI Layout** (Properties Panel):
```
Selected: Player
Name: Player
[Properties...]

Components:
┌─────────────────────────┐
│ RigidBody            [×]│
│  Mass: 1.0              │
│  Gravity Scale: 1.0     │
│  Is Kinematic: □        │
└─────────────────────────┘
┌─────────────────────────┐
│ BoxCollider          [×]│
│  Width: 32              │
│  Height: 32             │
└─────────────────────────┘

[+ Add Component ▼]
```

**Implementation**:
- Modify `qt_editor.py` properties panel
- Create component property widgets dynamically
- Modify `scene_serializer.py` (serialize component data)

---

#### 1.4 Basic Scene Triggers (~4 hours)
**What**: Simple component for scene transitions (collide with object → load scene)

**Features**:
- Create `SceneTrigger` component
- Properties:
  - `target_tag`: Which sprite tag triggers it (e.g., "player")
  - `target_scene`: Which scene to load
- Automatically loads scene on collision
- Visual indicator in editor (show trigger bounds)

**Usage**:
1. Create sprite (invisible box at door location)
2. Add `BoxCollider` component
3. Add `SceneTrigger` component
4. Set target_scene = "level_2"
5. When player touches it → loads level_2

**File**: `v2_engine/components/scene_trigger.py`

---

#### 1.5 Build System Integration (~6 hours)
**What**: One-click build to create distributable game

**Features**:
- "Build Game" menu item (File → Build Game)
- Build settings dialog (platform, output folder)
- Progress dialog during build
- Uses existing V1 asset packer system
- Produces `.exe` (Windows) or executable (Linux/Mac)

**Implementation**:
- Add menu item to `qt_editor.py`
- Create build dialog
- Call V1 `asset_packer.py` and `build_player.py`
- Show success/failure message with output path

**File**: `v2_engine/editor/build_dialog.py`

---

**PRIORITY 1 TOTAL**: ~24 hours (3 working days)

**Success Criteria**: Users can configure project settings, add components to sprites, create scene transitions, and build playable executables.

---

### **PRIORITY 2: Essential Components** (Build Actual Games)

These are the **core components** needed to make functional games. Without these, sprites just sit there - no physics, no input, no behavior.

#### 2.1 Core Components (~12 hours)

**RigidBody Component**:
- Properties: `mass`, `gravity_scale`, `velocity`, `is_kinematic`
- Applies gravity every frame
- Handles velocity-based movement
- Collision response (bounce, slide, stop)

**BoxCollider Component**:
- Properties: `width`, `height`, `offset`, `is_trigger`
- AABB collision detection
- Collision events (on_collision_enter, on_collision_exit)

**SpriteRenderer Component** (formalize existing):
- Properties: `layer`, `flip_x`, `flip_y`, `tint_color`
- Already implicit, make it explicit

**Transform Component** (expose existing):
- Already exists on Sprite
- Show as component in inspector for consistency

**Files**:
- `v2_engine/components/rigidbody.py`
- `v2_engine/components/box_collider.py`
- `v2_engine/components/sprite_renderer.py`

---

#### 2.2 Input System (~4 hours)
**What**: Complete keyboard/mouse input integration for scenes

**Features**:
- Expose InputHandler to scenes as `self.input`
- API:
  - `self.input.key_pressed('w')` - just pressed this frame
  - `self.input.key_held('w')` - held down
  - `self.input.key_released('w')` - just released
  - `self.input.mouse_pos()` - mouse position
  - `self.input.mouse_clicked(button)` - mouse button pressed

**Implementation**:
- Complete `v2_engine/core/input.py` (exists as skeleton)
- Add to scene update cycle
- Add to component update cycle (components can access parent sprite's scene)

---

#### 2.3 Camera Component (~4 hours)
**What**: Camera that follows player and respects bounds

**Features**:
- `FollowTarget` component
  - Properties: `target` (which sprite to follow), `smoothness`, `offset`
- Camera bounds (min_x, min_y, max_x, max_y)
- Smooth follow with lerp
- Dead zone (don't follow small movements)

**File**: `v2_engine/components/follow_camera.py`

**Note**: Editor already has camera for viewport. This is for gameplay.

---

#### 2.4 Simple Behavior Components (~8 hours)

**PatrolAI Component**:
- Move sprite between waypoints
- Properties: `waypoints` (list of positions), `speed`, `loop`

**PlatformerController Component**:
- WASD movement + spacebar jump
- Properties: `speed`, `jump_force`, `double_jump`
- Requires RigidBody

**Health Component**:
- Properties: `max_health`, `current_health`
- Methods: `take_damage(amount)`, `heal(amount)`
- Events: `on_death`

**Trigger Component** (already in 1.4):
- Generic trigger system
- Properties: `trigger_type`, `target_tag`
- Events: `on_trigger_enter`, `on_trigger_exit`

**Files**:
- `v2_engine/components/patrol_ai.py`
- `v2_engine/components/platformer_controller.py`
- `v2_engine/components/health.py`

---

**PRIORITY 2 TOTAL**: ~28 hours (3.5 working days)

**Success Criteria**: Can create a working platformer with player movement, enemies that patrol, health system, and scene transitions.

---

### **PRIORITY 3: Advanced Tooling** (Polish & Power Features)

These are **quality-of-life improvements** and **advanced features** that make the IDE professional. Important, but games can be made without them.

#### 3.1 Sprite Templates/Prefabs (~6 hours)
**What**: Save sprites with components as reusable templates

**Features**:
- "Save as Template" button in properties panel
- Template library panel (4th tab in left panel)
- Drag template from library → creates sprite with all components
- Templates stored as JSON in project folder

**Use Case**:
1. Create "Player" sprite with RigidBody, BoxCollider, PlatformerController
2. Save as template
3. Reuse in every level

---

#### 3.2 Component Creator Wizard (~8 hours)
**What**: Wizard to create custom components without writing boilerplate

**Features**:
- New → Component... menu item
- Wizard asks for:
  - Component name
  - Properties (name, type, default value)
  - Update code (optional Python)
- Generates Python file with boilerplate
- Auto-registers component with IDE

**Output Example**:
```python
# Generated component
class CustomBehavior(Component):
    def __init__(self, sprite):
        super().__init__(sprite)
        self.speed = 100.0
        self.damage = 10

    def update(self, dt):
        # User's custom code here
        pass
```

---

#### 3.3 Visual Scripting (Optional) (~16 hours)
**What**: Node-based behavior editor for non-coders

**Features**:
- Visual node graph (like Unreal Blueprints, Godot VisualScript)
- Common nodes: Input, Math, Comparisons, Events
- Compiles to Python component
- For designers who don't code

**Note**: This is ambitious and optional. Many engines don't have this.

---

#### 3.4 Animation System (~12 hours)
**What**: Sprite sheet animations

**Features**:
- Import sprite sheets (grid-based)
- Define animations (name, frames, speed)
- `Animator` component
- Animation state machine
- Preview in IDE

**Components**:
- `v2_engine/components/animator.py`
- Animation editor window

---

**PRIORITY 3 TOTAL**: ~42 hours (5 working days)

**Success Criteria**: IDE has professional polish, templates speed up development, custom components are easy to create.

---

## Immediate Next Steps (Session-by-Session Plan)

### Session 1: Project Settings Panel (~4 hours)
**Goal**: Create UI to edit `2d_project.json`

**Tasks**:
1. Create `ProjectSettingsDialog` (QDialog)
2. Load `2d_project.json` into form fields
3. Sections: Window, Physics, Scenes, Assets
4. Save button writes back to JSON
5. Add to File menu: "Project Settings..."

**Deliverable**: User can set game resolution, fullscreen mode, entry scene through UI

---

### Session 2: Scene Background System (~2 hours)
**Goal**: Scenes can have background colors or images

**Tasks**:
1. Add `background_color` and `background_image` to `Scene` class
2. Properties panel shows background section when no sprite selected
3. Scene serializer saves background settings
4. Renderer draws background before sprites

**Deliverable**: User can set blue sky background or forest image for levels

---

### Session 3: Component Inspector Foundation (~8 hours)
**Goal**: Can add/view/edit components on sprites

**Tasks**:
1. Add "Components" section to properties panel
2. Show all attached components with properties
3. "Add Component" dropdown (empty for now, will populate in Session 4)
4. Edit component properties (dynamically generate widgets based on property types)
5. Remove component button
6. Serialize components to scene files (save/load)

**Deliverable**: IDE can inspect components (even if none exist yet)

---

### Session 4: First Real Component - RigidBody (~4 hours)
**Goal**: Create RigidBody component and use it in IDE

**Tasks**:
1. Implement `RigidBody` component
   - Properties: mass, gravity_scale, velocity, is_kinematic
   - Update: apply gravity, move sprite by velocity
2. Register with IDE's component list
3. Add via "Add Component" in inspector
4. Edit mass, gravity_scale in inspector
5. Test in game preview - sprite should fall with gravity

**Deliverable**: Can add RigidBody to sprite, configure it, see it work in game

---

### Session 5: Scene Triggers (~4 hours)
**Goal**: Create SceneTrigger component for scene transitions

**Tasks**:
1. Implement `SceneTrigger` component
   - Properties: target_tag, target_scene
   - On collision with tagged sprite → load target_scene
2. Add to component registry
3. UI to configure target scene (dropdown of available scenes)
4. Test: create "door" sprite with trigger, player touches it, loads next scene

**Deliverable**: Can create scene transitions without writing code

---

### Session 6: Build System Integration (~6 hours)
**Goal**: One-click game build

**Tasks**:
1. Add "Build Game" to File menu
2. Create `BuildDialog` (select output folder, platform)
3. Progress dialog with status messages
4. Call V1 asset packer system
5. Call V1 build_player.py
6. Show success message with path to executable

**Deliverable**: Click "Build Game" → get playable .exe

---

**Total for MVP IDE**: ~28 hours (3-4 working days)

---

## Success Criteria (After Priority 1)

Users should be able to:
- ✅ Create a new project with configured settings (resolution, entry scene)
- ✅ Set game resolution and fullscreen mode through UI
- ✅ Add sprites to scenes and set scene backgrounds
- ✅ Add RigidBody component to sprites and configure properties
- ✅ Edit component properties visually (no code needed)
- ✅ Create scene triggers (door → load level_2) without code
- ✅ Build and export playable game executable
- ✅ Play game with gravity/physics working correctly

This creates a **minimal but complete game creation loop**.

---

## What We're Deferring (Not Blocking Core Workflow)

These are important but don't prevent basic game creation:

- Animation system (Priority 3)
- Tilemap support (Priority 3)
- Audio integration (Priority 3)
- Advanced components (Priority 2-3)
- Visual scripting (Priority 3, optional)
- Undo/redo (Polish)
- Multi-select sprites (Polish)
- Advanced prefab system (Priority 3)
- Visual resize handles (Polish)

---

## Development Philosophy

**Build the IDE around the component system**, not the other way around:

1. **Components are first-class citizens** in the UI
2. **Inspector drives everything** - if it's not in the inspector, it doesn't exist to users
3. **No code required for basics** - adding physics, collision, triggers should be visual
4. **Code is for advanced users** - custom components, complex logic
5. **Templates enable reuse** - don't make users rebuild the same sprite 20 times

---

## Comparison: Old vs New Priorities

### Old Priorities (Incorrect):
1. Physics system
2. Animation/Tilemap/Audio
3. UI polish

### New Priorities (Correct):
1. **IDE Core** (project settings, components, build system)
2. **Essential Components** (physics, input, basic behaviors)
3. **Advanced Tooling** (templates, animation, polish)

**Why**: The old plan focused on engine features. The new plan focuses on **user workflow**. Users need IDE tools to access engine features.

---

**Next Step**: Begin Session 1 - Project Settings Panel
