"""
PyQt6-based Native Editor for Scribe Engine V2

Proper IDE with docking panels and embedded Pygame viewport.
"""

import sys
import os
import pygame
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QLabel, QLineEdit, QPushButton,
    QDockWidget, QMenuBar, QMenu, QSplitter, QFormLayout, QGroupBox,
    QInputDialog, QMessageBox, QTextEdit, QTabWidget, QStackedWidget, QFrame,
    QGridLayout, QCheckBox, QColorDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QImage, QPixmap, QPainter, QColor

from v2_engine.core.game import Game
from v2_engine.utils.math import Vector2
from v2_engine.editor.editor_state import EditorState
from v2_engine.editor.tools.select_tool import SelectTool
from v2_engine.editor.scene_serializer import SceneSerializer
from v2_engine.editor.theme import EditorTheme, get_theme, set_theme
from v2_engine.editor.command import (
    CommandHistory, MoveCommand, RotateCommand, ScaleCommand,
    SetOriginCommand, DeleteSpriteCommand, AddSpriteCommand, ModifyPropertyCommand
)
from v2_engine.editor.code_editor import CodeEditor
from v2_engine.editor.panels.hierarchy_panel import HierarchyPanel
from v2_engine.editor.panels.gamestate_panel import GameStatePanel
from v2_engine.editor.panels.properties_panel import PropertiesPanel
from v2_engine.editor.panels.viewport_panel import ViewportPanel
from v2_engine.editor.panels.code_panel import CodePanel, SplitCodePanel
from v2_engine.editor.managers.selection_manager import SelectionManager
from v2_engine.editor.managers.playback_manager import PlaybackManager
from v2_engine.editor.managers.scene_manager_ui import SceneManagerUI

# Add shared utils to path
import sys
shared_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'shared')
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from utils.config_manager import add_recent_project


