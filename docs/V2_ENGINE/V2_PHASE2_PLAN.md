# Scribe Engine V2 - Phase 2 Implementation Plan

**Phase 2: IDE Integration - Visual Scene Editing**

**Status**: Planning
**Start Date**: 2025-09-30

---

## Overview

**Goal**: Integrate V2 scene-based engine into the existing Scribe Engine IDE with visual editing tools

**Timeline**: 6-8 weeks

**Success Criteria**:
- Web-based scene editor with drag-drop sprite placement
- Property inspector for editing sprite properties
- Live preview showing pygame window
- Asset browser for images and resources
- Ability to create, edit, and test V2 games entirely from the IDE
- Seamless switching between V1 and V2 projects

---

## Architecture Decision: Web IDE + Native Preview

Based on the Phase 1 vision, we'll use a **hybrid architecture**:

### Web Layer (IDE Interface)
- **Technology**: Flask + HTML/CSS/JavaScript (existing stack)
- **Purpose**: Visual editing, file management, property inspector
- **Lives in**: `ide/` directory
- **Renders**: Scene layout, sprite hierarchy, asset browser

### Native Layer (Game Runtime)
- **Technology**: Pygame (existing V2 engine)
- **Purpose**: Live preview and actual game testing
- **Lives in**: `v2_engine/` directory
- **Runs as**: Subprocess spawned by IDE

### Communication
- **File-based**: IDE modifies scene Python files, subprocess detects changes
- **Live reload**: Watchdog monitors file changes and reloads scenes
- **State sync**: IDE can query game state via simple JSON API

---

## Phase 2 Development Breakdown

### Part 1: IDE Foundation (Week 1-2)
**Goal**: Set up V2 project support in existing IDE

**Tasks**:
1. **Project Type Detection**
   - Detect V1 vs V2 projects (`project.json` vs `2d_project.json`)
   - Update launcher UI to show project type
   - Add "New V2 Project" wizard

2. **V2 Editor Layout**
   - Create `ide/templates/v2_editor/` directory structure
   - Design 3-panel layout (similar to `ide_demo/`)
     - Left: Project/Assets panel
     - Center: Scene editor (canvas) / Code view (tabs)
     - Right: Hierarchy / Inspector panel
   - Implement basic HTML/CSS structure

3. **Flask Routes for V2**
   - `/v2/editor/<project_id>` - Main V2 editor
   - `/v2/api/project/<project_id>` - Get project config
   - `/v2/api/scenes/<project_id>` - List scenes
   - `/v2/api/sprites/<scene_id>` - Get sprite data
   - `/v2/api/preview/<project_id>` - Launch preview

**Deliverable**: Can open V2 projects in IDE, see basic editor layout

---

### Part 2: Scene Serialization System (Week 2-3)
**Goal**: Bridge between visual editing and Python code

Since scenes are Python files, we need a system to:
- Parse scene files to extract sprite data
- Modify sprite properties without breaking custom code
- Maintain hand-written code alongside visual edits

**Approach: Metadata Comments**

Scene files will use special comments for visual editing:

```python
class Level01Scene(Scene):
    def on_enter(self):
        # [SCRIBE_SPRITE_START: player]
        self.player = Player(100, 300)
        # Properties: {"x": 100, "y": 300, "layer": 10}
        # [SCRIBE_SPRITE_END: player]

        # [SCRIBE_SPRITE_START: platform_01]
        platform = Platform(200, 450, 150, 20)
        # Properties: {"x": 200, "y": 450, "width": 150, "height": 20}
        self.platforms.append(platform)
        # [SCRIBE_SPRITE_END: platform_01]
```

**Tasks**:
1. Create `SceneParser` class to extract sprite metadata
2. Create `SceneWriter` class to update sprite properties
3. Handle edge cases (custom code, deleted sprites, etc.)
4. Implement scene diff detection

**Files to Create**:
- `ide/scene_parser.py` - Parse Python scene files
- `ide/scene_writer.py` - Modify scene files safely

**Deliverable**: Can read/write sprite data from scene Python files

---

### Part 3: Visual Scene Editor (Week 3-5)
**Goal**: Drag-drop sprite placement with canvas rendering

**Tasks**:

1. **Canvas Renderer** (`ide/static/v2_assets/scene_canvas.js`)
   - HTML5 canvas for scene visualization
   - Grid system with snap-to-grid
   - Zoom and pan controls
   - Render sprites as rectangles with labels

2. **Sprite Palette** (Left panel)
   - List of available sprite types (Player, Platform, Enemy, etc.)
   - Drag from palette to canvas to create sprite
   - Custom sprite type creation

3. **Selection and Transform**
   - Click to select sprite on canvas
   - Drag to move sprite
   - Resize handles for width/height
   - Rotation handle (future)
   - Multi-select (Shift+click)

4. **Scene Hierarchy** (Right panel, top)
   - Tree view of all sprites in scene
   - Click to select sprite
   - Show/hide sprites
   - Reorder for layering

