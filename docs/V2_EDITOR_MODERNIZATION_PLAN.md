# Scribe Engine V2 - Editor Modernization Plan

**Created**: 2025-10-04
**Status**: Planning Phase
**Goal**: Transform Qt editor into a modern, clean, professional IDE

---

## Vision

Create a **modern, breathable, intuitive** editor that:
- Uses clean visual hierarchy and generous spacing
- Provides clear focus without overwhelming the user
- Matches quality of professional game engines (Unity, Godot, Unreal)
- Maintains approachability for beginners

---

## Design Principles

1. **Breathable Layout**: Generous margins and padding (8-12px minimum)
2. **Visual Hierarchy**: Clear distinction between primary, secondary, tertiary UI
3. **Consistent Theming**: Centralized color palette and spacing system
4. **Progressive Disclosure**: Hide complexity until needed (collapsible sections)
5. **Clarity Over Density**: Better to scroll than to cram
6. **Iconography**: Visual recognition over text-heavy UI

---

## Color Palette (Modern Dark Theme)

### Base Colors
```python
BACKGROUND_DARK = "#1e1e1e"      # Main editor background
BACKGROUND_MID = "#252526"       # Panel backgrounds
BACKGROUND_LIGHT = "#2d2d30"     # Raised elements (buttons, cards)
BACKGROUND_HOVER = "#3e3e42"     # Hover states

BORDER_SUBTLE = "#3c3c41"        # Subtle separators
BORDER_STRONG = "#555555"        # Strong dividers

TEXT_PRIMARY = "#cccccc"         # Main text
TEXT_SECONDARY = "#969696"       # Labels, hints
TEXT_DISABLED = "#6e6e6e"        # Disabled state

ACCENT_PRIMARY = "#0e639c"       # Selected items, focus
ACCENT_HOVER = "#1177bb"         # Hover on accented items
ACCENT_BRIGHT = "#4fc3f7"        # Highlights, links

SUCCESS = "#4ec9b0"              # Success states
WARNING = "#ce9178"              # Warnings
ERROR = "#f48771"                # Errors
INFO = "#3794ff"                 # Information
```

### Component-Specific Colors
```python
# Component categories (inspired by vision doc)
CATEGORY_PHYSICS = "#ff9800"     # Orange - RigidBody, Colliders
CATEGORY_RENDERING = "#2196f3"   # Blue - Sprites, Cameras
CATEGORY_GAMEPLAY = "#4caf50"    # Green - Controllers, Logic
CATEGORY_AI = "#9c27b0"          # Purple - AI behaviors
CATEGORY_AUDIO = "#00bcd4"       # Cyan - Audio sources
CATEGORY_INTERACTION = "#ff5722" # Red-Orange - Triggers, Dialogue
```

### Spacing System
```python
SPACING_TINY = 4      # Tight gaps (inside buttons)
SPACING_SMALL = 8     # Standard gaps (between elements)
SPACING_MEDIUM = 12   # Section gaps
SPACING_LARGE = 16    # Major section gaps
SPACING_XLARGE = 24   # Panel gaps

PADDING_COMPACT = 6   # Button padding
PADDING_NORMAL = 10   # Panel padding
PADDING_SPACIOUS = 16 # Card padding
```

### Typography
```python
FONT_FAMILY_UI = "Segoe UI, Arial, sans-serif"
FONT_FAMILY_CODE = "Consolas, 'Courier New', monospace"

FONT_SIZE_SMALL = 10   # Hints, captions
FONT_SIZE_NORMAL = 11  # Standard UI text
FONT_SIZE_LARGE = 13   # Headers, emphasis
FONT_SIZE_XLARGE = 16  # Section titles
```

---

## Implementation Phases

### Phase 1: Centralized Theme System (Foundation)

**File**: `v2_engine/editor/theme.py`