class PygameWidget(QLabel):
    """Widget that displays a Pygame surface as a QImage."""

    def __init__(self, parent=None, editor_window=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Styled by global theme - viewport background
        theme = get_theme()
        self.setStyleSheet(f"background-color: {theme.background_light}; border: 1px solid {theme.border_strong};")
        self.setMouseTracking(True)  # Enable mouse tracking for hover events

        # Store reference to editor window for event callbacks
        self.editor_window = editor_window

        # Initialize Pygame without display (render to surface only)
        pygame.init()
        self.pygame_surface = pygame.Surface((800, 600))

        # Mouse state
        self.mouse_pressed = False
        self.last_mouse_pos = None
        self.middle_mouse_pressed = False
        self.space_held = False

    def get_surface(self):
        """Get the Pygame surface for rendering."""
        return self.pygame_surface

    def update_from_surface(self):
        """Convert Pygame surface to QPixmap and display it."""
        # Convert pygame surface to QImage
        width, height = self.pygame_surface.get_size()
        data = pygame.image.tostring(self.pygame_surface, 'RGB')
        qimage = QImage(data, width, height, width * 3, QImage.Format.Format_RGB888)

        # Convert to pixmap and display
        pixmap = QPixmap.fromImage(qimage)
        self.setPixmap(pixmap)

    def resizeEvent(self, event):
        """Handle widget resize."""
        super().resizeEvent(event)
        size = self.size()
        self.pygame_surface = pygame.Surface((size.width(), size.height()))

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_pressed = True
            self.last_mouse_pos = Vector2(event.pos().x(), event.pos().y())
            # Notify editor window of mouse press
            if self.editor_window and hasattr(self.editor_window, 'on_viewport_mouse_press'):
                self.editor_window.on_viewport_mouse_press(event.pos().x(), event.pos().y())
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.middle_mouse_pressed = True
            self.last_mouse_pos = Vector2(event.pos().x(), event.pos().y())

    def mouseDoubleClickEvent(self, event):
        """Handle mouse double-click events."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Notify editor window of double-click
            if self.editor_window and hasattr(self.editor_window, 'on_viewport_double_click'):
                self.editor_window.on_viewport_double_click(event.pos().x(), event.pos().y())

    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        current_pos = Vector2(event.pos().x(), event.pos().y())

        # Update cursor position in status bar
        if self.editor_window and hasattr(self.editor_window, 'update_cursor_position'):
            self.editor_window.update_cursor_position(current_pos.x, current_pos.y)

        # Middle mouse drag OR Space + left mouse drag - pan camera
        if (self.middle_mouse_pressed or (self.space_held and self.mouse_pressed)) and self.last_mouse_pos:
            if self.editor_window and hasattr(self.editor_window, 'on_viewport_camera_pan'):
                delta = current_pos - self.last_mouse_pos
                self.editor_window.on_viewport_camera_pan(delta.x, delta.y)

        # Left mouse drag (without space) - move sprite
        elif self.mouse_pressed and not self.space_held and self.last_mouse_pos:
            if self.editor_window and hasattr(self.editor_window, 'on_viewport_mouse_drag'):
                self.editor_window.on_viewport_mouse_drag(current_pos.x, current_pos.y)

        self.last_mouse_pos = current_pos

    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_pressed = False
            # Notify editor window that drag ended (with position for box selection)
            if self.editor_window and hasattr(self.editor_window, 'on_viewport_mouse_release'):
                pos = event.position()
                self.editor_window.on_viewport_mouse_release(pos.x(), pos.y())
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.middle_mouse_pressed = False

    def wheelEvent(self, event):
        """Handle mouse wheel events for zoom."""
        if self.editor_window and hasattr(self.editor_window, 'on_viewport_wheel'):
            delta = event.angleDelta().y()
            pos = event.position()  # Use position() instead of pos() in PyQt6
            self.editor_window.on_viewport_wheel(delta, pos.x(), pos.y())


class EditorWindow(QMainWindow):
    """Main editor window with PyQt6."""

    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path

        # Add to recent projects
        add_recent_project(project_path)

        # Load or create editor theme
        theme_path = os.path.join(project_path, 'editor_theme.json')
        self.theme = EditorTheme.load(theme_path)
        set_theme(self.theme)

        # Apply theme stylesheet globally
        self.setStyleSheet(self.theme.get_stylesheet())

        # Initialize game
        self.game = Game(project_path, editor_mode=True)
        if not self.game.initialize():
            raise RuntimeError("Failed to initialize game")

        # Initialize component registry
        from v2_engine.components.component_registry import get_component_registry
        component_registry = get_component_registry()
        component_registry.initialize(project_path)

        # Editor state
        self.state = EditorState()
        self.select_tool = SelectTool()
        self.scene_serializer = SceneSerializer()
        self.play_process = None  # Track running game process
        self.transform_tool = 'move'  # Default transform tool

        # Command history for undo/redo
        self.command_history = CommandHistory(max_history=50)

        # Selection manager
        self.selection_manager = SelectionManager(self)
        self.selection_manager.selection_changed.connect(self._on_selection_changed)

        # Playback manager
        self.playback_manager = PlaybackManager(self)
        self.playback_manager.playback_started.connect(self._on_playback_started)
        self.playback_manager.playback_stopped.connect(self._on_playback_stopped)

        # Scene manager UI
        self.scene_manager_ui = SceneManagerUI(self)
        self.scene_manager_ui.scene_switched.connect(self._on_scene_switched)
        self.scene_manager_ui.scene_created.connect(self._on_scene_created)
        self.scene_manager_ui.scene_saved.connect(self._on_scene_saved)

        # Gizmo interaction state
        self.gizmo_dragging = False
        self.gizmo_drag_start = None
        self.gizmo_drag_type = None  # 'rotate' or 'scale'
        self.scale_handle_type = None  # Which scale handle ('corner', 'top', 'bottom', 'left', 'right')
        self.initial_rotation = 0
        self.initial_scale = Vector2(1, 1)

        # Store initial values for undo/redo
        self.drag_start_position = None
        self.drag_start_rotation = None
        self.drag_start_scale = None
        self.drag_start_origin = None

        # Setup UI (creates Pygame widget and screen)
        self.setup_ui()

        # Set game's screen to the pygame widget's surface
        self.game.screen = self.pygame_widget.get_surface()

        # Perform initial scene transition (after screen exists)
        if self.game.scene_manager:
            self.game.scene_manager._perform_scene_transition()

        # Register any persistent entities from the initial scene
        self.register_persistent_entities_from_current_scene()

        # Update UI with loaded scene
        self.update_hierarchy()
        self.refresh_code_view()
        self.update_gamestate_panel()

        # Setup timer for rendering
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self.update_viewport)
        self.render_timer.start(16)  # ~60 FPS

        # Setup timer for monitoring play process
        self.play_monitor_timer = QTimer()
        self.play_monitor_timer.timeout.connect(self.check_play_process)
        self.play_monitor_timer.start(1000)  # Check every second

        # Selection state
        self.selected_sprite = None  # Primary selected sprite (for backward compatibility)
        self.selected_sprites = []  # List of all selected sprites (for multi-select)
        self.copied_sprite = None  # For copy/paste

        # Scene file tracking
        self.current_scene_file = None  # Path to currently loaded scene file

        # Box selection state
        self.box_select_start = None  # Screen position where box selection started
        self.box_select_dragging = False  # Whether currently box selecting

        # Scale feedback state
        self.scale_feedback_mouse_pos = None  # Mouse position during scaling for feedback display

        # Play mode state
        self.is_playing = False

    def setup_ui(self):
        """Setup the main UI layout."""
        self.setWindowTitle("Scribe Engine V2 - Editor")
        self.setGeometry(100, 100, 1600, 900)

        # Enable keyboard event handling
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Create menu bar
        self.create_menu_bar()

        # Create central widget with tabs (Visual/Code/Split)
        self.create_center_panel()

        # Create docked panels
        self._create_hierarchy_panel_new()  # New modular version
        self._create_properties_panel_new()  # New modular version
        self._create_gamestate_panel_new()  # New modular version

    def create_center_panel(self):
        """Create the center panel with Visual/Code/Split tabs."""
        # Container widget
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab bar
        tab_bar = QTabWidget()
        tab_bar.setTabPosition(QTabWidget.TabPosition.North)
        tab_bar.currentChanged.connect(self.on_view_mode_changed)

        # Visual tab - Pygame viewport with toolbar (using ViewportPanel)
        # Create pygame widget first
        self.pygame_widget = PygameWidget(editor_window=self)

        # Create viewport panel with pygame widget
        self.viewport_panel = ViewportPanel(self, self.pygame_widget, self.theme)

        # Wire up signals
        self.viewport_panel.transform_tool_changed.connect(self.set_transform_tool)
        self.viewport_panel.grid_visibility_changed.connect(self.toggle_grid_visibility)
        self.viewport_panel.grid_size_changed.connect(self._on_grid_size_changed_from_panel)
        self.viewport_panel.snap_to_grid_changed.connect(self._on_snap_to_grid_changed_from_panel)
        self.viewport_panel.play_requested.connect(self.play_scene)
        self.viewport_panel.stop_requested.connect(self.stop_play)

        # Keep backward compatible references for existing code
        self.grid_visible_checkbox = self.viewport_panel.grid_visible_checkbox
        self.grid_size_combo = self.viewport_panel.grid_size_combo
        self.snap_checkbox = self.viewport_panel.snap_checkbox
        self.move_tool_btn = self.viewport_panel.move_tool_btn
        self.rotate_tool_btn = self.viewport_panel.rotate_tool_btn
        self.scale_tool_btn = self.viewport_panel.scale_tool_btn
        self.play_btn = self.viewport_panel.play_btn
        self.stop_btn = self.viewport_panel.stop_btn
        self.fps_label = self.viewport_panel.fps_label
        self.zoom_label = self.viewport_panel.zoom_label
        self.cursor_pos_label = self.viewport_panel.cursor_pos_label

        tab_bar.addTab(self.viewport_panel, "Visual")

        # Code tab - Professional code editor with file navigator (using CodePanel)
        self.code_panel = CodePanel(self, self.theme, self.project_path)

        # Wire up signals
        self.code_panel.file_saved.connect(self.on_code_saved)
        self.code_panel.file_saved_and_reload.connect(self.on_code_saved_and_reload)
        self.code_panel.file_selected.connect(self.on_navigator_file_selected)

        # Keep backward compatible references
        self.file_navigator = self.code_panel.file_navigator
        self.code_editor = self.code_panel.code_editor

        tab_bar.addTab(self.code_panel, "Code")

        # Split tab - Scene view and code editor side by side (using SplitCodePanel)
        split_widget = QWidget()
        split_layout = QHBoxLayout(split_widget)
        split_layout.setContentsMargins(0, 0, 0, 0)
        split_layout.setSpacing(0)

        # Create main splitter for scene and code sections
        main_split_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Create second pygame widget for split view
        self.pygame_widget_split = PygameWidget(editor_window=self)
        main_split_splitter.addWidget(self.pygame_widget_split)

        # Split code panel
        self.split_code_panel = SplitCodePanel(self, self.theme, self.project_path)

        # Wire up signals
        self.split_code_panel.file_saved.connect(self.on_code_saved)
        self.split_code_panel.file_saved_and_reload.connect(self.on_code_saved_and_reload)
        self.split_code_panel.switch_to_instance_requested.connect(self.on_split_switch_to_instance)

        # Keep backward compatible references
        self.split_code_tabs = self.split_code_panel.split_code_tabs

        main_split_splitter.addWidget(self.split_code_panel)

        # Set initial sizes for main splitter (50/50 split)
        main_split_splitter.setSizes([500, 500])

        split_layout.addWidget(main_split_splitter)
        tab_bar.addTab(split_widget, "Split")

        # Store tab bar reference for view mode switching
        self.view_tab_bar = tab_bar

        layout.addWidget(tab_bar)

        # Note: Status bar is now part of ViewportPanel (Visual tab only)

        self.setCentralWidget(container)

        # Store reference to tab widget
        self.view_tab_widget = tab_bar
        self.current_view_mode = "Visual"

    def on_view_mode_changed(self, index):
        """Handle view mode tab change."""
        modes = ["Visual", "Code", "Split"]
        self.current_view_mode = modes[index] if index < len(modes) else "Visual"
        print(f"[Editor] View mode changed to: {self.current_view_mode}")

        # Refresh code views when switching to Code or Split
        if self.current_view_mode in ["Code", "Split"]:
            self.refresh_code_view()

    def keyPressEvent(self, event):
        """Handle key press events."""
        modifiers = event.modifiers()

        # Undo/Redo shortcuts
        if event.key() == Qt.Key.Key_Z and modifiers == Qt.KeyboardModifier.ControlModifier:
            # Ctrl+Z - Undo
            self.undo()
            event.accept()
        elif event.key() == Qt.Key.Key_Z and modifiers == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
            # Ctrl+Shift+Z - Redo
            self.redo()
            event.accept()
        elif event.key() == Qt.Key.Key_Y and modifiers == Qt.KeyboardModifier.ControlModifier:
            # Ctrl+Y - Redo (alternative)
            self.redo()
            event.accept()
        elif event.key() == Qt.Key.Key_Space:
            self.pygame_widget.space_held = True
            self.pygame_widget_split.space_held = True
            event.accept()
        elif event.key() == Qt.Key.Key_G:
            # Toggle grid visibility
            self.toggle_grid_visibility()
            event.accept()
        elif event.key() == Qt.Key.Key_W:
            # Move tool
            self.set_transform_tool('move')
            event.accept()
        elif event.key() == Qt.Key.Key_E:
            # Rotate tool
            self.set_transform_tool('rotate')
            event.accept()
        elif event.key() == Qt.Key.Key_R:
            # Scale tool
            self.set_transform_tool('scale')
            event.accept()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """Handle key release events."""
        if event.key() == Qt.Key.Key_Space:
            self.pygame_widget.space_held = False
            self.pygame_widget_split.space_held = False
            event.accept()
        else:
            super().keyReleaseEvent(event)

    def closeEvent(self, event):
        """Handle window close - cleanup game process."""
        if self.play_process and self.play_process.poll() is None:
            print("[Editor] Stopping game before closing editor...")
            self.stop_play()
        event.accept()

    def create_menu_bar(self):
        """Create the top menu bar."""
        from PyQt6.QtGui import QKeySequence

        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        save_action = QAction("Save Scene", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.save_scene)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        # Save/Load game state
        save_game_action = QAction("Save Game...", self)
        save_game_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_game_action.triggered.connect(self.open_save_dialog)
        file_menu.addAction(save_game_action)

        load_game_action = QAction("Load Game...", self)
        load_game_action.setShortcut(QKeySequence("Ctrl+Shift+L"))
        load_game_action.triggered.connect(self.open_load_dialog)
        file_menu.addAction(load_game_action)

        file_menu.addSeparator()

        settings_action = QAction("Project Settings...", self)
        settings_action.triggered.connect(self.open_project_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        copy_action = QAction("Copy Sprite", self)
        copy_action.setShortcut(QKeySequence("Ctrl+C"))
        copy_action.triggered.connect(self.copy_sprite)
        edit_menu.addAction(copy_action)

        paste_action = QAction("Paste Sprite", self)
        paste_action.setShortcut(QKeySequence("Ctrl+V"))
        paste_action.triggered.connect(self.paste_sprite)
        edit_menu.addAction(paste_action)

        edit_menu.addSeparator()

        delete_action = QAction("Delete Sprite", self)
        delete_action.setShortcut(QKeySequence("Delete"))
        delete_action.triggered.connect(lambda: self.delete_selected_sprite(confirm=False))
        edit_menu.addAction(delete_action)

        # Scene menu
        scene_menu = menubar.addMenu("Scene")

        new_scene_action = QAction("New Scene...", self)
        new_scene_action.triggered.connect(self.create_new_scene)
        scene_menu.addAction(new_scene_action)

        scene_menu.addSeparator()

        # Dynamic scene list will be added here
        self.scene_menu = scene_menu
        self.update_scene_menu()

        # View menu
        view_menu = menubar.addMenu("View")

        reset_camera_action = QAction("Reset Camera", self)
        reset_camera_action.triggered.connect(self.reset_camera)
        view_menu.addAction(reset_camera_action)

        # Play menu
        play_menu = menubar.addMenu("Play")

        play_action = QAction("▶ Play Scene", self)
        play_action.setShortcut(QKeySequence("F5"))
        play_action.triggered.connect(self.play_scene)
        play_menu.addAction(play_action)

        stop_action = QAction("⏹ Stop Game", self)
        stop_action.setShortcut(QKeySequence("Shift+F5"))
        stop_action.triggered.connect(self.stop_play)
        play_menu.addAction(stop_action)

    def create_hierarchy_panel(self):
        """Create the left panel with unified collapsible sections."""
        from PyQt6.QtWidgets import QScrollArea

        dock = QDockWidget("Project", self)
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        dock.setMinimumWidth(324)

        # Scrollable container
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Main container with unified layout
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(self.theme.spacing_small, self.theme.spacing_small,
                                 self.theme.spacing_small, self.theme.spacing_small)
        layout.setSpacing(self.theme.spacing_medium)

        # === Current Scene Section (Always expanded, shows scene context) ===
        self.scene_section_header = self.create_collapsible_header("Scene: Loading...", collapsed=False, add_button=False)
        layout.addWidget(self.scene_section_header)

        self.scene_section_body = QWidget()
        scene_body_layout = QVBoxLayout(self.scene_section_body)
        scene_body_layout.setContentsMargins(self.theme.spacing_medium, self.theme.spacing_small,
                                            self.theme.spacing_small, self.theme.spacing_small)
        scene_body_layout.setSpacing(self.theme.spacing_small)

        # Entities subheader with + button
        self.entities_header = self.create_collapsible_header("Entities", collapsed=False, add_button=True, add_callback=self.show_add_object_dialog)
        scene_body_layout.addWidget(self.entities_header)

        # Entities body (hierarchy tree)
        self.entities_body = QWidget()
        entities_body_layout = QVBoxLayout(self.entities_body)
        entities_body_layout.setContentsMargins(self.theme.spacing_medium, self.theme.spacing_small,
                                               self.theme.spacing_small, self.theme.spacing_small)
        entities_body_layout.setSpacing(self.theme.spacing_small)

        # Hierarchy tree
        self.hierarchy_tree = QTreeWidget()
        self.hierarchy_tree.setHeaderHidden(True)
        self.hierarchy_tree.itemClicked.connect(self.on_hierarchy_item_clicked)
        entities_body_layout.addWidget(self.hierarchy_tree)

        # Delete button
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(lambda: self.delete_selected_sprite(confirm=True))
        entities_body_layout.addWidget(delete_button)

        scene_body_layout.addWidget(self.entities_body)

        layout.addWidget(self.scene_section_body)

        # Link headers to bodies
        self.scene_section_header.section_body = self.scene_section_body
        self.entities_header.section_body = self.entities_body

        # === Assets Section (Collapsible) ===
        self.assets_section_header = self.create_collapsible_header("Assets", collapsed=True, add_button=False)
        layout.addWidget(self.assets_section_header)

        self.assets_section_body = QWidget()
        assets_body_layout = QVBoxLayout(self.assets_section_body)
        assets_body_layout.setContentsMargins(self.theme.spacing_medium, self.theme.spacing_small,
                                             self.theme.spacing_small, self.theme.spacing_small)
        assets_body_layout.setSpacing(self.theme.spacing_small)

        # Asset browser tree
        self.asset_tree = QTreeWidget()
        self.asset_tree.setHeaderHidden(True)
        self.asset_tree.itemClicked.connect(self.on_asset_clicked)
        assets_body_layout.addWidget(self.asset_tree)

        # Asset preview
        preview_label = QLabel("Preview:")
        preview_label.setProperty("type", "caption")
        assets_body_layout.addWidget(preview_label)

        self.asset_preview = QLabel()
        self.asset_preview.setMinimumHeight(100)
        self.asset_preview.setMaximumHeight(200)
        self.asset_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.asset_preview.setStyleSheet(f"border: 1px solid {self.theme.border_strong}; background-color: {self.theme.background_dark};")
        self.asset_preview.setText("No preview")
        assets_body_layout.addWidget(self.asset_preview)

        # Assign button
        self.assign_asset_btn = QPushButton("Assign to Selected Sprite")
        self.assign_asset_btn.setEnabled(False)
        self.assign_asset_btn.clicked.connect(self.assign_asset_to_sprite)
        assets_body_layout.addWidget(self.assign_asset_btn)

        self.assets_section_body.setVisible(False)  # Start collapsed
        layout.addWidget(self.assets_section_body)

        # Link header to body
        self.assets_section_header.section_body = self.assets_section_body

        # === All Scenes Section (Collapsible) ===
        self.scenes_section_header = self.create_collapsible_header("All Scenes", collapsed=True, add_button=True, add_callback=self.create_new_scene)
        layout.addWidget(self.scenes_section_header)

        self.scenes_section_body = QWidget()
        scenes_body_layout = QVBoxLayout(self.scenes_section_body)
        scenes_body_layout.setContentsMargins(self.theme.spacing_medium, self.theme.spacing_small,
                                             self.theme.spacing_small, self.theme.spacing_small)
        scenes_body_layout.setSpacing(self.theme.spacing_small)

        # Scene list
        self.scene_list = QTreeWidget()
        self.scene_list.setHeaderHidden(True)
        self.scene_list.itemClicked.connect(self.on_scene_list_clicked)
        scenes_body_layout.addWidget(self.scene_list)

        self.scenes_section_body.setVisible(False)  # Start collapsed
        layout.addWidget(self.scenes_section_body)

        # Link header to body
        self.scenes_section_header.section_body = self.scenes_section_body

        # Add stretch to push everything to top
        layout.addStretch()

        scroll_area.setWidget(container)
        dock.setWidget(scroll_area)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

        self.update_hierarchy()
        self.update_scene_list()
        self.update_asset_browser()

        # Track selected asset
        self.selected_asset_path = None

    def _create_hierarchy_panel_new(self):
        """Create the hierarchy panel using the new modular HierarchyPanel class."""
        # Create the new panel
        self.hierarchy_panel = HierarchyPanel(self, self.theme)

        # Wire up signals
        self.hierarchy_panel.sprite_selected.connect(self.on_hierarchy_item_clicked_new)
        self.hierarchy_panel.sprite_delete_requested.connect(lambda: self.delete_selected_sprite(confirm=True))
        self.hierarchy_panel.asset_selected.connect(self._on_asset_selected)
        self.hierarchy_panel.asset_assign_requested.connect(self.assign_asset_to_sprite)
        self.hierarchy_panel.scene_selected.connect(self.switch_to_scene)
        self.hierarchy_panel.add_object_requested.connect(self.show_add_object_dialog)
        self.hierarchy_panel.create_scene_requested.connect(self.create_new_scene)

        # Add to main window
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.hierarchy_panel)

        # Initialize data
        self.hierarchy_panel.update_hierarchy(self.game)
        self.hierarchy_panel.update_scenes(self._get_scenes_config(), self.game.scene_manager.current_scene if self.game.scene_manager else None)
        self.hierarchy_panel.update_assets(self.project_path)

        # Keep references for backward compatibility
        self.hierarchy_tree = self.hierarchy_panel.hierarchy_tree
        self.asset_tree = self.hierarchy_panel.asset_tree
        self.asset_preview = self.hierarchy_panel.asset_preview
        self.assign_asset_btn = self.hierarchy_panel.assign_asset_btn
        self.scene_list = self.hierarchy_panel.scene_list
        self.scene_section_header = self.hierarchy_panel.scene_section_header

    def _get_scenes_config(self):
        """Get scenes configuration from project config."""
        return self.scene_manager_ui.get_scenes_config()

    def on_hierarchy_item_clicked_new(self, sprite):
        """Handle sprite selection from new hierarchy panel."""
        self.selected_sprite = sprite
        self.state.selected_sprite = sprite
        self.update_properties_panel(sprite)

    def _on_asset_selected(self, file_path):
        """Handle asset selection from new hierarchy panel."""
        self.selected_asset_path = file_path
        # Enable assign button if sprite is selected
        if self.selected_sprite:
            self.hierarchy_panel.enable_asset_assign(True)
        else:
            self.hierarchy_panel.enable_asset_assign(False)

    # DEPRECATED: Toolbar and status bar creation moved to ViewportPanel
    # Old methods removed - see v2_engine/editor/panels/viewport_panel.py

    def update_fps_display(self):
        """Update FPS display in status bar."""
        self.viewport_panel.update_fps_display()

    def update_status_bar(self):
        """Update status bar information."""
        self.viewport_panel.update_zoom_display()

    def update_cursor_position(self, screen_x, screen_y):
        """Update cursor position in status bar."""
        self.viewport_panel.update_cursor_position(screen_x, screen_y)

    def create_collapsible_header(self, title, collapsed=False, add_button=False, add_callback=None):
        """
        Create a collapsible section header.

        Args:
            title: Header text
            collapsed: Whether section starts collapsed
            add_button: Whether to show "+" button
            add_callback: Callback for "+" button click

        Returns:
            QWidget: Header widget
        """
        from PyQt6.QtWidgets import QHBoxLayout, QWidget
        from PyQt6.QtGui import QFont

        header_widget = QWidget()
        header_widget.setCursor(Qt.CursorShape.PointingHandCursor)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(self.theme.spacing_small)

        # Collapse indicator
        indicator = QLabel("▶" if collapsed else "▼")
        indicator.setFont(QFont("Segoe UI", 12))
        indicator.setFixedSize(20, 20)
        indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(indicator)

        # Store indicator reference for later updates
        header_widget.collapse_indicator = indicator

        # Title label
        title_label = QLabel(title)
        title_label.setProperty("type", "header")
        header_layout.addWidget(title_label)

        # Store title label reference for updates (e.g., scene name)
        header_widget.title_label = title_label

        header_layout.addStretch()

        # Optional "+" button
        if add_button and add_callback:
            add_btn = QPushButton("+")
            add_btn.setFixedSize(24, 24)
            add_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.theme.accent_primary};
                    color: white;
                    font-weight: bold;
                    font-size: 16px;
                    border: none;
                    border-radius: 12px;
                    padding: 0px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: {self.theme.accent_hover};
                }}
            """)
            add_btn.setToolTip(f"Add {title}")
            add_btn.clicked.connect(add_callback)

            # Prevent click from propagating to header (which toggles collapse)
            add_btn.clicked.connect(lambda: None)

            header_layout.addWidget(add_btn)

        # Store collapsed state and body reference
        header_widget.collapsed = collapsed
        header_widget.section_body = None  # Will be set after creation

        # Make header clickable to toggle collapse
        def toggle_section(event):
            # Don't toggle if clicking the + button
            if add_button and add_callback:
                clicked_widget = header_widget.childAt(event.pos())
                if isinstance(clicked_widget, QPushButton):
                    return

            header_widget.collapsed = not header_widget.collapsed
            indicator.setText("▶" if header_widget.collapsed else "▼")

            # Toggle body visibility if reference is set
            if header_widget.section_body:
                header_widget.section_body.setVisible(not header_widget.collapsed)

        header_widget.mousePressEvent = toggle_section

        return header_widget

    def create_properties_panel(self):
        """Create the right properties panel."""
        from PyQt6.QtWidgets import QScrollArea

        dock = QDockWidget("Properties", self)
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        dock.setMinimumWidth(416)  # Wider to avoid cutoff text

        # Scrollable container
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Container widget inside scroll area
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)

        self.properties_label = QLabel("No object selected")
        layout.addWidget(self.properties_label)

        # Property form
        self.properties_form = QFormLayout()
        layout.addLayout(self.properties_form)

        layout.addStretch()

        scroll_area.setWidget(container)
        dock.setWidget(scroll_area)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

    def _create_properties_panel_new(self):
        """Create the properties panel using the new modular PropertiesPanel class."""
        # Create the new panel
        self.properties_panel = PropertiesPanel(self)

        # Add to main window
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_panel)

        # Keep references for backward compatibility
        self.properties_label = self.properties_panel.properties_label
        self.properties_form = self.properties_panel.properties_form

    def create_gamestate_panel(self):
        """Create the GameState debug panel."""
        from PyQt6.QtWidgets import QScrollArea, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QPushButton

        dock = QDockWidget("Game State", self)
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.BottomDockWidgetArea)

        # Container widget
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)

        # Info label
        info_label = QLabel("Global game state and persistent entities")
        info_label.setProperty("type", "caption")  # Uses theme caption style
        layout.addWidget(info_label)

        # Tree widget to display state
        self.gamestate_tree = QTreeWidget()
        self.gamestate_tree.setHeaderLabels(["Key", "Value"])
        self.gamestate_tree.setAlternatingRowColors(True)
        layout.addWidget(self.gamestate_tree)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.update_gamestate_panel)
        layout.addWidget(refresh_btn)

        dock.setWidget(container)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)

        # Initial update
        self.update_gamestate_panel()

    def update_gamestate_panel(self):
        """Update the GameState panel with current state."""
        # Delegate to new gamestate panel
        if hasattr(self, 'gamestate_panel'):
            self.gamestate_panel.update()

    def _create_gamestate_panel_new(self):
        """Create the GameState panel using the new modular GameStatePanel class."""
        # Create the new panel
        self.gamestate_panel = GameStatePanel(self, self.theme)

        # Add to main window
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.gamestate_panel)

        # Initialize data
        self.gamestate_panel.update()

        # Keep references for backward compatibility
        self.gamestate_tree = self.gamestate_panel.gamestate_tree

    def refresh_code_view(self):
        """Load and display the current scene file in code view."""
        self.code_panel.refresh_scene_code(self.game)
        # Sync current scene file reference
        self.current_scene_file = self.code_panel.get_current_scene_file()

    def save_code_and_reload(self):
        """Save code editor contents to file and reload the scene."""
        if not self.game.scene_manager or not self.game.scene_manager.current_scene:
            print("[Editor] No scene to save")
            return

        scene_name = self.game.scene_manager.current_scene

        # Find scene file path
        import json
        config_path = os.path.join(self.project_path, '2d_project.json')

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

            scene_file = None
            for scene_info in config.get('scenes', {}).get('scenes', []):
                if scene_info['name'] == scene_name:
                    scene_file = os.path.join(self.project_path, scene_info['file'])
                    break

            if not scene_file:
                print("[Editor] Scene file not found in config")
                return

            # Save camera position
            old_camera_pos = Vector2(self.state.camera.position.x, self.state.camera.position.y)
            old_camera_zoom = self.state.camera.zoom

            # Get code from whichever editor is currently visible
            if self.current_view_mode == "Code":
                code = self.code_editor.toPlainText()
            elif self.current_view_mode == "Split":
                code = self.code_editor_split.toPlainText()
            else:
                # Visual mode - shouldn't happen, but use main editor
                code = self.code_editor.toPlainText()

            # Write code to file
            with open(scene_file, 'w') as f:
                f.write(code)
            print(f"[Editor] Saved code to: {scene_file}")

            # Reload the scene module
            self.reload_scene(scene_name)

            # Restore camera
            self.state.camera.position = old_camera_pos
            self.state.camera.zoom = old_camera_zoom

            # Update UI
            self.update_hierarchy()
            self.update_properties_panel(None)
            self.selected_sprite = None
            self.state.selected_sprite = None

            print("[Editor] Scene reloaded successfully")

        except Exception as e:
            print(f"[Editor] Error saving/reloading code: {e}")
            import traceback
            traceback.print_exc()

    def reload_scene(self, scene_name):
        """Reload a scene from disk."""
        import importlib
        import sys

        # Find the scene module
        scene_module_name = None
        for key in sys.modules.keys():
            if scene_name in key and 'scenes' in key:
                scene_module_name = key
                break

        if scene_module_name:
            # Reload the module
            module = sys.modules[scene_module_name]
            importlib.reload(module)
            print(f"[Editor] Reloaded module: {scene_module_name}")

        # Re-register the scene
        self.game.scene_manager.scenes.clear()
        self.game._load_scenes()

        # Transition to reloaded scene
        self.game.scene_manager.load_scene(scene_name)
        self.game.scene_manager._perform_scene_transition()

    def update_hierarchy(self):
        """Update the hierarchy tree with scene objects."""
        # Delegate to new hierarchy panel
        if hasattr(self, 'hierarchy_panel'):
            self.hierarchy_panel.update_hierarchy(self.game)

    def on_hierarchy_item_clicked(self, item, column):
        """Handle hierarchy item selection."""
        sprite = item.data(0, Qt.ItemDataRole.UserRole)
        if sprite:
            self.selected_sprite = sprite
            self.state.selected_sprite = sprite
            self.update_properties_panel(sprite)

    def update_properties_panel(self, sprite):
        """Update properties panel with sprite data."""
        # Delegate to new properties panel
        if hasattr(self, 'properties_panel'):
            self.properties_panel.update_properties_panel(sprite)
            return

    def update_properties_panel_multi(self, sprites):
        """
        Update properties panel for multiple selected sprites.

        Args:
            sprites: List of selected sprites
        """
        from PyQt6.QtWidgets import QPushButton

        # Clear existing form
        while self.properties_form.count():
            child = self.properties_form.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not sprites:
            self.update_properties_panel(None)
            return

        # Show multi-select heading
        count = len(sprites)
        self.properties_label.setText(f"Multiple Objects ({count} selected)")

        # Disable assign asset button for multi-select
        if hasattr(self, 'assign_asset_btn'):
            self.assign_asset_btn.setEnabled(False)

        # Add info message
        info_label = QLabel(f"Select a single sprite to edit properties.\n{count} sprites selected.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"color: {self.theme.text_secondary}; padding: {self.theme.spacing_medium}px;")
        self.properties_form.addRow("", info_label)

        # Add "Deselect All" button
        deselect_btn = QPushButton("Deselect All")
        deselect_btn.clicked.connect(self.deselect_all)
        self.properties_form.addRow("", deselect_btn)

        # List selected sprites
        sprites_label = QLabel("Selected sprites:")
        sprites_label.setStyleSheet(f"font-weight: bold; margin-top: {self.theme.spacing_medium}px;")
        self.properties_form.addRow("", sprites_label)

        for sprite in sprites:
            sprite_name = getattr(sprite, 'name', sprite.__class__.__name__)
            sprite_item = QLabel(f"  • {sprite_name}")
            sprite_item.setStyleSheet(f"color: {self.theme.text_secondary};")
            self.properties_form.addRow("", sprite_item)

    def add_components_section(self, sprite):
        """Add components section to properties panel."""
        from PyQt6.QtWidgets import QFrame, QPushButton, QHBoxLayout, QWidget
        from v2_engine.editor.widgets.component_card import ComponentCard

        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.properties_form.addRow(separator)

        # Header with inline "+" button
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(self.theme.spacing_small)

        # Components header (now using "Behaviors" terminology)
        components_label = QLabel("Behaviors")
        components_label.setProperty("type", "header")  # Uses theme header style
        header_layout.addWidget(components_label)

        header_layout.addStretch()

        # Add "+" button inline with header
        add_btn = QPushButton("+")
        add_btn.setFixedSize(28, 28)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.accent_primary};
                color: white;
                font-weight: bold;
                font-size: 18px;
                border: none;
                border-radius: 14px;
                padding: 0px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {self.theme.accent_hover};
            }}
        """)
        add_btn.setToolTip("Add Behavior")
        add_btn.clicked.connect(lambda: self.show_add_component_dialog(sprite))
        header_layout.addWidget(add_btn)

        self.properties_form.addRow(header_container)

        # Display existing components using ComponentCard
        if hasattr(sprite, 'components') and sprite.components:
            for component_type, component in sprite.components.items():
                # Create component card (will default to collapsed)
                card = ComponentCard(component, sprite, self)

                # Connect signals
                card.remove_requested.connect(lambda comp_type=component.__class__: self.remove_component_from_sprite(sprite, comp_type))
                card.property_changed.connect(lambda prop_name, value, c=component, s=sprite: self.on_component_property_changed(c, prop_name, value, s))
                card.edit_code_requested.connect(self.on_edit_behavior_code)

                # Add to form
                self.properties_form.addRow(card)

    def add_component_widget(self, sprite, component):
        """Add a widget displaying a single component with its properties."""
        from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton

        # Container for component
        component_frame = QFrame()
        component_frame.setStyleSheet(f"QFrame {{ background-color: {self.theme.background_light}; border: 1px solid {self.theme.border_subtle}; border-radius: {self.theme.radius_medium}px; padding: {self.theme.spacing_small}px; }}")
        component_layout = QVBoxLayout(component_frame)
        component_layout.setContentsMargins(self.theme.spacing_small, self.theme.spacing_small, self.theme.spacing_small, self.theme.spacing_small)

        # Header with component name and remove button
        header_layout = QHBoxLayout()

        component_name = component.__class__.__name__
        name_label = QLabel(component_name)
        name_label.setProperty("type", "header")  # Uses theme header style
        header_layout.addWidget(name_label)

        header_layout.addStretch()

        # Remove button
        remove_btn = QPushButton("×")
        remove_btn.setMaximumWidth(25)
        remove_btn.setMaximumHeight(25)
        remove_btn.setStyleSheet(f"QPushButton {{ background-color: {self.theme.error}; color: white; font-weight: bold; }}")
        remove_btn.setToolTip("Remove component")
        remove_btn.clicked.connect(lambda: self.remove_component_from_sprite(sprite, component.__class__))
        header_layout.addWidget(remove_btn)

        component_layout.addLayout(header_layout)

        # Component properties (dynamically generated)
        self.add_component_properties(component, component_layout, sprite)

        self.properties_form.addRow(component_frame)

    def add_component_properties(self, component, layout, sprite):
        """Add editable properties for a component."""
        from PyQt6.QtWidgets import QFormLayout, QLineEdit, QCheckBox, QHBoxLayout

        # Get all component attributes (excluding internal ones)
        props_form = QFormLayout()
        props_form.setContentsMargins(0, 4, 0, 0)

        for attr_name in dir(component):
            # Skip private/protected attributes and methods
            if attr_name.startswith('_') or callable(getattr(component, attr_name)):
                continue
            # Skip base attributes
            if attr_name in ['sprite', 'enabled']:
                continue

            attr_value = getattr(component, attr_name)

            # Create appropriate widget based on type
            if isinstance(attr_value, bool):
                widget = QCheckBox()
                widget.setChecked(attr_value)
                widget.stateChanged.connect(
                    lambda state, c=component, a=attr_name: self.on_component_property_changed(c, a, state == 2, sprite)
                )
            elif isinstance(attr_value, (int, float, str)):
                widget = QLineEdit(str(attr_value))
                # Store original value to detect actual changes
                widget.setProperty('original_value', str(attr_value))
                # Connect editingFinished (fires on Enter or focus loss)
                widget.editingFinished.connect(
                    lambda w=widget, c=component, a=attr_name, s=sprite: self.on_component_property_changed(c, a, w.text(), s, w)
                )
            elif hasattr(attr_value, 'x') and hasattr(attr_value, 'y'):
                # Vector2 type - create two input fields
                vec_layout = QHBoxLayout()
                vec_layout.setContentsMargins(0, 0, 0, 0)
                vec_layout.setSpacing(4)

                x_input = QLineEdit(str(attr_value.x))
                x_input.setPlaceholderText("X")
                x_input.setMaximumWidth(60)
                y_input = QLineEdit(str(attr_value.y))
                y_input.setPlaceholderText("Y")
                y_input.setMaximumWidth(60)

                # Connect both inputs to update Vector2
                x_input.returnPressed.connect(
                    lambda xi=x_input, yi=y_input, c=component, a=attr_name:
                    self.on_vector2_property_changed(c, a, xi.text(), yi.text(), sprite)
                )
                y_input.returnPressed.connect(
                    lambda xi=x_input, yi=y_input, c=component, a=attr_name:
                    self.on_vector2_property_changed(c, a, xi.text(), yi.text(), sprite)
                )

                vec_layout.addWidget(QLabel("X:"))
                vec_layout.addWidget(x_input)
                vec_layout.addWidget(QLabel("Y:"))
                vec_layout.addWidget(y_input)
                vec_layout.addStretch()

                widget = QWidget()
                widget.setLayout(vec_layout)
            else:
                # For complex types, just display as string
                widget = QLabel(str(attr_value))

            props_form.addRow(f"{attr_name}:", widget)

        layout.addLayout(props_form)

    def on_component_property_changed(self, component, attr_name, value, sprite, widget=None):
        """Handle component property changes."""
        # Convert value to appropriate type
        current_value = getattr(component, attr_name)

        if isinstance(current_value, bool):
            new_value = value
        elif isinstance(current_value, int):
            try:
                new_value = int(value)
            except ValueError:
                return
        elif isinstance(current_value, float):
            try:
                new_value = float(value)
            except ValueError:
                return
        else:
            new_value = value

        # Only update if value actually changed
        if current_value != new_value:
            setattr(component, attr_name, new_value)
            print(f"[Editor] Component property changed: {component.__class__.__name__}.{attr_name} = {new_value}")
            self.update_viewport()

            # Update stored value in widget
            if widget:
                widget.setProperty('original_value', str(new_value))

        # Clear focus from widget if provided
        if widget:
            widget.clearFocus()

    def on_vector2_property_changed(self, component, attr_name, x_str, y_str, sprite):
        """Handle Vector2 property changes."""
        from v2_engine.utils.math import Vector2

        try:
            x = float(x_str)
            y = float(y_str)
            new_value = Vector2(x, y)
            setattr(component, attr_name, new_value)
            self.update_viewport()
        except ValueError:
            # Invalid input, ignore
            return

    def remove_component_from_sprite(self, sprite, component_type):
        """Remove a component from the sprite."""
        from PyQt6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            'Remove Component',
            f'Remove {component_type.__name__} component?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            sprite.remove_component(component_type)
            self.update_properties_panel(sprite)
            self.update_viewport()

    def show_add_component_dialog(self, sprite):
        """Show behavior browser dialog to add components."""
        from v2_engine.editor.widgets.behavior_browser import BehaviorBrowserDialog

        dialog = BehaviorBrowserDialog(self, sprite, self.theme, self.project_path)
        dialog.new_behavior_created.connect(self.on_new_behavior_created)

        if dialog.exec():
            # Get selected components
            selected_components = dialog.get_selected_components()

            for component_class, properties in selected_components:
                # Create and add component
                component = component_class(sprite)

                # Apply template properties if any
                for prop, value in properties.items():
                    setattr(component, prop, value)

                sprite.add_component(component)
                print(f"[Editor] Added {component.__class__.__name__} to {sprite.name}")

            # Refresh UI
            self.update_properties_panel(sprite)
            self.update_viewport()

    def get_available_component_types(self):
        """Get list of available component type names."""
        # Return list of available components
        # In the future, this could dynamically discover components
        return ['RigidBody', 'BoxCollider', 'PlatformerController', 'SceneTrigger', 'CameraFollow', 'SpawnPoint']

    def add_component_to_sprite(self, sprite, component_name, dialog):
        """Add a component to the sprite."""
        from v2_engine.components.rigidbody import RigidBody
        from v2_engine.components.box_collider import BoxCollider
        from v2_engine.components.platformer_controller import PlatformerController
        from v2_engine.components.scene_trigger import SceneTrigger
        from v2_engine.components.camera_follow import CameraFollow
        from v2_engine.components.spawn_point import SpawnPoint

        # Component registry
        component_classes = {
            'RigidBody': RigidBody,
            'BoxCollider': BoxCollider,
            'PlatformerController': PlatformerController,
            'SceneTrigger': SceneTrigger,
            'CameraFollow': CameraFollow,
            'SpawnPoint': SpawnPoint,
            # Future components will be added here
        }

        if component_name in component_classes:
            component_class = component_classes[component_name]

            # Check if sprite already has this component
            if sprite.has_component(component_class):
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    'Component Already Exists',
                    f'Sprite already has a {component_name} component.'
                )
                return

            # Create and add component
            component = component_class(sprite)
            sprite.add_component(component)

            dialog.accept()
            self.update_properties_panel(sprite)
            self.update_viewport()
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                'Unknown Component',
                f'Component type "{component_name}" not found.'
            )

    def show_scene_background_properties(self):
        """Show scene background properties when no sprite is selected."""
        if not self.game.scene_manager or not self.game.scene_manager.current_scene:
            return

        scene = self.game.scene_manager.scenes[self.game.scene_manager.current_scene]

        # Background Color
        from PyQt6.QtWidgets import QPushButton, QColorDialog
        from PyQt6.QtGui import QColor

        color_container = QWidget()
        color_layout = QHBoxLayout(color_container)
        color_layout.setContentsMargins(0, 0, 0, 0)

        # Color preview button
        bg_color = scene.background_color
        color_btn = QPushButton()
        color_btn.setStyleSheet(f"background-color: rgb({bg_color[0]}, {bg_color[1]}, {bg_color[2]}); min-height: 25px;")
        color_btn.setMaximumWidth(100)
        color_btn.clicked.connect(self.pick_background_color)
        color_layout.addWidget(color_btn)

        # Color value label
        color_label = QLabel(f"RGB({bg_color[0]}, {bg_color[1]}, {bg_color[2]})")
        color_layout.addWidget(color_label)
        color_layout.addStretch()

        self.properties_form.addRow("Background Color:", color_container)

        # Background Image
        bg_image = scene.background_image or "None"
        image_label = QLabel(bg_image)
        image_label.setWordWrap(True)
        self.properties_form.addRow("Background Image:", image_label)

        # === Grid Settings Section ===
        from PyQt6.QtWidgets import QCheckBox, QComboBox, QFrame

        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.properties_form.addRow(separator)

        # Grid header
        grid_label = QLabel("Grid Settings")
        grid_label.setProperty("type", "header")
        self.properties_form.addRow(grid_label)

        # Grid visibility toggle
        grid_visible_checkbox = QCheckBox("Show Grid (G)")
        grid_visible_checkbox.setChecked(self.state.camera.grid_visible)
        grid_visible_checkbox.stateChanged.connect(
            lambda state: self.toggle_grid_visibility(state == Qt.CheckState.Checked.value)
        )
        self.properties_form.addRow("", grid_visible_checkbox)

        # Grid size selector
        grid_size_combo = QComboBox()
        grid_sizes = [8, 16, 24, 32, 48, 64, 128]
        for size in grid_sizes:
            grid_size_combo.addItem(f"{size}px", size)

        # Set current grid size
        current_grid_size = self.state.camera.grid_size
        index = grid_size_combo.findData(current_grid_size)
        if index >= 0:
            grid_size_combo.setCurrentIndex(index)

        grid_size_combo.currentIndexChanged.connect(self.on_grid_size_changed)
        self.properties_form.addRow("Grid Size:", grid_size_combo)

        # Snap to grid toggle
        snap_checkbox = QCheckBox("Snap to Grid")
        snap_checkbox.setChecked(self.state.camera.snap_to_grid)
        snap_checkbox.stateChanged.connect(
            lambda state: setattr(self.state.camera, 'snap_to_grid', state == Qt.CheckState.Checked.value)
        )
        self.properties_form.addRow("", snap_checkbox)

    def on_grid_size_changed(self, index):
        """Handle grid size change."""
        from PyQt6.QtWidgets import QComboBox
        combo = self.sender()
        if isinstance(combo, QComboBox):
            new_size = combo.itemData(index)
            self.state.camera.grid_size = new_size
            self.update_viewport()
            print(f"[Editor] Grid size changed to {new_size}px")

    def _on_grid_size_changed_from_panel(self, new_size):
        """Handle grid size change from viewport panel."""
        self.state.camera.grid_size = new_size
        self.update_viewport()
        print(f"[Editor] Grid size changed to {new_size}px")

    def _on_snap_to_grid_changed_from_panel(self, snap_enabled):
        """Handle snap to grid change from viewport panel."""
        self.state.camera.snap_to_grid = snap_enabled
        print(f"[Editor] Snap to grid: {snap_enabled}")

    def toggle_grid_visibility(self, visible=None):
        """Toggle grid visibility."""
        if visible is None:
            # Toggle current state
            self.state.camera.grid_visible = not self.state.camera.grid_visible
        else:
            # Set to specific value
            self.state.camera.grid_visible = visible

        self.update_viewport()
        print(f"[Editor] Grid {'visible' if self.state.camera.grid_visible else 'hidden'}")

    def undo(self):
        """Undo the last operation."""
        if self.command_history.undo():
            desc = self.command_history.get_redo_description()  # This is what was just undone
            print(f"[Undo] Undid: {desc}")
            # Update UI
            if self.selected_sprite:
                self.update_properties_panel(self.selected_sprite)
            self.update_viewport()
        else:
            print("[Undo] Nothing to undo")

    def redo(self):
        """Redo the last undone operation."""
        if self.command_history.redo():
            desc = self.command_history.get_undo_description()  # This is what was just redone
            print(f"[Redo] Redid: {desc}")
            # Update UI
            if self.selected_sprite:
                self.update_properties_panel(self.selected_sprite)
            self.update_viewport()
        else:
            print("[Redo] Nothing to redo")

    def set_transform_tool(self, tool):
        """Set the current transform tool (move, rotate, scale)."""
        self.transform_tool = tool

        # Delegate button state updates to viewport panel
        self.viewport_panel.set_transform_tool(tool)

        print(f"[Editor] Transform tool: {tool}")
        self.update_viewport()

    def pick_background_color(self):
        """Open color picker for scene background."""
        if not self.game.scene_manager or not self.game.scene_manager.current_scene:
            return

        scene = self.game.scene_manager.scenes[self.game.scene_manager.current_scene]

        from PyQt6.QtWidgets import QColorDialog
        from PyQt6.QtGui import QColor

        current_color = scene.background_color
        initial_color = QColor(current_color[0], current_color[1], current_color[2])

        # Pause rendering while color dialog is open to prevent conflicts
        self.render_timer.stop()

        color = QColorDialog.getColor(initial_color, self, "Pick Background Color")

        # Resume rendering
        self.render_timer.start(16)

        if color.isValid():
            scene.background_color = (color.red(), color.green(), color.blue())
            self.update_properties_panel(None)  # Refresh properties panel
            self.update_viewport()  # Refresh viewport to show new color

    def update_viewport(self):
        """Update the Pygame viewport(s)."""
        # Render to main pygame widget (Visual and Split tabs)
        self.render_to_surface(self.pygame_widget)

        # If in split mode, also render to the split pygame widget
        if self.current_view_mode == "Split":
            self.render_to_surface(self.pygame_widget_split)

    def get_viewport_size_from_config(self):
        """Get game viewport size from project config."""
        import json
        config_path = os.path.join(self.project_path, '2d_project.json')
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                window_config = config.get('window', {})
                width = window_config.get('width', 800)
                height = window_config.get('height', 600)
                return (width, height)
        except Exception as e:
            print(f"[Editor] Warning: Could not load viewport size from config: {e}")
            return (800, 600)  # Default fallback

    def render_to_surface(self, widget):
        """Render scene to a specific pygame widget."""
        surface = widget.get_surface()
        if not surface:
            return

        # Render scene
        if self.game.scene_manager and self.game.scene_manager.current_scene:
            scene = self.game.scene_manager.scenes[self.game.scene_manager.current_scene]

            # Draw background (color or image)
            if hasattr(scene, 'background_surface') and scene.background_surface:
                # Scale background to fit surface
                scaled_bg = pygame.transform.scale(scene.background_surface, surface.get_size())
                surface.blit(scaled_bg, (0, 0))
            elif hasattr(scene, 'background_color') and scene.background_color:
                surface.fill(scene.background_color)
            else:
                # Default background
                surface.fill((60, 60, 65))

            # Draw grid (if visible)
            from v2_engine.editor import gizmos
            if self.state.camera.grid_visible:
                gizmos.draw_grid(surface, self.state.camera, surface.get_size())

            # Draw viewport bounds (game camera area)
            viewport_size = self.get_viewport_size_from_config()
            gizmos.draw_viewport_bounds(surface, self.state.camera, viewport_size)

            # Draw sprites
            if hasattr(scene, 'sprite_groups'):
                all_sprites = []
                for group_name, sprite_group in scene.sprite_groups.items():
                    all_sprites.extend(sprite_group.sprites)

                all_sprites.sort(key=lambda s: getattr(s, 'layer', 0))

                for sprite in all_sprites:
                    self.render_sprite(sprite, surface)

                # Draw gizmos
                for sprite in all_sprites:
                    is_selected = sprite in self.selected_sprites if self.selected_sprites else sprite == self.state.selected_sprite
                    gizmos.draw_sprite_gizmo(surface, sprite, self.state.camera, is_selected)

                    # Draw transform-specific gizmo for primary selected sprite only
                    if sprite == self.selected_sprite:
                        if self.transform_tool == 'rotate':
                            gizmos.draw_rotate_gizmo(surface, sprite, self.state.camera)
                        elif self.transform_tool == 'scale':
                            gizmos.draw_scale_gizmo(surface, sprite, self.state.camera)
                            # Draw scale feedback if currently scaling
                            if self.gizmo_dragging and self.gizmo_drag_type == 'scale' and self.scale_feedback_mouse_pos:
                                gizmos.draw_scale_feedback(surface, sprite, self.state.camera,
                                                          int(self.scale_feedback_mouse_pos.x),
                                                          int(self.scale_feedback_mouse_pos.y))

            # Draw box selection rectangle if dragging
            if self.box_select_dragging and self.box_select_start:
                # Get current mouse position from last drag event
                if hasattr(self, 'last_box_select_pos'):
                    gizmos.draw_selection_box(surface, self.box_select_start, self.last_box_select_pos)

        # Update the Qt widget with the rendered surface
        widget.update_from_surface()

    def render_sprite(self, sprite, surface):
        """Render a single sprite to the surface."""
        if not hasattr(sprite, 'image') or sprite.image is None:
            return

        # Check visibility - in editor mode, invisible objects render with ghosting
        is_visible = getattr(sprite, 'visible', True)
        editor_ghost_mode = not is_visible

        import math

        screen_pos = self.state.camera.world_to_screen(sprite.position)

        # Get transform properties
        sprite_scale = getattr(sprite, 'scale', Vector2(1, 1))
        sprite_rotation = getattr(sprite, 'rotation', 0)
        sprite_origin = getattr(sprite, 'origin', Vector2(0.5, 0.5))

        # Calculate combined scale including camera zoom
        final_scale_x = sprite_scale.x * self.state.camera.zoom
        final_scale_y = sprite_scale.y * self.state.camera.zoom
        avg_scale = (final_scale_x + final_scale_y) / 2.0

        # Get original image dimensions
        orig_width = sprite.image.get_width()
        orig_height = sprite.image.get_height()

        if sprite_rotation != 0:
            # First scale the image
            if sprite.image.get_flags() & pygame.SRCALPHA:
                scaled_image = pygame.transform.rotozoom(sprite.image, 0, avg_scale)
            else:
                temp_surface = pygame.Surface(sprite.image.get_size(), pygame.SRCALPHA)
                temp_surface.blit(sprite.image, (0, 0))
                scaled_image = pygame.transform.rotozoom(temp_surface, 0, avg_scale)

            # Calculate origin point in scaled image coordinates (pixels)
            scaled_width = scaled_image.get_width()
            scaled_height = scaled_image.get_height()
            origin_x_px = sprite_origin.x * scaled_width
            origin_y_px = sprite_origin.y * scaled_height

            # Rotate the scaled image
            # pygame rotates counterclockwise, but our rotation convention is clockwise, so negate
            rendered_image = pygame.transform.rotate(scaled_image, -sprite_rotation)

            # Calculate how the origin point moved due to rotation
            # Center of scaled image (rotation pivot point)
            center_x = scaled_width / 2
            center_y = scaled_height / 2

            # Vector from center to origin in scaled image
            dx = origin_x_px - center_x
            dy = origin_y_px - center_y

            # Rotate this vector to track where the origin point should be
            # Use positive sprite_rotation (our convention) for the orbit calculation
            angle_rad = math.radians(sprite_rotation)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            # 2D rotation matrix
            rotated_dx = dx * cos_a - dy * sin_a
            rotated_dy = dx * sin_a + dy * cos_a

            # Origin point in rotated image (relative to rotated image's center)
            rotated_rect = rendered_image.get_rect()
            rotated_center_x = rotated_rect.width / 2
            rotated_center_y = rotated_rect.height / 2

            rotated_origin_x = rotated_center_x + rotated_dx
            rotated_origin_y = rotated_center_y + rotated_dy

            # Position image so rotated origin point is at screen_pos
            topleft_x = screen_pos.x - rotated_origin_x
            topleft_y = screen_pos.y - rotated_origin_y

        else:
            # No rotation - simpler calculation
            if avg_scale != 1.0:
                if final_scale_x != 1.0 or final_scale_y != 1.0:
                    width = int(orig_width * final_scale_x)
                    height = int(orig_height * final_scale_y)
                    rendered_image = pygame.transform.scale(sprite.image, (width, height))
                else:
                    rendered_image = sprite.image
            else:
                rendered_image = sprite.image

            image_rect = rendered_image.get_rect()

            # Calculate position: screen_pos is where the origin point should be
            topleft_x = screen_pos.x - (sprite_origin.x * image_rect.width)
            topleft_y = screen_pos.y - (sprite_origin.y * image_rect.height)

        # Blit to surface (with transparency for ghosted invisible objects)
        if editor_ghost_mode:
            # Create a copy with alpha transparency for ghosting effect
            ghost_image = rendered_image.copy()
            ghost_image.set_alpha(100)  # 40% opacity for ghosted objects
            surface.blit(ghost_image, (int(topleft_x), int(topleft_y)))
        else:
            surface.blit(rendered_image, (int(topleft_x), int(topleft_y)))

    def reset_camera(self):
        """Reset camera to default position."""
        self.state.camera.reset()

    def save_scene(self):
        """Save the current scene to file."""
        # Delegate to scene manager UI if available
        if hasattr(self, 'scene_manager_ui'):
            self.scene_manager_ui.save_scene()
            return


    def open_project_settings(self):
        """Open the project settings dialog."""
        from v2_engine.editor.project_settings_dialog import ProjectSettingsDialog
        dialog = ProjectSettingsDialog(self.project_path, self)
        dialog.exec()

    def open_save_dialog(self):
        """Open the save game dialog."""
        from v2_engine.editor.save_load_dialog import SaveDialog
        from v2_engine.core.game_state import get_game_state

        game_state = get_game_state()
        current_scene = self.game.scene_manager.current_scene_name if self.game.scene_manager else "unknown"

        dialog = SaveDialog(game_state, self.project_path, current_scene, self)
        if dialog.exec():
            print(f"[Editor] Game saved successfully")

    def open_load_dialog(self):
        """Open the load game dialog."""
        from v2_engine.editor.save_load_dialog import LoadDialog
        from v2_engine.core.game_state import get_game_state

        game_state = get_game_state()

        dialog = LoadDialog(game_state, self.project_path, self)
        if dialog.exec():
            print(f"[Editor] Game loaded successfully")
            # Get the loaded scene name from pending entity states
            if hasattr(game_state, '_pending_entity_states'):
                # Reload current scene to apply loaded state
                if self.game.scene_manager:
                    self.game.scene_manager.reload_current_scene()
                    self.update_hierarchy()
                    self.update_properties_panel()
                    QMessageBox.information(
                        self,
                        "Load Complete",
                        "Game state loaded. Scene has been reloaded with saved state."
                    )

    def play_scene(self):
        """Play the scene in a separate window."""
        # Delegate to playback manager if available
        if hasattr(self, 'playback_manager'):
            # Auto-save before playing
            print("[Editor] Auto-saving scene before play...")
            self.save_scene()

            # Get current scene name
            current_scene = self.game.scene_manager.current_scene if self.game.scene_manager else None

            # Launch via playback manager
            self.playback_manager.play(self.project_path, current_scene)
            return


    def stop_play(self):
        """Stop the running game."""
        # Delegate to playback manager if available
        if hasattr(self, 'playback_manager'):
            self.playback_manager.stop()
            return

            print("[Editor] No game running")

    def check_play_process(self):
        """Check if the play process is still running and update UI accordingly."""
        # Delegate to playback manager if available
        if hasattr(self, 'playback_manager'):
            self.playback_manager.check_process()
            return

    def show_add_object_dialog(self):
        """Add a new object to the scene (simplified - just add directly)."""
        self.add_sprite_object()

    def add_sprite_object(self):
        """Add a new sprite object to the scene."""
        if not self.game.scene_manager or not self.game.scene_manager.current_scene:
            print("[Editor] No scene loaded")
            return

        scene = self.game.scene_manager.scenes[self.game.scene_manager.current_scene]

        # Create new sprite at center of viewport
        from v2_engine.sprites.sprite_object import SpriteObject

        # Calculate center of viewport in world coords
        viewport_size = self.pygame_widget.get_surface().get_size()
        screen_center = Vector2(viewport_size[0] / 2, viewport_size[1] / 2)
        world_center = self.state.camera.screen_to_world(screen_center)

        # Create sprite
        new_sprite = SpriteObject(world_center.x, world_center.y)
        new_sprite.image = pygame.Surface((64, 64))
        new_sprite.image.fill((200, 100, 150))  # Purple/pink color to distinguish from test sprite
        new_sprite.origin = Vector2(0.5, 0.5)
        new_sprite.layer = 0

        # Add to 'all' group
        if 'all' in scene.sprite_groups:
            scene.sprite_groups['all'].add(new_sprite)
            print(f"[Editor] Added new sprite at ({world_center.x:.1f}, {world_center.y:.1f})")

            # Update hierarchy
            self.update_hierarchy()

            # Select the new sprite
            self.selected_sprite = new_sprite
            self.state.selected_sprite = new_sprite
            self.update_properties_panel(new_sprite)
        else:
            print("[Editor] No 'all' sprite group found")

    def delete_selected_sprite(self, confirm=False):
        """Delete the currently selected sprite."""
        if not self.selected_sprite:
            print("[Editor] No sprite selected to delete")
            return

        # Confirm deletion if requested (from button click)
        if confirm:
            reply = QMessageBox.question(
                self,
                'Delete Sprite',
                'Are you sure you want to delete the selected sprite?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Remove from all sprite groups
        scene = self.game.scene_manager.scenes[self.game.scene_manager.current_scene]
        if hasattr(scene, 'sprite_groups'):
            for group in scene.sprite_groups.values():
                if self.selected_sprite in group.sprites:
                    group.remove(self.selected_sprite)
                    sprite_name = getattr(self.selected_sprite, 'name', self.selected_sprite.__class__.__name__)
                    print(f"[Editor] Deleted sprite: {sprite_name}")

        # Clear selection
        self.selected_sprite = None
        self.state.selected_sprite = None
        self.update_properties_panel(None)

        # Update hierarchy
        self.update_hierarchy()

    # Multi-select helper methods
    def _on_selection_changed(self, sprites, primary_sprite):
        """Handle selection change from SelectionManager."""
        # Update local references for backward compatibility
        self.selected_sprites = sprites
        self.selected_sprite = primary_sprite
        self.state.selected_sprite = primary_sprite

        # Update UI
        if len(sprites) > 1:
            # Multi-selection
            self.update_properties_panel_multi(sprites)
        else:
            # Single or no selection
            self.update_properties_panel(primary_sprite)

        # Update split view code tabs
        self.update_split_view_code_tabs()

        # Update viewport
        self.update_viewport()

    def _on_playback_started(self, pid):
        """Handle playback start from PlaybackManager."""
        # Update local state for backward compatibility
        self.play_process = self.playback_manager.play_process
        self.is_playing = True

        # Update toolbar buttons
        if hasattr(self, 'play_btn'):
            self.play_btn.setEnabled(False)
            self.play_btn.setText("▶ Playing...")
            self.play_btn.setStyleSheet(f"background-color: {self.theme.success}; color: {self.theme.text_primary};")
        if hasattr(self, 'stop_btn'):
            self.stop_btn.setEnabled(True)

        print(f"[Editor] Playback started (PID: {pid})")

    def _on_playback_stopped(self, exit_code):
        """Handle playback stop from PlaybackManager."""
        # Update local state for backward compatibility
        self.play_process = None
        self.is_playing = False

        # Update toolbar buttons
        if hasattr(self, 'play_btn'):
            self.play_btn.setEnabled(True)
            self.play_btn.setText("▶ Play (F5)")
            self.play_btn.setStyleSheet("")  # Reset to default theme styling
        if hasattr(self, 'stop_btn'):
            self.stop_btn.setEnabled(False)

        print(f"[Editor] Playback stopped (exit code: {exit_code})")

    def _on_scene_switched(self, scene_name):
        """Handle scene switch from SceneManagerUI."""
        # Update UI
        self.update_hierarchy()
        self.refresh_code_view()
        self.update_scene_menu()
        self.update_scene_list()

        # Clear selection
        if hasattr(self, 'selection_manager'):
            self.selection_manager.clear()
        else:
            self.selected_sprite = None
            self.state.selected_sprite = None
            self.update_properties_panel(None)

        print(f"[Editor] UI updated after scene switch to: {scene_name}")

    def _on_scene_created(self, scene_name):
        """Handle scene creation from SceneManagerUI."""
        # Update scene menu and list
        self.update_scene_menu()
        self.update_scene_list()

        # Switch to the new scene
        if hasattr(self, 'scene_manager_ui'):
            self.scene_manager_ui.switch_to_scene(scene_name)

        print(f"[Editor] UI updated after scene creation: {scene_name}")

    def _on_scene_saved(self, scene_name):
        """Handle scene save from SceneManagerUI."""
        # Refresh code view to show saved changes
        self.refresh_code_view()

        print(f"[Editor] UI updated after scene save: {scene_name}")

    def select_sprite(self, sprite, add_to_selection=False):
        """
        Select a sprite (or add to current selection).

        Args:
            sprite: Sprite to select
            add_to_selection: If True, add to selection; if False, clear and select only this sprite
        """
        # Delegate to selection manager if available
        if hasattr(self, 'selection_manager'):
            self.selection_manager.select(sprite, add_to_selection)
            return


    def deselect_all(self):
        """Deselect all sprites."""
        # Delegate to selection manager if available
        if hasattr(self, 'selection_manager'):
            self.selection_manager.clear()
            return


    def get_selected_sprites(self):
        """Get list of currently selected sprites."""
        # Delegate to selection manager if available
        if hasattr(self, 'selection_manager'):
            return self.selection_manager.get_selection()


    def copy_sprite(self):
        """Copy the currently selected sprite."""
        # Delegate to selection manager if available
        if hasattr(self, 'selection_manager'):
            self.selection_manager.copy()
            return


    def paste_sprite(self):
        """Paste the copied sprite."""
        # Delegate to selection manager if available
        if hasattr(self, 'selection_manager'):
            if not self.game.scene_manager or not self.game.scene_manager.current_scene:
                print("[Editor] No scene loaded")
                return

            scene = self.game.scene_manager.scenes[self.game.scene_manager.current_scene]
            new_sprite = self.selection_manager.paste(scene)

            if new_sprite:
                # Update hierarchy
                self.update_hierarchy()

                # Select the new sprite
                self.select_sprite(new_sprite)
            return


    def check_rotate_gizmo_hit(self, screen_x, screen_y, sprite):
        """Check if mouse is over rotate gizmo handle."""
        import math

        # Get sprite center in screen space
        world_center = sprite.position
        screen_center = self.state.camera.world_to_screen(world_center)

        # Calculate radius and handle position
        rect = sprite.get_rect()
        screen_rect = self.state.camera.world_to_screen_rect(rect)
        radius = int(max(screen_rect.width, screen_rect.height) * 0.6) + 20

        # Get current rotation
        current_rotation = getattr(sprite, 'rotation', 0)
        handle_angle = -90 + current_rotation  # Handle follows rotation
        handle_x = screen_center.x + int(radius * math.cos(math.radians(handle_angle)))
        handle_y = screen_center.y + int(radius * math.sin(math.radians(handle_angle)))

        # Check if click is within handle circle (8px radius + some tolerance)
        distance = math.sqrt((screen_x - handle_x)**2 + (screen_y - handle_y)**2)
        return distance <= 12  # 8px handle + 4px tolerance

    def check_scale_gizmo_hit(self, screen_x, screen_y, sprite):
        """
        Check if mouse is over scale gizmo handle.

        Returns:
            str or False: Handle type ('corner', 'horizontal', 'vertical', 'top', 'bottom', 'left', 'right') or False
        """
        rect = sprite.get_rect()
        screen_rect = self.state.camera.world_to_screen_rect(rect)

        # Corner handles (uniform scaling) - improved hit detection
        handle_size = 8
        tolerance = 8  # Increased from 4 to 8 for better UX
        corners = [
            (screen_rect.left, screen_rect.top, 'corner_tl'),
            (screen_rect.right, screen_rect.top, 'corner_tr'),
            (screen_rect.left, screen_rect.bottom, 'corner_bl'),
            (screen_rect.right, screen_rect.bottom, 'corner_br')
        ]

        for corner_x, corner_y, handle_type in corners:
            if abs(screen_x - corner_x) <= handle_size + tolerance and \
               abs(screen_y - corner_y) <= handle_size + tolerance:
                return handle_type

        # Edge handles (axis-specific scaling) - improved hit detection
        edge_handle_size = 6
        edge_tolerance = 8  # Increased from default for better UX
        edges = [
            (screen_rect.centerx, screen_rect.top, 'top'),
            (screen_rect.centerx, screen_rect.bottom, 'bottom'),
            (screen_rect.left, screen_rect.centery, 'left'),
            (screen_rect.right, screen_rect.centery, 'right')
        ]

        for edge_x, edge_y, handle_type in edges:
            import math
            distance = math.sqrt((screen_x - edge_x)**2 + (screen_y - edge_y)**2)
            if distance <= edge_handle_size + edge_tolerance:
                return handle_type

        return False

    def on_viewport_mouse_press(self, x, y):
        """Handle mouse press in viewport."""
        # Convert screen coords to world coords
        screen_pos = Vector2(x, y)
        world_pos = self.state.camera.screen_to_world(screen_pos)

        # If we have a selected sprite and using rotate/scale tool, check gizmo hit first
        if self.selected_sprite:
            if self.transform_tool == 'rotate' and self.check_rotate_gizmo_hit(x, y, self.selected_sprite):
                import math
                self.gizmo_dragging = True
                self.gizmo_drag_type = 'rotate'
                self.gizmo_drag_start = Vector2(x, y)
                self.initial_rotation = getattr(self.selected_sprite, 'rotation', 0)
                # Store for undo
                self.drag_start_rotation = self.initial_rotation
                print("[Editor] Started rotate gizmo drag")
                return

            elif self.transform_tool == 'scale':
                handle_type = self.check_scale_gizmo_hit(x, y, self.selected_sprite)
                if handle_type:
                    self.gizmo_dragging = True
                    self.gizmo_drag_type = 'scale'
                    self.scale_handle_type = handle_type
                    self.gizmo_drag_start = Vector2(x, y)
                    self.initial_scale = getattr(self.selected_sprite, 'scale', Vector2(1, 1))
                    # Store for undo
                    self.drag_start_scale = Vector2(self.initial_scale.x, self.initial_scale.y)
                    print(f"[Editor] Started scale gizmo drag ({handle_type})")
                    return

            elif self.transform_tool == 'move':
                # Store initial positions for all selected sprites (for multi-select move)
                if len(self.selected_sprites) > 1:
                    self.multi_drag_start_positions = [Vector2(s.position.x, s.position.y) for s in self.selected_sprites]
                    # Set drag_start_position to primary sprite's position
                    self.drag_start_position = Vector2(self.selected_sprite.position.x, self.selected_sprite.position.y)
                else:
                    # Single sprite - just store its position
                    self.drag_start_position = Vector2(self.selected_sprite.position.x, self.selected_sprite.position.y)

        # Try to select sprite at this position
        if self.game.scene_manager and self.game.scene_manager.current_scene:
            scene = self.game.scene_manager.scenes[self.game.scene_manager.current_scene]

            if hasattr(scene, 'sprite_groups'):
                all_sprites = []
                for group_name, sprite_group in scene.sprite_groups.items():
                    all_sprites.extend(sprite_group.sprites)

                # Find sprite at position (check in reverse layer order - top to bottom)
                all_sprites.sort(key=lambda s: getattr(s, 'layer', 0), reverse=True)

                # Check if Ctrl is held for multi-select
                from PyQt6.QtCore import Qt
                from PyQt6.QtWidgets import QApplication
                modifiers = QApplication.keyboardModifiers()
                ctrl_held = modifiers & Qt.KeyboardModifier.ControlModifier

                sprite_clicked = False
                for sprite in all_sprites:
                    if self.select_tool._point_in_sprite(world_pos, sprite):
                        sprite_clicked = True

                        # If sprite is already selected and Ctrl is NOT held, don't change selection
                        # (allows dragging multi-selected sprites)
                        if sprite in self.selected_sprites and not ctrl_held:
                            # Just make this the primary sprite if it isn't already
                            if sprite != self.selected_sprite:
                                self.selected_sprite = sprite
                                self.state.selected_sprite = sprite

                                # Update drag start position to use the new primary sprite
                                # This prevents the "jump" when dragging from a non-primary sprite
                                if self.transform_tool == 'move' and len(self.selected_sprites) > 1:
                                    # Recalculate drag positions with new primary
                                    self.multi_drag_start_positions = [Vector2(s.position.x, s.position.y) for s in self.selected_sprites]
                                    self.drag_start_position = Vector2(self.selected_sprite.position.x, self.selected_sprite.position.y)
                        else:
                            # Use new select_sprite method
                            self.select_sprite(sprite, add_to_selection=ctrl_held)

                        # Clear box selection state when clicking on a sprite
                        self.box_select_start = None
                        self.box_select_dragging = False
                        return

                # No sprite clicked - deselect or prepare for box selection
                if not sprite_clicked:
                    # Store click position for potential box selection (if user drags)
                    self.box_select_start = Vector2(x, y)
                    # Don't start box selection yet - wait for drag
                    # If Ctrl not held, deselect everything
                    if not ctrl_held:
                        self.deselect_all()

    def on_viewport_double_click(self, x, y):
        """Handle double-click in viewport - opens split view with selected sprite."""
        # Convert screen coords to world coords
        screen_pos = Vector2(x, y)
        world_pos = self.state.camera.screen_to_world(screen_pos)

        # Find sprite at position
        if self.game.scene_manager and self.game.scene_manager.current_scene:
            scene = self.game.scene_manager.scenes[self.game.scene_manager.current_scene]

            if hasattr(scene, 'sprite_groups'):
                all_sprites = []
                for group_name, sprite_group in scene.sprite_groups.items():
                    all_sprites.extend(sprite_group.sprites)

                # Find sprite at position (check in reverse layer order - top to bottom)
                all_sprites.sort(key=lambda s: getattr(s, 'layer', 0), reverse=True)

                for sprite in all_sprites:
                    if self.select_tool._point_in_sprite(world_pos, sprite):
                        # Select the sprite
                        self.select_sprite(sprite, add_to_selection=False)

                        # Switch to Split view
                        self.view_tab_bar.setCurrentIndex(2)  # 0=Visual, 1=Code, 2=Split

                        print(f"[Editor] Double-clicked sprite: {getattr(sprite, 'name', sprite.__class__.__name__)}")
                        return

    def on_viewport_mouse_drag(self, x, y):
        """Handle mouse drag in viewport."""
        # Check if we should start box selection (user is dragging from empty space)
        if self.box_select_start and not self.box_select_dragging and not self.selected_sprite:
            # Check if drag distance is significant (avoid accidental box select on tiny movements)
            import math
            drag_distance = math.sqrt((x - self.box_select_start.x)**2 + (y - self.box_select_start.y)**2)
            if drag_distance > 5:  # 5 pixel threshold
                self.box_select_dragging = True
                print("[Editor] Started box selection")

        # Handle box selection dragging
        if self.box_select_dragging:
            # Store current position for rendering box selection
            self.last_box_select_pos = Vector2(x, y)
            return

        if not self.selected_sprite:
            return

        # Handle gizmo dragging
        if self.gizmo_dragging:
            if self.gizmo_drag_type == 'rotate':
                import math
                # Calculate angle from sprite center to current mouse position
                world_center = self.selected_sprite.position
                screen_center = self.state.camera.world_to_screen(world_center)

                # Current angle from center to mouse
                dx = x - screen_center.x
                dy = y - screen_center.y
                current_angle = math.degrees(math.atan2(dy, dx))

                # Calculate angle at drag start
                start_dx = self.gizmo_drag_start.x - screen_center.x
                start_dy = self.gizmo_drag_start.y - screen_center.y
                start_angle = math.degrees(math.atan2(start_dy, start_dx))

                # Calculate rotation change from drag start
                angle_change = current_angle - start_angle

                # Apply rotation change to initial rotation
                if not hasattr(self.selected_sprite, 'rotation'):
                    self.selected_sprite.rotation = 0
                self.selected_sprite.rotation = self.initial_rotation + angle_change

            elif self.gizmo_drag_type == 'scale':
                # Calculate scale based on which handle and drag direction
                if self.gizmo_drag_start and self.scale_handle_type:
                    delta_x = x - self.gizmo_drag_start.x
                    delta_y = y - self.gizmo_drag_start.y

                    if not hasattr(self.selected_sprite, 'scale'):
                        self.selected_sprite.scale = Vector2(1, 1)

                    # Check if Shift is held for aspect ratio lock
                    from PyQt6.QtCore import Qt
                    from PyQt6.QtWidgets import QApplication
                    modifiers = QApplication.keyboardModifiers()
                    shift_held = modifiers & Qt.KeyboardModifier.ShiftModifier

                    # Get current scale as baseline
                    new_scale_x = self.initial_scale.x
                    new_scale_y = self.initial_scale.y

                    # Corner handles - always uniform scaling
                    if self.scale_handle_type.startswith('corner'):
                        import math

                        # Determine direction multipliers based on which corner
                        if self.scale_handle_type == 'corner_tl':
                            # Top-left: dragging left/up decreases, right/down increases
                            x_mult = -1
                            y_mult = -1
                        elif self.scale_handle_type == 'corner_tr':
                            # Top-right: dragging right/up increases/decreases
                            x_mult = 1
                            y_mult = -1
                        elif self.scale_handle_type == 'corner_bl':
                            # Bottom-left: dragging left/down decreases/increases
                            x_mult = -1
                            y_mult = 1
                        else:  # corner_br
                            # Bottom-right: dragging right/down increases
                            x_mult = 1
                            y_mult = 1

                        # Calculate average scale change (uniform)
                        scale_change_x = (delta_x * x_mult) / 100.0
                        scale_change_y = (delta_y * y_mult) / 100.0
                        scale_change = (scale_change_x + scale_change_y) / 2.0

                        new_scale_x = self.initial_scale.x + scale_change
                        new_scale_y = self.initial_scale.y + scale_change

                    # Horizontal edge handles - width only (or uniform if Shift held)
                    elif self.scale_handle_type in ['left', 'right']:
                        scale_change = delta_x / 100.0
                        if self.scale_handle_type == 'left':
                            scale_change = -scale_change  # Invert for left handle

                        if shift_held:
                            # Shift held - uniform scaling
                            new_scale_x = self.initial_scale.x + scale_change
                            new_scale_y = self.initial_scale.y + scale_change
                        else:
                            # Normal - width only
                            new_scale_x = self.initial_scale.x + scale_change
                            new_scale_y = self.initial_scale.y  # Keep Y unchanged

                    # Vertical edge handles - height only (or uniform if Shift held)
                    elif self.scale_handle_type in ['top', 'bottom']:
                        scale_change = delta_y / 100.0
                        if self.scale_handle_type == 'top':
                            scale_change = -scale_change  # Invert for top handle

                        if shift_held:
                            # Shift held - uniform scaling
                            new_scale_x = self.initial_scale.x + scale_change
                            new_scale_y = self.initial_scale.y + scale_change
                        else:
                            # Normal - height only
                            new_scale_x = self.initial_scale.x  # Keep X unchanged
                            new_scale_y = self.initial_scale.y + scale_change

                    # Clamp scale values
                    new_scale_x = max(0.1, min(5.0, new_scale_x))
                    new_scale_y = max(0.1, min(5.0, new_scale_y))

                    self.selected_sprite.scale = Vector2(new_scale_x, new_scale_y)

                    # Store mouse position for feedback display
                    self.scale_feedback_mouse_pos = Vector2(x, y)
            return

        # Normal move behavior (only when move tool is active)
        if self.transform_tool == 'move':
            # Convert screen coords to world coords
            screen_pos = Vector2(x, y)
            world_pos = self.state.camera.screen_to_world(screen_pos)

            # Calculate delta from primary sprite's initial position BEFORE snapping
            if self.drag_start_position:
                # Calculate raw delta (before any snapping)
                raw_delta_x = world_pos.x - self.drag_start_position.x
                raw_delta_y = world_pos.y - self.drag_start_position.y

                # If multi-select, move all sprites by the same delta
                if len(self.selected_sprites) > 1 and hasattr(self, 'multi_drag_start_positions'):
                    for i, sprite in enumerate(self.selected_sprites):
                        if i < len(self.multi_drag_start_positions):
                            # Move sprite by same delta, maintaining relative position
                            start_pos = self.multi_drag_start_positions[i]
                            new_x = start_pos.x + raw_delta_x
                            new_y = start_pos.y + raw_delta_y

                            # Apply grid snapping if enabled (to each sprite individually)
                            if self.state.camera.snap_to_grid:
                                new_x = self.state.camera.snap_to_grid_value(new_x)
                                new_y = self.state.camera.snap_to_grid_value(new_y)

                            sprite.position.x = new_x
                            sprite.position.y = new_y
                else:
                    # Single sprite - apply delta and snap
                    new_x = self.drag_start_position.x + raw_delta_x
                    new_y = self.drag_start_position.y + raw_delta_y

                    # Apply grid snapping if enabled
                    if self.state.camera.snap_to_grid:
                        new_x = self.state.camera.snap_to_grid_value(new_x)
                        new_y = self.state.camera.snap_to_grid_value(new_y)

                    self.selected_sprite.position.x = new_x
                    self.selected_sprite.position.y = new_y
            # Note: Properties panel will update on mouse release

    def on_viewport_mouse_release(self, x=None, y=None):
        """Handle mouse release - update properties after drag and create undo command."""
        # Handle box selection completion
        if self.box_select_dragging:
            if x is not None and y is not None and self.box_select_start:
                # Calculate box selection rectangle in screen space
                box_min_x = min(self.box_select_start.x, x)
                box_max_x = max(self.box_select_start.x, x)
                box_min_y = min(self.box_select_start.y, y)
                box_max_y = max(self.box_select_start.y, y)

                # Find sprites within box
                if self.game.scene_manager and self.game.scene_manager.current_scene:
                    scene = self.game.scene_manager.scenes[self.game.scene_manager.current_scene]

                    if hasattr(scene, 'sprite_groups'):
                        all_sprites = []
                        for group_name, sprite_group in scene.sprite_groups.items():
                            all_sprites.extend(sprite_group.sprites)

                        # Check which sprites are in selection box
                        from PyQt6.QtCore import Qt
                        from PyQt6.QtWidgets import QApplication
                        modifiers = QApplication.keyboardModifiers()
                        ctrl_held = modifiers & Qt.KeyboardModifier.ControlModifier

                        # If Ctrl not held, clear selection first
                        if not ctrl_held:
                            self.selected_sprites = []

                        for sprite in all_sprites:
                            # Get sprite bounds in screen space
                            rect = sprite.get_rect()
                            screen_rect = self.state.camera.world_to_screen_rect(rect)

                            # Check if sprite rect intersects with selection box
                            if (screen_rect.right >= box_min_x and screen_rect.left <= box_max_x and
                                screen_rect.bottom >= box_min_y and screen_rect.top <= box_max_y):
                                if sprite not in self.selected_sprites:
                                    self.selected_sprites.append(sprite)

                        # Update selection state
                        if self.selected_sprites:
                            self.selected_sprite = self.selected_sprites[-1]
                            self.state.selected_sprite = self.selected_sprite

                            # Update properties panel
                            if len(self.selected_sprites) > 1:
                                self.update_properties_panel_multi(self.selected_sprites)
                            else:
                                self.update_properties_panel(self.selected_sprites[0])

                            print(f"[Editor] Box selected {len(self.selected_sprites)} sprite(s)")
                        else:
                            self.selected_sprite = None
                            self.state.selected_sprite = None
                            self.update_properties_panel(None)

            self.box_select_dragging = False
            self.box_select_start = None
            return

        # Clear box selection state if it wasn't used (click without drag)
        if self.box_select_start and not self.box_select_dragging:
            self.box_select_start = None

        # Create undo command if we were dragging
        if self.selected_sprite:
            # Rotation command
            if self.gizmo_dragging and self.gizmo_drag_type == 'rotate' and self.drag_start_rotation is not None:
                new_rotation = getattr(self.selected_sprite, 'rotation', 0)
                if abs(new_rotation - self.drag_start_rotation) > 0.01:  # Only if actually changed
                    command = RotateCommand(self.selected_sprite, self.drag_start_rotation, new_rotation)
                    self.command_history.execute(command)
                    print(f"[Undo] Rotation command added: {self.drag_start_rotation:.1f}° → {new_rotation:.1f}°")
                self.drag_start_rotation = None

            # Scale command
            elif self.gizmo_dragging and self.gizmo_drag_type == 'scale' and self.drag_start_scale is not None:
                new_scale = getattr(self.selected_sprite, 'scale', Vector2(1, 1))
                if abs(new_scale.x - self.drag_start_scale.x) > 0.01 or abs(new_scale.y - self.drag_start_scale.y) > 0.01:
                    command = ScaleCommand(self.selected_sprite, self.drag_start_scale, new_scale)
                    self.command_history.execute(command)
                    print(f"[Undo] Scale command added: ({self.drag_start_scale.x:.2f}, {self.drag_start_scale.y:.2f}) → ({new_scale.x:.2f}, {new_scale.y:.2f})")
                self.drag_start_scale = None

            # Move command (supports multi-select)
            elif self.transform_tool == 'move' and self.drag_start_position is not None:
                new_position = Vector2(self.selected_sprite.position.x, self.selected_sprite.position.y)
                if abs(new_position.x - self.drag_start_position.x) > 0.01 or abs(new_position.y - self.drag_start_position.y) > 0.01:
                    # If multiple sprites selected, create batch command
                    if len(self.selected_sprites) > 1:
                        from v2_engine.editor.command import BatchCommand
                        commands = []
                        for i, sprite in enumerate(self.selected_sprites):
                            if hasattr(self, 'multi_drag_start_positions') and i < len(self.multi_drag_start_positions):
                                old_pos = self.multi_drag_start_positions[i]
                                new_pos = Vector2(sprite.position.x, sprite.position.y)
                                if abs(new_pos.x - old_pos.x) > 0.01 or abs(new_pos.y - old_pos.y) > 0.01:
                                    commands.append(MoveCommand(sprite, old_pos, new_pos))
                        if commands:
                            batch_command = BatchCommand(commands, "Move")
                            self.command_history.execute(batch_command)
                            print(f"[Undo] Batch move command added for {len(commands)} sprites")
                        self.multi_drag_start_positions = None
                    else:
                        command = MoveCommand(self.selected_sprite, self.drag_start_position, new_position)
                        self.command_history.execute(command)
                        print(f"[Undo] Move command added: ({self.drag_start_position.x:.0f}, {self.drag_start_position.y:.0f}) → ({new_position.x:.0f}, {new_position.y:.0f})")
                self.drag_start_position = None

        # Clear gizmo dragging state
        if self.gizmo_dragging:
            self.gizmo_dragging = False
            self.gizmo_drag_type = None
            self.scale_handle_type = None
            self.gizmo_drag_start = None
            self.scale_feedback_mouse_pos = None  # Clear scale feedback
            print("[Editor] Ended gizmo drag")

        if self.selected_sprite:
            self.update_properties_panel(self.selected_sprite)

    def on_viewport_camera_pan(self, delta_x, delta_y):
        """Handle camera panning."""
        # Pan camera (move in opposite direction of mouse drag)
        self.state.camera.position.x -= delta_x / self.state.camera.zoom
        self.state.camera.position.y -= delta_y / self.state.camera.zoom

    def on_viewport_wheel(self, delta, x, y):
        """Handle mouse wheel for zoom."""
        # Zoom in/out
        zoom_factor = 1.1 if delta > 0 else 0.9
        old_zoom = self.state.camera.zoom
        self.state.camera.zoom = max(0.1, min(5.0, self.state.camera.zoom * zoom_factor))

        # Zoom towards mouse position
        screen_pos = Vector2(x, y)
        world_pos_before = self.state.camera.screen_to_world(screen_pos)
        world_pos_after = self.state.camera.screen_to_world(screen_pos)

        # Adjust camera to keep mouse position stable
        diff = world_pos_before - world_pos_after
        self.state.camera.position += diff

        # Update status bar
        self.update_status_bar()

    def on_property_changed(self, sprite, property_name, value_str):
        """Handle property value changes from the properties panel."""
        try:
            # Parse value based on property type
            if property_name == 'name':
                # Update sprite name
                sprite.name = value_str
                print(f"[Editor] Renamed sprite to '{value_str}'")
                # Update hierarchy to reflect new name
                self.update_hierarchy()
                # Re-select the sprite to keep properties panel open
                self.selected_sprite = sprite
                self.state.selected_sprite = sprite
                # Refresh properties panel to update heading and clear focus
                self.update_properties_panel(sprite)
                return
            elif property_name == 'layer':
                value = int(value_str)
                sprite.layer = value
            elif property_name == 'rotation':
                value = float(value_str)
                sprite.rotation = value
                print(f"[Editor] Set rotation to {value}°")
            elif property_name in ['width', 'height']:
                # Update scale based on width/height change
                value = int(value_str)
                if value <= 0:
                    print(f"[Editor] Invalid {property_name}: must be > 0")
                    return

                if hasattr(sprite, 'image') and sprite.image:
                    base_width = sprite.image.get_width()
                    base_height = sprite.image.get_height()

                    if not hasattr(sprite, 'scale'):
                        sprite.scale = Vector2(1, 1)

                    if property_name == 'width':
                        # Calculate new X scale to achieve desired width
                        new_scale_x = value / base_width
                        sprite.scale = Vector2(new_scale_x, sprite.scale.y)
                        print(f"[Editor] Set width to {value} (scale.x = {new_scale_x:.2f})")
                    else:  # height
                        # Calculate new Y scale to achieve desired height
                        new_scale_y = value / base_height
                        sprite.scale = Vector2(sprite.scale.x, new_scale_y)
                        print(f"[Editor] Set height to {value} (scale.y = {new_scale_y:.2f})")

            elif '.' in property_name:
                # Nested property (e.g., position.x, origin.y)
                obj_name, attr_name = property_name.split('.')
                obj = getattr(sprite, obj_name)
                old_value = getattr(obj, attr_name)
                value = float(value_str)

                # Special handling for origin changes to create undo command
                if obj_name == 'origin':
                    old_origin = Vector2(sprite.origin.x, sprite.origin.y)
                    setattr(obj, attr_name, value)  # Apply the change
                    new_origin = Vector2(sprite.origin.x, sprite.origin.y)

                    # Create command
                    command = SetOriginCommand(sprite, old_origin, new_origin)
                    self.command_history.execute(command)
                else:
                    setattr(obj, attr_name, value)
            else:
                # Direct property
                value = float(value_str)
                setattr(sprite, property_name, value)

            print(f"[Editor] Updated {property_name} to {value_str}")

            # Refresh properties panel to show updated value
            self.update_properties_panel(sprite)

        except ValueError as e:
            print(f"[Editor] Invalid value for {property_name}: {value_str} - {e}")

    def set_origin_preset(self, sprite, origin_x: float, origin_y: float):
        """
        Set sprite origin to a preset value.

        Args:
            sprite: Sprite to modify
            origin_x: Origin X coordinate (0.0-1.0)
            origin_y: Origin Y coordinate (0.0-1.0)
        """
        old_origin = Vector2(sprite.origin.x, sprite.origin.y)
        new_origin = Vector2(origin_x, origin_y)

        # Create and execute command
        command = SetOriginCommand(sprite, old_origin, new_origin)
        self.command_history.execute(command)

        self.update_properties_panel(sprite)
        print(f"[Editor] Set origin to ({origin_x}, {origin_y})")

    def move_sprite_layer(self, sprite, direction: int):
        """
        Move sprite forward or backward in layer order.

        Args:
            sprite: Sprite to move
            direction: +1 to move forward (increase layer), -1 to move backward (decrease layer)
        """
        current_layer = getattr(sprite, 'layer', 0)
        new_layer = current_layer + direction

        sprite.layer = new_layer
        print(f"[Editor] Moved sprite to layer {new_layer}")

        # Refresh properties panel to show updated layer value
        self.update_properties_panel(sprite)

    def on_persistent_changed(self, sprite, is_persistent: bool):
        """Handle persistent checkbox state change."""
        from v2_engine.core.game_state import get_game_state
        import uuid

        sprite.is_persistent = is_persistent

        if is_persistent:
            # Auto-generate entity ID if not set
            if not sprite.entity_id:
                sprite_name = getattr(sprite, 'name', 'sprite')
                # Create a short, readable ID based on sprite name
                sprite.entity_id = f"{sprite_name}_{uuid.uuid4().hex[:8]}"

            # Register with GameState and set home scene
            game_state = get_game_state()
            current_scene_name = self.game.scene_manager.current_scene if self.game.scene_manager else None
            game_state.register_persistent(sprite, sprite.entity_id, home_scene=current_scene_name)
            print(f"[Editor] Registered persistent entity: {sprite.entity_id} (home: {current_scene_name})")
        else:
            # Unregister from GameState
            game_state = get_game_state()
            if sprite.entity_id and sprite.entity_id in game_state.persistent_entities:
                del game_state.persistent_entities[sprite.entity_id]
                print(f"[Editor] Unregistered persistent entity: {sprite.entity_id}")
            sprite.entity_id = None

        # Refresh properties panel to show/hide entity ID field
        self.update_properties_panel(sprite)

        # Update GameState panel to reflect changes
        self.update_gamestate_panel()

    def on_entity_id_changed(self, sprite, new_id: str):
        """Handle entity ID change."""
        from v2_engine.core.game_state import get_game_state
        import uuid

        old_id = sprite.entity_id
        game_state = get_game_state()

        # If empty, auto-generate
        if not new_id.strip():
            sprite_name = getattr(sprite, 'name', 'sprite')
            new_id = f"{sprite_name}_{uuid.uuid4().hex[:8]}"

        # Update entity ID
        sprite.entity_id = new_id

        # Re-register with GameState using new ID
        if old_id and old_id in game_state.persistent_entities:
            del game_state.persistent_entities[old_id]

        if sprite.is_persistent:
            game_state.register_persistent(sprite, new_id)
            print(f"[Editor] Updated entity ID: {old_id} -> {new_id}")

        # Refresh properties panel to show updated ID
        self.update_properties_panel(sprite)

        # Update GameState panel to reflect changes
        self.update_gamestate_panel()

    def on_visible_changed(self, sprite, is_visible: bool):
        """Handle visible checkbox state change."""
        sprite.visible = is_visible

        # Update hierarchy to reflect visibility change
        self.update_hierarchy()

        # Force viewport redraw to show ghosting
        if hasattr(self, 'game') and self.game:
            self.game.needs_render = True

    def on_code_saved(self, file_path: str):
        """Handle code file saved event."""
        print(f"[Editor] Code saved: {file_path}")

    def on_code_saved_and_reload(self, file_path: str):
        """Handle code file saved and reload request - hot-reload the behavior."""
        print(f"[Editor] Code saved and reloading: {file_path}")

        try:
            # Check if this is a behavior file
            if 'behaviors' not in file_path:
                QMessageBox.warning(
                    self,
                    "Not a Behavior",
                    "Hot-reload only works for custom behaviors in the behaviors/ directory."
                )
                return

            # Extract module and class names from file path
            import os
            filename = os.path.basename(file_path)
            module_name = filename[:-3]  # Remove .py extension

            # Reload the module
            import sys
            import importlib
            from v2_engine.components.component import Component
            import inspect

            module_key = f'behaviors.{module_name}'

            if module_key not in sys.modules:
                QMessageBox.warning(
                    self,
                    "Module Not Loaded",
                    f"Behavior module '{module_name}' is not currently loaded.\n\n"
                    f"The behavior must be used at least once before hot-reloading."
                )
                return

            # Reload the module
            print(f"[HotReload] Reloading module: {module_key}")
            module = importlib.reload(sys.modules[module_key])

            # Find all Component subclasses in the reloaded module
            reloaded_classes = []
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Component) and obj is not Component:
                    if obj.__module__ == module_key:
                        reloaded_classes.append((name, obj))

            if not reloaded_classes:
                QMessageBox.warning(
                    self,
                    "No Components Found",
                    f"No Component classes found in {filename}"
                )
                return

            # Reload behaviors in the component registry
            from v2_engine.components.component_registry import get_component_registry
            registry = get_component_registry()
            registry.refresh_custom_behaviors(self.project_path)

            # Find all sprites using these old component classes and re-instantiate
            reload_count = 0
            if self.game and self.game.scene_manager and self.game.scene_manager.current_scene_obj:
                current_scene = self.game.scene_manager.current_scene_obj

                for class_name, new_class in reloaded_classes:
                    # Find sprites with this component
                    for sprite in current_scene.sprites:
                        for comp_type, component in list(sprite.components.items()):
                            # Check if this is the old version of the reloaded class
                            if component.__class__.__name__ == class_name:
                                print(f"[HotReload] Re-instantiating {class_name} on {sprite.name}")

                                # Remove old component
                                sprite.remove_component(component.__class__)

                                # Create new instance with new class
                                new_component = new_class(sprite)
                                sprite.add_component(new_component)

                                reload_count += 1

            # Update properties panel if current sprite was affected
            if self.selected_sprite:
                self.update_properties_panel(self.selected_sprite)

            # Update viewport
            self.update_viewport()

            # Success message
            class_names = [name for name, _ in reloaded_classes]
            QMessageBox.information(
                self,
                "Hot-Reload Complete",
                f"Successfully reloaded:\n{', '.join(class_names)}\n\n"
                f"Re-instantiated {reload_count} component(s)"
            )

            print(f"[HotReload] Complete - reloaded {len(reloaded_classes)} class(es), "
                  f"re-instantiated {reload_count} component(s)")

        except SyntaxError as e:
            QMessageBox.critical(
                self,
                "Syntax Error",
                f"Cannot reload behavior due to syntax error:\n\n"
                f"Line {e.lineno}: {e.msg}\n"
                f"{e.text}"
            )
            print(f"[HotReload] Syntax error: {e}")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Reload Error",
                f"Failed to reload behavior:\n{e}"
            )
            print(f"[HotReload] Error: {e}")
            import traceback
            traceback.print_exc()

    def on_new_behavior_created(self, file_path: str):
        """Handle new behavior created event - open it in code editor."""
        print(f"[Editor] Opening new behavior in code editor: {file_path}")

        # Refresh file navigators to show new file
        if hasattr(self, 'file_navigator'):
            self.file_navigator.refresh()
        if hasattr(self, 'file_navigator_split'):
            self.file_navigator_split.refresh()

        # Switch to Code view tab
        self.view_tab_bar.setCurrentIndex(1)  # 0=Visual, 1=Code, 2=Split

        # Load the file in the code editor
        self.code_editor.load_file(file_path)

        # Update file navigator highlighting
        if hasattr(self, 'file_navigator'):
            self.file_navigator.set_current_file(file_path)
        if hasattr(self, 'file_navigator_split'):
            self.file_navigator_split.set_current_file(file_path)

    def on_navigator_file_selected(self, file_path: str):
        """Handle file selection from file navigator."""
        import os

        if not os.path.exists(file_path):
            QMessageBox.warning(
                self,
                "File Not Found",
                f"Cannot find file:\n{file_path}"
            )
            return

        print(f"[Editor] Opening file from navigator: {file_path}")

        # Load the file in the appropriate code editor based on current view
        current_view = self.view_tab_bar.currentIndex()

        if current_view == 1:  # Code view
            self.code_editor.load_file(file_path)
        elif current_view == 2:  # Split view
            self.code_editor_split.load_file(file_path)
        else:  # Visual view - switch to Code view
            self.view_tab_bar.setCurrentIndex(1)
            self.code_editor.load_file(file_path)

        # Update file navigator highlighting
        if hasattr(self, 'file_navigator'):
            self.file_navigator.set_current_file(file_path)
        if hasattr(self, 'file_navigator_split'):
            self.file_navigator_split.set_current_file(file_path)

    def update_split_view_code_tabs(self):
        """Update split view code tabs when sprite selection changes."""
        # Delegate to split code panel if available
        if hasattr(self, 'split_code_panel'):
            current_scene_file = self.get_current_scene_file_path()
            self.split_code_panel.update_tabs(self.selected_sprite, current_scene_file)

    def get_current_scene_file_path(self) -> str:
        """Get the file path of the currently loaded scene."""
        if not hasattr(self, 'current_scene_file'):
            return ""
        return self.current_scene_file if self.current_scene_file else ""

    def on_split_switch_to_instance(self):
        """Handle switch to instance editing in split view."""
        # Delegate to split code panel
        self.split_code_panel.switch_to_instance_tab()

    def on_split_tab_changed(self, index: int):
        """Handle split view tab change."""
        # Could add additional logic here if needed in the future
        pass

    def on_edit_behavior_code(self, component):
        """Handle edit code button click for a behavior."""
        import inspect
        import os

        try:
            # Get the source file for the component
            source_file = inspect.getfile(component.__class__)

            if not os.path.exists(source_file):
                QMessageBox.warning(
                    self,
                    "File Not Found",
                    f"Cannot find source file:\n{source_file}"
                )
                return

            print(f"[Editor] Opening behavior code: {source_file}")

            # Switch to Code view tab
            self.view_tab_bar.setCurrentIndex(1)  # 0=Visual, 1=Code, 2=Split

            # Load the file in the code editor
            self.code_editor.load_file(source_file)

            # Update file navigator highlighting
            if hasattr(self, 'file_navigator'):
                self.file_navigator.set_current_file(source_file)
            if hasattr(self, 'file_navigator_split'):
                self.file_navigator_split.set_current_file(source_file)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open behavior code:\n{e}"
            )
            print(f"[Editor] Error opening behavior code: {e}")
            import traceback
            traceback.print_exc()

    def open_color_picker(self, sprite):
        """Open color picker dialog and update sprite color."""
        # Get current color from the image surface
        current_color = (255, 255, 255)
        if hasattr(sprite, 'image') and sprite.image:
            width = sprite.image.get_width()
            height = sprite.image.get_height()
            try:
                center_color = sprite.image.get_at((width // 2, height // 2))
                current_color = (center_color.r, center_color.g, center_color.b)
            except:
                current_color = (255, 255, 255)

        initial_color = QColor(*current_color)

        # Open color dialog with non-modal behavior to prevent freezing
        color = QColorDialog.getColor(
            initial_color,
            self,
            "Choose Object Color",
            QColorDialog.ColorDialogOption.DontUseNativeDialog  # Use Qt dialog instead of native
        )

        if color.isValid():
            new_color = (color.red(), color.green(), color.blue())

            # Update sprite color attribute
            sprite.color = new_color

            # Update the image surface with the new color
            if hasattr(sprite, 'image') and sprite.image:
                # Refill the surface with the new color
                sprite.image.fill(new_color)

            # Refresh properties panel to update color preview and RGB label
            self.update_properties_panel(sprite)

            # Force viewport redraw
            if hasattr(self, 'game') and self.game:
                self.game.needs_render = True

    def update_scene_list(self):
        """Update the Scene list in the left panel."""
        # Delegate to new hierarchy panel
        if hasattr(self, 'hierarchy_panel'):
            scenes_config = self._get_scenes_config()
            current_scene = self.game.scene_manager.current_scene if self.game.scene_manager else None
            self.hierarchy_panel.update_scenes(scenes_config, current_scene)

    def on_scene_list_clicked(self, item, column):
        """Handle scene list item click."""
        scene_name = item.data(0, Qt.ItemDataRole.UserRole)
        if scene_name:
            self.switch_to_scene(scene_name)

    def update_scene_menu(self):
        """Update the Scene menu with the list of available scenes."""
        import json

        # Remove old scene actions (everything after the separator)
        actions = self.scene_menu.actions()
        separator_index = -1
        for i, action in enumerate(actions):
            if action.isSeparator():
                separator_index = i
                break

        # Remove all actions after separator
        if separator_index >= 0:
            for action in actions[separator_index + 1:]:
                self.scene_menu.removeAction(action)

        # Read project config to get scene list
        config_path = os.path.join(self.project_path, '2d_project.json')
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

            scenes = config.get('scenes', {}).get('scenes', [])
            current_scene = self.game.scene_manager.current_scene if self.game.scene_manager else None

            for scene_info in scenes:
                scene_name = scene_info['name']
                action = QAction(f"{'✓ ' if scene_name == current_scene else '   '}{scene_name}", self)
                action.triggered.connect(lambda checked, name=scene_name: self.switch_to_scene(name))
                self.scene_menu.addAction(action)

        except Exception as e:
            print(f"[Editor] Error updating scene menu: {e}")

    def register_persistent_entities_from_current_scene(self):
        """Register any persistent entities found in the current scene."""
        from v2_engine.core.game_state import get_game_state

        if not self.game.scene_manager or not self.game.scene_manager.current_scene:
            return

        game_state = get_game_state()
        scene = self.game.scene_manager.scenes[self.game.scene_manager.current_scene]

        scene_name = self.game.scene_manager.current_scene

        for group in scene.sprite_groups.values():
            for sprite in list(group.sprites):
                if getattr(sprite, 'is_persistent', False) and getattr(sprite, 'entity_id', None):
                    # Only register if not already in GameState
                    if sprite.entity_id not in game_state.persistent_entities:
                        game_state.register_persistent(sprite, sprite.entity_id, home_scene=scene_name)
                        print(f"[Editor] Registered persistent entity on load: {sprite.entity_id} (home: {scene_name})")

    def reload_scene_from_file(self, scene_name: str):
        """Reload a scene module from disk (editor mode only)."""
        import importlib
        import sys

        # Find the scene file path
        import json
        config_path = os.path.join(self.project_path, '2d_project.json')

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

            # Find the scene file
            scene_file = None
            for scene_info in config.get('scenes', {}).get('scenes', []):
                if scene_info['name'] == scene_name:
                    scene_file = scene_info['file']
                    break

            if not scene_file:
                print(f"[Editor] Scene file not found for: {scene_name}")
                return

            # Convert file path to module name (e.g., "scenes/main_scene.py" -> "scenes.main_scene")
            module_name = scene_file.replace('/', '.').replace('\\', '.').replace('.py', '')

            # Reload the module if it's already loaded
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
                print(f"[Editor] Reloaded scene module: {module_name}")

            # Re-import and recreate the scene instance
            scene_module = importlib.import_module(module_name)
            scene_class = getattr(scene_module, scene_info['class'])

            # Replace the scene instance in the scene manager
            self.game.scene_manager.scenes[scene_name] = scene_class(self.game)
            print(f"[Editor] Recreated scene instance: {scene_name}")

        except Exception as e:
            print(f"[Editor] Error reloading scene {scene_name}: {e}")
            import traceback
            traceback.print_exc()

    def switch_to_scene(self, scene_name: str):
        """Switch to a different scene."""
        # Delegate to scene manager UI if available
        if hasattr(self, 'scene_manager_ui'):
            self.scene_manager_ui.switch_to_scene(scene_name)
            return


    def create_new_scene(self):
        """Create a new scene with dialog."""
        # Delegate to scene manager UI if available
        if hasattr(self, 'scene_manager_ui'):
            self.scene_manager_ui.create_new_scene(self)
            return


    def update_asset_browser(self):
        """Populate the asset browser with files from the assets directory."""
        # Delegate to new hierarchy panel
        if hasattr(self, 'hierarchy_panel'):
            self.hierarchy_panel.update_assets(self.project_path)

    def on_asset_clicked(self, item, column):
        """Handle asset item click - show preview."""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)

        if file_path is None:
            # Clicked a folder
            self.asset_preview.setText("No preview")
            self.asset_preview.setPixmap(QPixmap())
            self.selected_asset_path = None
            self.assign_asset_btn.setEnabled(False)
            return

        # Store selected asset
        self.selected_asset_path = file_path

        # Load and display preview
        try:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Scale to fit preview area while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    self.asset_preview.width() - 10,
                    self.asset_preview.height() - 10,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.asset_preview.setPixmap(scaled_pixmap)

                # Enable assign button if sprite is selected
                self.assign_asset_btn.setEnabled(self.selected_sprite is not None)
            else:
                self.asset_preview.setText("Failed to load image")
                self.assign_asset_btn.setEnabled(False)
        except Exception as e:
            print(f"[Editor] Error loading asset preview: {e}")
            self.asset_preview.setText("Error loading preview")
            self.assign_asset_btn.setEnabled(False)

    def assign_asset_to_sprite(self):
        """Assign the selected asset to the selected sprite."""
        if not self.selected_sprite or not self.selected_asset_path:
            print("[Editor] No sprite or asset selected")
            return

        try:
            # Load the image with pygame
            image = pygame.image.load(self.selected_asset_path)

            # Assign to sprite
            self.selected_sprite.image = image

            # Store relative path from project root for serialization
            rel_path = os.path.relpath(self.selected_asset_path, self.project_path)
            self.selected_sprite.image_path = rel_path

            sprite_name = getattr(self.selected_sprite, 'name', 'Sprite')
            asset_name = os.path.basename(self.selected_asset_path)
            print(f"[Editor] Assigned '{asset_name}' to sprite '{sprite_name}'")

            # Update properties panel to reflect new size
            self.update_properties_panel(self.selected_sprite)

        except Exception as e:
            print(f"[Editor] Error assigning asset: {e}")
            QMessageBox.warning(
                self,
                'Error',
                f'Failed to assign asset: {str(e)}'
            )


def main(project_path):
    """Launch the PyQt6 editor."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for consistent look

    window = EditorWindow(project_path)
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Usage: python qt_editor.py <project_path>")
