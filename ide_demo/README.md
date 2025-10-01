# Scribe Engine v2 - IDE Prototype

This is an interactive design prototype of the proposed Scribe Engine v2 IDE for 2D game development.

## Features Demonstrated

### Layout
- **Three-panel layout**: Project/Assets (left), Scene Editor/Code (center), Hierarchy/Inspector (right)
- **Top menu bar**: File, Edit, Scene, Build, Help
- **Status bar**: Shows current state and runtime info

### Left Sidebar - Project & Assets
- **File tree** with collapsible sections:
  - Scenes (Python files)
  - Sprites (organized by folders)
  - Tilemaps
  - Audio
- Click files to "open" them (updates center panel)
- Expandable/collapsible sections

### Center Panel - Scene Editor & Code

#### Visual Scene Editor (Canvas)
- **Canvas toolbar** with tools:
  - Select, Move, Add Sprite
  - Grid, Collision, Snap toggles
  - Zoom controls
- **Interactive canvas**:
  - Click sprites to select them
  - Drag sprites to reposition
  - Snap to grid (when enabled)
  - Shows grid overlay
  - Shows collision boxes (when enabled)
- **Canvas status bar**: Shows scene size, mouse position, selected sprite

#### Code Editor
- Syntax-highlighted Python code
- Shows the actual Scene class structure
- Demonstrates the Python API design

#### View Modes
- **Visual**: Canvas only
- **Code**: Code editor only
- **Split**: Both side-by-side (default)

### Right Sidebar

#### Scene Hierarchy
- Lists all objects in the scene
- Click to select (syncs with canvas)
- Shows sprite types with icons

#### Inspector
- Shows properties of selected sprite:
  - File path
  - Transform (Position, Size)
  - Physics (Gravity, Collision, Speed)
  - Layer (Z-index)
  - Animation settings
- **Interactive**: Change position values to move sprite

### Interactive Features

Try these:
1. **Click sprites on canvas** - they'll be selected and highlighted
2. **Drag sprites around** - they'll move (with grid snap if enabled)
3. **Toggle Grid/Collision** - see visual aids
4. **Change position in Inspector** - sprite moves on canvas
5. **Click Play Scene** - shows what would happen in real IDE
6. **Switch view modes** - Visual/Code/Split tabs
7. **Expand/collapse tree sections** - organize your project
8. **Zoom in/out** - scale the canvas view

## How to View

Simply open `index.html` in a web browser. No server needed for this prototype.

## What This Demonstrates

### Design Decisions:
- **Familiar layout**: Similar to Unity, Godot, Unreal (industry standard)
- **Dark theme**: Easy on eyes for long dev sessions
- **Split view**: See visual layout AND code simultaneously
- **Two-way editing**: Change visual OR code (both stay in sync)
- **Inspector-driven workflow**: Click, edit properties, done

### Python-First Approach:
- Code editor shows clean, readable Python
- Visual editor generates/updates this Python
- No custom syntax - just Python classes
- Scene class structure is simple and understandable

### Accessibility:
- Beginners: Use visual editor, minimal code
- Intermediate: Mix visual layout + code logic
- Advanced: Edit Python directly, visual updates

### Workflow Example:
1. Drag sprite onto canvas (visual)
2. Position it where you want (visual)
3. Add behavior in code (Python)
4. Click Play to test in pygame window
5. Iterate

## Technical Notes

**Current Implementation:**
- Pure HTML/CSS/JavaScript
- Canvas 2D API for rendering
- Mock data (not connected to backend)
- Demonstrates UI/UX only

**Real Implementation Would Add:**
- Flask backend integration
- Actual Python code generation
- File system operations
- Pygame subprocess spawning
- Hot reload on file changes
- Asset import/management
- Undo/redo system
- Multi-scene support

## Design Goals Achieved

✅ **Approachable**: Visual tools for beginners
✅ **Powerful**: Full Python access for advanced users
✅ **Transparent**: See the code being generated
✅ **Familiar**: Industry-standard layout
✅ **Integrated**: Everything in one IDE
✅ **Visual + Code**: Best of both worlds

## Feedback Welcome

This prototype is meant to visualize the v2 IDE concept. It demonstrates:
- Layout and organization
- Visual editing workflow
- Code structure
- Inspector-based property editing
- Scene hierarchy

The actual implementation would be much more powerful, but this shows the core UX/UI vision.