5. **Property Inspector** (Right panel, bottom)
   - Editable properties for selected sprite
   - Position (x, y)
   - Size (width, height)
   - Layer (z-order)
   - Custom properties (health, speed, etc.)
   - Live update as you drag

**API Routes**:
- `POST /v2/api/scene/<scene_id>/sprite` - Create sprite
- `PUT /v2/api/scene/<scene_id>/sprite/<sprite_id>` - Update sprite
- `DELETE /v2/api/scene/<scene_id>/sprite/<sprite_id>` - Delete sprite
- `GET /v2/api/scene/<scene_id>/data` - Get all scene data

**Deliverable**: Can visually create and edit scenes in IDE

---

### Part 4: Live Preview Integration (Week 5-6)
**Goal**: Launch pygame preview from IDE

**Architecture**:
```
IDE (Flask)
    |
    v
Spawns subprocess: python3 test_v2.py <project_path>
    |
    v
Pygame window opens (separate process)
```

**Tasks**:

1. **Preview Manager** (`ide/preview_manager.py`)
   - Spawn pygame subprocess
   - Monitor subprocess health
   - Kill subprocess on stop
   - Handle multiple previews (one per project)

2. **File Watcher Integration**
   - Use watchdog to monitor scene file changes
   - Auto-reload scenes when files change
   - Show reload notification in IDE

3. **Preview Controls in IDE**
   - "Start Preview" button (top toolbar)
   - "Stop Preview" button
   - "Restart Preview" button
   - Preview status indicator (Running/Stopped)

4. **Error Handling**
   - Capture pygame subprocess errors
   - Display in IDE console panel
   - Syntax error highlighting

**API Routes**:
- `POST /v2/api/preview/<project_id>/start` - Start preview
- `POST /v2/api/preview/<project_id>/stop` - Stop preview
- `GET /v2/api/preview/<project_id>/status` - Get status

**Deliverable**: Can test V2 games directly from IDE with live reload

---

### Part 5: Asset Management (Week 6-7)
**Goal**: Visual asset browser for sprites, sounds, music

**Tasks**:

1. **Asset Browser** (Left panel)
   - Tree view of `assets/` directory
   - Thumbnail previews for images
   - Upload/import assets
   - Drag image to canvas to create sprite

2. **Asset Manager Backend** (`ide/asset_manager.py`)
   - List assets in project
   - Upload files to `assets/` directory
   - Generate thumbnails for images
   - Validate asset formats (PNG, JPG, WAV, MP3)

3. **Sprite Image Assignment**
   - Property inspector shows current sprite image
   - Click to browse and select new image
   - Preview image in inspector

**API Routes**:
- `GET /v2/api/assets/<project_id>` - List all assets
- `POST /v2/api/assets/<project_id>/upload` - Upload asset
- `DELETE /v2/api/assets/<project_id>/<asset_path>` - Delete asset
- `PUT /v2/api/sprite/<sprite_id>/image` - Assign image to sprite

**Deliverable**: Can manage game assets from IDE

---

### Part 6: Code View Toggle (Week 7)
**Goal**: Switch between visual and code editing

**Tasks**:

1. **Tab System** (Center panel)
   - "Visual" tab (default) - Canvas scene editor
   - "Code" tab - CodeMirror Python editor
   - Toggle between views with hotkey (Ctrl+Shift+E)

2. **Code Editor Integration**
   - Reuse existing CodeMirror setup from V1
   - Python syntax highlighting
   - Auto-save on blur
   - Visual mode detects code changes and updates

3. **Sync Warning**
   - Detect when code changes conflict with visual edits
   - Show warning: "Scene modified outside visual editor"
   - Option to reload or keep changes

**Deliverable**: Can edit scenes visually or with code

---

### Part 7: Polish and Testing (Week 8)
**Goal**: Bug fixes, UX improvements, documentation

**Tasks**:

1. **Bug Fixes**
   - Test all editor operations
   - Fix edge cases in scene parser/writer
   - Handle corrupted project files gracefully

2. **UX Improvements**
   - Keyboard shortcuts (Delete to remove sprite, etc.)
   - Undo/redo support (future enhancement)
   - Tooltips and help text
   - Loading states and spinners

3. **Documentation**
   - Update `V2_DEVELOPER_GUIDE.md` with IDE instructions
   - Create `V2_IDE_GUIDE.md` for IDE features
   - Screenshot/video tutorial

4. **Integration Testing**
   - Create V2 project from IDE
   - Add sprites visually
   - Modify properties
   - Launch preview
   - Test game works
   - Export/build game

**Deliverable**: Stable, usable V2 IDE ready for end users

---

## Detailed File Structure

