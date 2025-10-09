"""
Viewport Panel - Scene editor viewport with toolbar and status bar.

This panel encapsulates:
- Scene toolbar (grid, snap, transform tools, play/stop)
- Pygame widget for scene rendering
- Status bar (FPS, zoom, cursor position)
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox,
    QComboBox, QLabel, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from v2_engine.utils.math import Vector2


class ViewportPanel(QWidget):
    """
    Viewport panel containing the scene editor with toolbar and status bar.

    Signals:
        transform_tool_changed: Emitted when transform tool changes (str: 'move'/'rotate'/'scale')
        grid_visibility_changed: Emitted when grid visibility toggles (bool)
        grid_size_changed: Emitted when grid size changes (int)
        snap_to_grid_changed: Emitted when snap setting changes (bool)
        play_requested: Emitted when Play button clicked
        stop_requested: Emitted when Stop button clicked
    """

    # Signals
    transform_tool_changed = pyqtSignal(str)  # 'move', 'rotate', 'scale'
    grid_visibility_changed = pyqtSignal(bool)
    grid_size_changed = pyqtSignal(int)
    snap_to_grid_changed = pyqtSignal(bool)
    play_requested = pyqtSignal()
    stop_requested = pyqtSignal()

    def __init__(self, editor, pygame_widget, theme):
        """
        Initialize the viewport panel.

        Args:
            editor: Reference to EditorWindow
            pygame_widget: PygameWidget instance for scene rendering
            theme: EditorTheme instance
        """
        super().__init__()
        self.editor = editor
        self.pygame_widget = pygame_widget
        self.theme = theme

        # Initialize FPS tracking
        self.fps_counter = 0

        # Create UI
        self._create_ui()

    def _create_ui(self):
        """Create the viewport panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Scene toolbar
        self._create_toolbar(layout)

        # Pygame viewport
        layout.addWidget(self.pygame_widget)

        # Status bar
        self._create_status_bar(layout)

    def _create_toolbar(self, parent_layout):
        """Create toolbar for scene editor controls."""
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(
            self.theme.spacing_small,
            self.theme.spacing_small,
            self.theme.spacing_small,
            self.theme.spacing_small
        )
        toolbar_layout.setSpacing(self.theme.spacing_medium)

        # Grid visibility toggle
        self.grid_visible_checkbox = QCheckBox("Show Grid (G)")
        self.grid_visible_checkbox.setChecked(self.editor.state.camera.grid_visible)
        self.grid_visible_checkbox.stateChanged.connect(self._on_grid_visibility_changed)
        toolbar_layout.addWidget(self.grid_visible_checkbox)

        # Grid size selector
        grid_size_label = QLabel("Grid Size:")
        toolbar_layout.addWidget(grid_size_label)

        self.grid_size_combo = QComboBox()
        grid_sizes = [8, 16, 24, 32, 48, 64, 128]
        for size in grid_sizes:
            self.grid_size_combo.addItem(f"{size}px", size)

        # Set current grid size
        index = self.grid_size_combo.findData(self.editor.state.camera.grid_size)
        if index >= 0:
            self.grid_size_combo.setCurrentIndex(index)

        self.grid_size_combo.currentIndexChanged.connect(self._on_grid_size_changed)
        toolbar_layout.addWidget(self.grid_size_combo)

        # Snap to grid toggle
        self.snap_checkbox = QCheckBox("Snap to Grid")
        self.snap_checkbox.setChecked(self.editor.state.camera.snap_to_grid)
        self.snap_checkbox.stateChanged.connect(self._on_snap_to_grid_changed)
        toolbar_layout.addWidget(self.snap_checkbox)

        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.VLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        toolbar_layout.addWidget(separator1)

        # Transform tools label
        tools_label = QLabel("Transform:")
        toolbar_layout.addWidget(tools_label)

        # Move tool button (W)
        self.move_tool_btn = QPushButton("⇱ Move (W)")
        self.move_tool_btn.setCheckable(True)
        self.move_tool_btn.setChecked(True)  # Default tool
        self.move_tool_btn.setMinimumHeight(32)
        self.move_tool_btn.clicked.connect(lambda: self._on_transform_tool_clicked('move'))
        toolbar_layout.addWidget(self.move_tool_btn)

        # Rotate tool button (E)
        self.rotate_tool_btn = QPushButton("↻ Rotate (E)")
        self.rotate_tool_btn.setCheckable(True)
        self.rotate_tool_btn.setMinimumHeight(32)
        self.rotate_tool_btn.clicked.connect(lambda: self._on_transform_tool_clicked('rotate'))
        toolbar_layout.addWidget(self.rotate_tool_btn)

        # Scale tool button (R)
        self.scale_tool_btn = QPushButton("⇲ Scale (R)")
        self.scale_tool_btn.setCheckable(True)
        self.scale_tool_btn.setMinimumHeight(32)
        self.scale_tool_btn.clicked.connect(lambda: self._on_transform_tool_clicked('scale'))
        toolbar_layout.addWidget(self.scale_tool_btn)

        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        toolbar_layout.addWidget(separator2)

        # Play button
        self.play_btn = QPushButton("▶ Play (F5)")
        self.play_btn.setProperty("primary", "true")
        self.play_btn.setMinimumHeight(32)
        self.play_btn.clicked.connect(self._on_play_clicked)
        toolbar_layout.addWidget(self.play_btn)

        # Stop button
        self.stop_btn = QPushButton("⏹ Stop (Shift+F5)")
        self.stop_btn.setMinimumHeight(32)
        self.stop_btn.setEnabled(False)  # Disabled until game is running
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        toolbar_layout.addWidget(self.stop_btn)

        toolbar_layout.addStretch()

        # Add toolbar to parent layout
        parent_layout.addWidget(toolbar)

    def _create_status_bar(self, parent_layout):
        """Create status bar for displaying FPS, zoom, and cursor position."""
        status_bar = QWidget()
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(
            self.theme.spacing_small,
            self.theme.spacing_small,
            self.theme.spacing_small,
            self.theme.spacing_small
        )
        status_layout.setSpacing(self.theme.spacing_medium)

        # Apply subtle background
        status_bar.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme.background_mid};
                border-top: 1px solid {self.theme.border_subtle};
            }}
        """)

        # FPS label
        self.fps_label = QLabel("FPS: 60")
        self.fps_label.setMinimumWidth(80)
        status_layout.addWidget(self.fps_label)

        # Separator
        separator1 = QLabel("|")
        separator1.setStyleSheet(f"color: {self.theme.border_subtle};")
        status_layout.addWidget(separator1)

        # Zoom label
        self.zoom_label = QLabel("Zoom: 100%")
        self.zoom_label.setMinimumWidth(100)
        status_layout.addWidget(self.zoom_label)

        # Separator
        separator2 = QLabel("|")
        separator2.setStyleSheet(f"color: {self.theme.border_subtle};")
        status_layout.addWidget(separator2)

        # Cursor position label
        self.cursor_pos_label = QLabel("Cursor: (0, 0)")
        self.cursor_pos_label.setMinimumWidth(150)
        status_layout.addWidget(self.cursor_pos_label)

        status_layout.addStretch()

        # Add status bar to parent layout
        parent_layout.addWidget(status_bar)

        # Initialize FPS timer
        self.fps_timer = QTimer()
        self.fps_timer.timeout.connect(self.update_fps_display)
        self.fps_timer.start(1000)  # Update every second

    # Signal handlers (internal)

    def _on_grid_visibility_changed(self, state):
        """Handle grid visibility checkbox state change."""
        visible = state == Qt.CheckState.Checked.value
        self.grid_visibility_changed.emit(visible)

    def _on_grid_size_changed(self, index):
        """Handle grid size combo box change."""
        new_size = self.grid_size_combo.itemData(index)
        self.grid_size_changed.emit(new_size)

    def _on_snap_to_grid_changed(self, state):
        """Handle snap to grid checkbox state change."""
        snap_enabled = state == Qt.CheckState.Checked.value
        self.snap_to_grid_changed.emit(snap_enabled)

    def _on_transform_tool_clicked(self, tool):
        """Handle transform tool button clicks."""
        self.transform_tool_changed.emit(tool)

    def _on_play_clicked(self):
        """Handle Play button click."""
        self.play_requested.emit()

    def _on_stop_clicked(self):
        """Handle Stop button click."""
        self.stop_requested.emit()

    # Public API

    def get_pygame_widget(self):
        """Get the pygame widget instance."""
        return self.pygame_widget

    def set_transform_tool(self, tool):
        """
        Set the active transform tool and update button states.

        Args:
            tool: 'move', 'rotate', or 'scale'
        """
        self.move_tool_btn.setChecked(tool == 'move')
        self.rotate_tool_btn.setChecked(tool == 'rotate')
        self.scale_tool_btn.setChecked(tool == 'scale')

    def set_play_state(self, is_playing):
        """
        Update play/stop button states.

        Args:
            is_playing: True if game is running, False otherwise
        """
        self.play_btn.setEnabled(not is_playing)
        self.stop_btn.setEnabled(is_playing)

    def update_status(self, fps=None, zoom=None, cursor_pos=None):
        """
        Update status bar information.

        Args:
            fps: FPS value (int) or None to skip
            zoom: Zoom value (float 0.0-inf) or None to skip
            cursor_pos: Tuple of (screen_x, screen_y) or None to skip
        """
        if fps is not None:
            self.fps_label.setText(f"FPS: {fps}")

        if zoom is not None:
            zoom_percent = int(zoom * 100)
            self.zoom_label.setText(f"Zoom: {zoom_percent}%")

        if cursor_pos is not None:
            screen_x, screen_y = cursor_pos
            # Convert screen position to world position
            world_pos = self.editor.state.camera.screen_to_world(Vector2(screen_x, screen_y))
            self.cursor_pos_label.setText(f"Cursor: ({int(world_pos.x)}, {int(world_pos.y)})")

    def update_fps_display(self):
        """Update FPS display (called by timer)."""
        # Calculate approximate FPS based on render timer (16ms = ~60 FPS)
        self.fps_label.setText(f"FPS: ~60")

    def update_zoom_display(self):
        """Update zoom display from current camera state."""
        zoom_percent = int(self.editor.state.camera.zoom * 100)
        self.zoom_label.setText(f"Zoom: {zoom_percent}%")

    def update_cursor_position(self, screen_x, screen_y):
        """
        Update cursor position in status bar.

        Args:
            screen_x: Screen X coordinate
            screen_y: Screen Y coordinate
        """
        world_pos = self.editor.state.camera.screen_to_world(Vector2(screen_x, screen_y))
        self.cursor_pos_label.setText(f"Cursor: ({int(world_pos.x)}, {int(world_pos.y)})")