```python
@dataclass
class EditorTheme:
    """Centralized theme configuration for Qt editor."""

    # Colors
    background_dark: str = "#1e1e1e"
    background_mid: str = "#252526"
    # ... all colors above

    # Spacing
    spacing_small: int = 8
    spacing_medium: int = 12
    # ... all spacing above

    # Typography
    font_family_ui: str = "Segoe UI, Arial, sans-serif"
    # ... etc

    def get_stylesheet(self) -> str:
        """Generate complete Qt stylesheet from theme."""
        return f"""
            QMainWindow {{
                background-color: {self.background_dark};
                color: {self.text_primary};
                font-family: {self.font_family_ui};
                font-size: {self.font_size_normal}pt;
            }}

            QDockWidget {{
                background-color: {self.background_mid};
                border: 1px solid {self.border_subtle};
                titlebar-close-icon: url(close.png);
                titlebar-normal-icon: url(float.png);
            }}

            QDockWidget::title {{
                background-color: {self.background_light};
                padding: {self.spacing_small}px;
                border-bottom: 1px solid {self.border_subtle};
            }}

            QPushButton {{
                background-color: {self.background_light};
                color: {self.text_primary};
                border: 1px solid {self.border_subtle};
                border-radius: 3px;
                padding: {self.padding_compact}px {self.padding_normal}px;
                min-height: 24px;
            }}

            QPushButton:hover {{
                background-color: {self.background_hover};
                border-color: {self.accent_hover};
            }}

            QPushButton:pressed {{
                background-color: {self.accent_primary};
            }}

            QPushButton:disabled {{
                background-color: {self.background_dark};
                color: {self.text_disabled};
            }}

            QTreeWidget {{
                background-color: {self.background_mid};
                color: {self.text_primary};
                border: none;
                outline: none;
                padding: {self.spacing_small}px;
            }}

            QTreeWidget::item {{
                padding: {self.spacing_tiny}px;
                border-radius: 3px;
            }}

            QTreeWidget::item:selected {{
                background-color: {self.accent_primary};
                color: white;
            }}

            QTreeWidget::item:hover {{
                background-color: {self.background_hover};
            }}

            QTabWidget::pane {{
                border: 1px solid {self.border_subtle};
                background-color: {self.background_mid};
            }}

            QTabBar::tab {{
                background-color: {self.background_dark};
                color: {self.text_secondary};
                padding: {self.spacing_small}px {self.spacing_medium}px;
                border: 1px solid {self.border_subtle};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }}

            QTabBar::tab:selected {{
                background-color: {self.background_mid};
                color: {self.text_primary};
                border-bottom: 2px solid {self.accent_bright};
            }}

            QTabBar::tab:hover {{
                background-color: {self.background_hover};
            }}

            QScrollBar:vertical {{
                background-color: {self.background_dark};
                width: 12px;
                border: none;
            }}

            QScrollBar::handle:vertical {{
                background-color: {self.border_strong};
                border-radius: 6px;
                min-height: 20px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: {self.text_disabled};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QLineEdit, QTextEdit {{
                background-color: {self.background_dark};
                color: {self.text_primary};
                border: 1px solid {self.border_subtle};
                border-radius: 3px;
                padding: {self.spacing_small}px;
                selection-background-color: {self.accent_primary};
            }}

            QLineEdit:focus, QTextEdit:focus {{
                border-color: {self.accent_bright};
            }}

            QLabel {{
                color: {self.text_primary};
            }}

            QGroupBox {{
                border: 1px solid {self.border_subtle};
                border-radius: 4px;
                margin-top: {self.spacing_medium}px;
                padding-top: {self.spacing_medium}px;
                background-color: {self.background_light};
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {self.spacing_medium}px;
                padding: 0 {self.spacing_small}px;
                color: {self.text_secondary};
                font-weight: bold;
            }}
        """
```

**Tasks:**
- [ ] Create `v2_engine/editor/theme.py` with EditorTheme dataclass
- [ ] Implement `get_stylesheet()` method
- [ ] Add theme loading/saving to project settings
- [ ] Apply theme globally in EditorWindow.__init__()
- [ ] Remove all hardcoded styles from qt_editor.py

---

### Phase 2: Modernize Inspector Panel

**Goal**: Transform flat form layout into beautiful component cards

**Current**:
```
Properties
──────────
Name: [Player        ]
Position X: [100.0   ]
Position Y: [200.0   ]
Rotation: [0.0       ]
... (all properties flat)
```

**Target**:
```
┌─────────────────────────────────┐
│ Selected: Player                │
│ ─────────────────────────────── │
│ Transform               [▼]     │
│   Position: (100, 200)          │
│   Rotation: 0°                  │
│   Scale: (1.0, 1.0)             │
│                                 │
│ ┌───────────────────────────┐   │
│ │ ⚙️ RigidBody          [×]│   │
│ │ Mass: 1.0                 │   │
│ │ Gravity Scale: 1.0        │   │
│ │ ☑ Is Kinematic            │   │
│ │ ─────────────────────────││   │
│ │ Physics                   │   │
│ └───────────────────────────┘   │
│                                 │
│ ┌───────────────────────────┐   │
│ │ 📦 BoxCollider        [×]│   │
│ │ Width: 32                 │   │
│ │ Height: 32                │   │
│ │ ☐ Is Trigger              │   │
│ │ ─────────────────────────││   │
│ │ Physics                   │   │
│ └───────────────────────────┘   │
│                                 │
│ [+ Add Component ▼]             │
└─────────────────────────────────┘
```

**Implementation**:

Create `v2_engine/editor/widgets/component_card.py`:
```python
class ComponentCard(QWidget):
    """Collapsible card widget for displaying a component."""

    def __init__(self, component_name, category, icon_emoji, parent=None):
        super().__init__(parent)
        self.component_name = component_name
        self.category = category
        self.collapsed = False

        self.setup_ui(icon_emoji)

    def setup_ui(self, icon_emoji):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header (clickable to collapse)
        header = QWidget()
        header.setObjectName("ComponentCardHeader")
        header_layout = QHBoxLayout(header)

        # Icon + Name
        icon_label = QLabel(icon_emoji)
        icon_label.setFont(QFont("Segoe UI Emoji", 14))
        header_layout.addWidget(icon_label)

        name_label = QLabel(self.component_name)
        name_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        header_layout.addWidget(name_label)

        header_layout.addStretch()

        # Delete button
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(20, 20)
        header_layout.addWidget(delete_btn)

        layout.addWidget(header)

        # Body (properties)
        self.body = QWidget()
        self.body_layout = QFormLayout(self.body)
        self.body_layout.setContentsMargins(32, 8, 8, 8)  # Indent under icon
        layout.addWidget(self.body)

        # Category badge at bottom
        category_label = QLabel(self.category)
        category_label.setObjectName("CategoryBadge")
        category_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(category_label)
```

**Tasks:**
- [ ] Create ComponentCard widget
- [ ] Add collapse/expand animation
- [ ] Implement property editors (sliders, checkboxes, color pickers)
- [ ] Refactor properties panel to use ComponentCard
- [ ] Add category color coding

---

### Phase 3: Improve Hierarchy Panel

**Goal**: Add icons, better visual organization, drag-drop

**Features**:
- Icon for each sprite type (🎮 Player, 🧱 Platform, ⭐ Collectible)
- Component indicators (small icons showing RigidBody, Collider, etc.)
- Drag-drop to reorder sprites
- Right-click context menu (Duplicate, Delete, Copy, Paste)
- Search/filter bar

**Tasks:**
- [ ] Add icon system for sprites
- [ ] Implement drag-drop reordering
- [ ] Add search bar above hierarchy tree
- [ ] Create context menu
- [ ] Show component count badge on sprites

---

### Phase 4: Redesign Main Layout

**Goal**: Better space utilization, cleaner organization

**Changes**:
- Move GameState panel to tabbed left panel (not bottom dock)
- Add bottom Console panel for runtime logs
- Add toolbar above viewport with quick tools
- Status bar at bottom with scene info, FPS, camera position

**New Layout**:
```
┌──────────────────────────────────────────────────────────────┐
│ File  Scene  GameObject  Component  Play            Help [?] │
├─────────┬────────────────────────────────────────┬───────────┤
│ PROJECT │ [Select] [Move] [Rotate] [Scale]       │PROPERTIES │
│ ─────── │ ──────────────────────────────────────│───────────│
│ Scenes  │                                        │Selected:  │
│ Hierchy │      [Pygame Viewport]                │ Player    │
│ Assets  │                                        │           │
│ State   │                                        │Transform ▼│
│         │                                        │[Card UI]  │
│         │                                        │           │
│ [Tree]  │                                        │Components:│
│         │                                        │[Cards...] │
│         │                                        │           │
│         │                                        │[+Add]     │
├─────────┴────────────────────────────────────────┴───────────┤
│ CONSOLE                                        [Clear][Filter]│
│ [SceneManager] Loaded scene: main                            │
│ [Physics] Initialized collision system                       │
├──────────────────────────────────────────────────────────────┤
│ Scene: main  |  FPS: 60  |  Camera: (0, 0)  |  Zoom: 100%  │
└──────────────────────────────────────────────────────────────┘
```

**Tasks:**
- [ ] Move GameState to left panel tabs
- [ ] Create Console panel (bottom dock)
- [ ] Create Toolbar widget above viewport
- [ ] Create StatusBar widget
- [ ] Adjust spacing and proportions

---

### Phase 5: Polish & UX Improvements

**Keyboard Shortcuts**:
- Ctrl+N - New Scene
- Ctrl+S - Save Scene
- Ctrl+D - Duplicate Selected
- Delete - Delete Selected
- Ctrl+C/V - Copy/Paste sprite
- F2 - Rename sprite
- F5 - Play
- Shift+F5 - Stop

**Visual Polish**:
- Add subtle shadows to cards
- Smooth hover transitions
- Loading spinners for async operations
- Toast notifications for actions
- Undo/Redo feedback

**Tasks:**
- [ ] Implement all keyboard shortcuts
- [ ] Add hover animations
- [ ] Create toast notification system
- [ ] Add loading states
- [ ] Implement undo/redo

---

## Success Criteria

✅ **Editor looks modern and professional**
✅ **UI has consistent spacing (no cramped areas)**
✅ **Component cards are beautiful and functional**
✅ **No hardcoded colors (all from theme)**
✅ **Keyboard shortcuts work smoothly**
✅ **New users can navigate without confusion**

---

## References

- Unity Editor UX
- Godot Editor UX
- VS Code theming
- Material Design spacing principles
- V2_VISION.md (terminology, philosophy)