```
ide/
├── templates/
│   ├── v2_editor/
│   │   ├── editor.html              # Main V2 editor layout
│   │   ├── _scene_canvas.html       # Canvas panel
│   │   ├── _sprite_palette.html     # Sprite palette panel
│   │   ├── _hierarchy_panel.html    # Scene hierarchy
│   │   ├── _inspector_panel.html    # Property inspector
│   │   ├── _asset_browser.html      # Asset browser
│   │   └── _code_editor.html        # Code view
│
├── static/
│   ├── v2_assets/
│   │   ├── v2_editor.js             # Main V2 editor logic
│   │   ├── scene_canvas.js          # Canvas rendering
│   │   ├── sprite_palette.js        # Palette interactions
│   │   ├── property_inspector.js    # Inspector logic
│   │   ├── asset_browser.js         # Asset management
│   │   └── v2_editor.css            # V2 editor styles
│
├── scene_parser.py                  # Parse Python scene files
├── scene_writer.py                  # Modify scene files
├── preview_manager.py               # Pygame subprocess manager
├── asset_manager.py                 # Asset file operations
└── app.py                           # Updated with V2 routes
```

---

## Key Technical Challenges

### Challenge 1: Scene File Modification

**Problem**: How to modify Python scene files without breaking custom code?

**Solution**: Use metadata comments approach (described in Part 2)
- Visual editor only modifies code between special markers
- Custom code outside markers is preserved
- If markers are missing, warn user and offer to add them

### Challenge 2: Live Preview Communication

**Problem**: How does IDE know when preview is ready?

**Solution**: Simple status file approach
- Subprocess writes `preview_status.json` when ready
- IDE polls this file for status updates
- Alternative: WebSocket (future enhancement)

### Challenge 3: Sprite Type Discovery

**Problem**: How does IDE know what sprite types are available?

**Solution**: Static registry approach
- IDE ships with built-in sprite types (Player, Platform, Enemy)
- Scan project for custom sprite classes
- Parse Python files for `class X(Sprite)` declarations

---

## Phase 2 Milestones

| Milestone | Week | Description |
|-----------|------|-------------|
| M1: Foundation | 2 | V2 projects open in IDE, basic layout |
| M2: Scene Data | 3 | Can read/write sprite data from Python files |
| M3: Visual Editor | 5 | Can create/edit scenes visually |
| M4: Live Preview | 6 | Can test games from IDE |
| M5: Assets | 7 | Can manage game assets |
| M6: Complete | 8 | Polished, tested, documented |

---

## Success Metrics

**Functionality**:
- [ ] Can create new V2 project from IDE
- [ ] Can add sprites by dragging to canvas
- [ ] Can edit sprite properties in inspector
- [ ] Can launch preview and see changes
- [ ] Can import assets and assign to sprites
- [ ] Can switch between visual and code editing
- [ ] Can build/export V2 games

**Performance**:
- [ ] Scene editor handles 100+ sprites without lag
- [ ] Live reload triggers within 1 second of file save
- [ ] Canvas rendering at 60 FPS

**Usability**:
- [ ] Non-programmer can create simple platformer in IDE
- [ ] Programmer can extend with custom code seamlessly
- [ ] Clear documentation with examples

---

## Optional Enhancements (Post-Phase 2)

These features are valuable but not required for Phase 2 completion:

1. **Tilemap Editor**
   - Grid-based tile placement
   - Tileset management
   - Collision layers

2. **Animation System**
   - Sprite sheet slicer
   - Animation timeline editor
   - Visual animation preview

3. **Particle Effects**
   - Particle emitter editor
   - Visual effects preview

4. **Audio Integration**
   - Waveform preview
   - Sound effect testing
   - Music track management

5. **Advanced Camera**
   - Camera zones editor
   - Camera shake effects
   - Cinematic camera paths

---

## Development Approach

### Incremental Development
- Build features in small, testable increments
- Commit after each completed feature
- Test with real V2 projects at each milestone

### Code Reuse
- Leverage existing V1 IDE code where possible
- Share components (CodeMirror setup, file browser, etc.)
- Abstract common patterns into utilities

### User-Centered Design
- Design for both beginners (visual) and experts (code)
- Provide escape hatches (always allow code editing)
- Clear visual feedback for all operations

---

## Risk Mitigation

**Risk**: Scene parser breaks custom code
**Mitigation**: Extensive testing, safe fallback to code-only mode

**Risk**: Live preview crashes or hangs
**Mitigation**: Timeout detection, force-kill subprocess, clear error messages

**Risk**: IDE becomes too complex
**Mitigation**: Progressive disclosure (hide advanced features initially)

---

## Phase 2 Completion Checklist

- [ ] V2 project type detection
- [ ] V2 editor UI layout implemented
- [ ] Scene parser/writer working
- [ ] Visual scene editor functional
- [ ] Property inspector working
- [ ] Live preview integration
- [ ] Asset browser implemented
- [ ] Code/visual toggle working
- [ ] Documentation updated
- [ ] End-to-end testing passed

---

## Next Steps

Once Phase 2 is complete:
- **Phase 3**: Advanced features (tilemap, animation, particles)
- **Phase 4**: Distribution and publishing tools
- **Phase 5**: Multiplayer and networking support

---

**Last Updated**: 2025-09-30
**Status**: Ready to implement
