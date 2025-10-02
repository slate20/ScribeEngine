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
    QInputDialog, QMessageBox, QTextEdit, QTabWidget, QStackedWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QImage, QPixmap, QPainter

from v2_engine.core.game import Game
from v2_engine.utils.math import Vector2
from v2_engine.editor.editor_state import EditorState
from v2_engine.editor.tools.select_tool import SelectTool
from v2_engine.editor.scene_serializer import SceneSerializer


class PygameWidget(QLabel):
    """Widget that displays a Pygame surface as a QImage."""

    def __init__(self, parent=None, editor_window=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: #3c3c41; border: 1px solid #555;")
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

    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        current_pos = Vector2(event.pos().x(), event.pos().y())

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
            # Notify editor window that drag ended
            if self.editor_window and hasattr(self.editor_window, 'on_viewport_mouse_release'):
                self.editor_window.on_viewport_mouse_release()
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

        # Initialize game
        self.game = Game(project_path, editor_mode=True)
        if not self.game.initialize():
            raise RuntimeError("Failed to initialize game")

        # Editor state
        self.state = EditorState()
        self.select_tool = SelectTool()
        self.scene_serializer = SceneSerializer()
        self.play_process = None  # Track running game process

        # Setup UI (creates Pygame widget and screen)
        self.setup_ui()

        # Set game's screen to the pygame widget's surface
        self.game.screen = self.pygame_widget.get_surface()

        # Perform initial scene transition (after screen exists)
        if self.game.scene_manager:
            self.game.scene_manager._perform_scene_transition()

        # Update UI with loaded scene
        self.update_hierarchy()
        self.refresh_code_view()

        # Setup timer for rendering
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self.update_viewport)
        self.render_timer.start(16)  # ~60 FPS

        self.selected_sprite = None
        self.copied_sprite = None  # For copy/paste

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
        self.create_hierarchy_panel()
        self.create_properties_panel()

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

        # Visual tab - Pygame viewport
        self.pygame_widget = PygameWidget(editor_window=self)
        tab_bar.addTab(self.pygame_widget, "Visual")

        # Code tab - Code editor
        self.code_editor = QTextEdit()
        self.code_editor.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
            }
        """)

        # Add save button below code editor
        code_container = QWidget()
        code_layout = QVBoxLayout(code_container)
        code_layout.addWidget(self.code_editor)
        save_code_button = QPushButton("Save Code & Reload Scene")
        save_code_button.clicked.connect(self.save_code_and_reload)
        code_layout.addWidget(save_code_button)

        tab_bar.addTab(code_container, "Code")

        # Split tab - Both views side by side
        split_widget = QWidget()
        split_layout = QHBoxLayout(split_widget)
        split_layout.setContentsMargins(0, 0, 0, 0)

        # Create second pygame widget for split view
        self.pygame_widget_split = PygameWidget(editor_window=self)
        split_layout.addWidget(self.pygame_widget_split, 1)

        # Create second code editor for split view
        self.code_editor_split = QTextEdit()
        self.code_editor_split.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
            }
        """)

        code_split_container = QWidget()
        code_split_layout = QVBoxLayout(code_split_container)
        code_split_layout.addWidget(self.code_editor_split)
        save_code_split_button = QPushButton("Save Code & Reload Scene")
        save_code_split_button.clicked.connect(self.save_code_and_reload)
        code_split_layout.addWidget(save_code_split_button)

        split_layout.addWidget(code_split_container, 1)
        tab_bar.addTab(split_widget, "Split")

        layout.addWidget(tab_bar)
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
        if event.key() == Qt.Key.Key_Space:
            self.pygame_widget.space_held = True
            self.pygame_widget_split.space_held = True
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
        """Create the left panel with Scenes and Hierarchy tabs."""
        dock = QDockWidget("Project", self)
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)

        # Container widget with tabs
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        tabs = QTabWidget()

        # === Scenes Tab ===
        scenes_widget = QWidget()
        scenes_layout = QVBoxLayout(scenes_widget)

        # New scene button
        new_scene_btn = QPushButton("+ New Scene")
        new_scene_btn.clicked.connect(self.create_new_scene)
        scenes_layout.addWidget(new_scene_btn)

        # Scene list
        self.scene_list = QTreeWidget()
        self.scene_list.setHeaderHidden(True)
        self.scene_list.itemClicked.connect(self.on_scene_list_clicked)
        scenes_layout.addWidget(self.scene_list)

        tabs.addTab(scenes_widget, "Scenes")

        # === Hierarchy Tab ===
        hierarchy_widget = QWidget()
        hierarchy_layout = QVBoxLayout(hierarchy_widget)

        # Add sprite button
        add_button = QPushButton("+ Add Sprite")
        add_button.clicked.connect(self.add_sprite)
        hierarchy_layout.addWidget(add_button)

        # Hierarchy tree
        self.hierarchy_tree = QTreeWidget()
        self.hierarchy_tree.setHeaderLabel("Scene Objects")
        self.hierarchy_tree.itemClicked.connect(self.on_hierarchy_item_clicked)
        hierarchy_layout.addWidget(self.hierarchy_tree)

        # Delete button
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(lambda: self.delete_selected_sprite(confirm=True))
        hierarchy_layout.addWidget(delete_button)

        tabs.addTab(hierarchy_widget, "Hierarchy")

        layout.addWidget(tabs)
        dock.setWidget(container)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

        self.update_hierarchy()
        self.update_scene_list()

    def create_properties_panel(self):
        """Create the right properties panel."""
        dock = QDockWidget("Properties", self)
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)

        # Container widget
        container = QWidget()
        layout = QVBoxLayout(container)

        self.properties_label = QLabel("No object selected")
        layout.addWidget(self.properties_label)

        # Property form
        self.properties_form = QFormLayout()
        layout.addLayout(self.properties_form)

        layout.addStretch()

        dock.setWidget(container)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

    def refresh_code_view(self):
        """Load and display the current scene file in all code views."""
        if not self.game.scene_manager or not self.game.scene_manager.current_scene:
            self.code_editor.setPlainText("# No scene loaded")
            self.code_editor_split.setPlainText("# No scene loaded")
            return

        scene_name = self.game.scene_manager.current_scene

        # Find scene file path from config
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

            if scene_file and os.path.exists(scene_file):
                with open(scene_file, 'r') as f:
                    code = f.read()
                # Update all code editor instances
                self.code_editor.setPlainText(code)
                self.code_editor_split.setPlainText(code)
            else:
                error_msg = f"# Scene file not found: {scene_file}"
                self.code_editor.setPlainText(error_msg)
                self.code_editor_split.setPlainText(error_msg)

        except Exception as e:
            error_msg = f"# Error loading scene file: {e}"
            self.code_editor.setPlainText(error_msg)
            self.code_editor_split.setPlainText(error_msg)

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
        self.hierarchy_tree.clear()

        if not self.game.scene_manager or not self.game.scene_manager.current_scene:
            return

        scene = self.game.scene_manager.scenes[self.game.scene_manager.current_scene]

        if hasattr(scene, 'sprite_groups'):
            for group_name, sprite_group in scene.sprite_groups.items():
                group_item = QTreeWidgetItem(self.hierarchy_tree, [group_name])

                for i, sprite in enumerate(sprite_group.sprites):
                    # Use sprite.name if available, otherwise generate default
                    if hasattr(sprite, 'name') and sprite.name:
                        display_name = sprite.name
                    else:
                        display_name = f"{sprite.__class__.__name__}_{i}"
                        # Auto-assign the name to the sprite
                        sprite.name = display_name

                    sprite_item = QTreeWidgetItem(group_item, [display_name])
                    sprite_item.setData(0, Qt.ItemDataRole.UserRole, sprite)  # Store sprite reference

                group_item.setExpanded(True)

    def on_hierarchy_item_clicked(self, item, column):
        """Handle hierarchy item selection."""
        sprite = item.data(0, Qt.ItemDataRole.UserRole)
        if sprite:
            self.selected_sprite = sprite
            self.state.selected_sprite = sprite
            self.update_properties_panel(sprite)

    def update_properties_panel(self, sprite):
        """Update properties panel with sprite data."""
        # Clear existing form
        while self.properties_form.count():
            child = self.properties_form.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not sprite:
            self.properties_label.setText("No object selected")
            return

        # Show sprite name in heading if available
        sprite_name = getattr(sprite, 'name', sprite.__class__.__name__)
        self.properties_label.setText(f"Selected: {sprite_name}")

        # Name (first field for easy editing)
        sprite_name = getattr(sprite, 'name', 'Sprite')
        name_edit = QLineEdit(sprite_name)
        name_edit.returnPressed.connect(lambda: self.on_property_changed(sprite, 'name', name_edit.text()))
        self.properties_form.addRow("Name:", name_edit)

        # Position
        pos_x_edit = QLineEdit(str(round(sprite.position.x, 2)))
        pos_y_edit = QLineEdit(str(round(sprite.position.y, 2)))
        pos_x_edit.returnPressed.connect(lambda: self.on_property_changed(sprite, 'position.x', pos_x_edit.text()))
        pos_y_edit.returnPressed.connect(lambda: self.on_property_changed(sprite, 'position.y', pos_y_edit.text()))
        self.properties_form.addRow("Position X:", pos_x_edit)
        self.properties_form.addRow("Position Y:", pos_y_edit)

        # Size (Width/Height)
        if hasattr(sprite, 'image') and sprite.image:
            width = sprite.image.get_width()
            height = sprite.image.get_height()
        else:
            width = 0
            height = 0

        width_edit = QLineEdit(str(width))
        height_edit = QLineEdit(str(height))
        width_edit.returnPressed.connect(lambda: self.on_property_changed(sprite, 'width', width_edit.text()))
        height_edit.returnPressed.connect(lambda: self.on_property_changed(sprite, 'height', height_edit.text()))
        self.properties_form.addRow("Width:", width_edit)
        self.properties_form.addRow("Height:", height_edit)

        # Origin
        origin_x_edit = QLineEdit(str(round(sprite.origin.x, 2)))
        origin_y_edit = QLineEdit(str(round(sprite.origin.y, 2)))
        origin_x_edit.returnPressed.connect(lambda: self.on_property_changed(sprite, 'origin.x', origin_x_edit.text()))
        origin_y_edit.returnPressed.connect(lambda: self.on_property_changed(sprite, 'origin.y', origin_y_edit.text()))
        self.properties_form.addRow("Origin X:", origin_x_edit)
        self.properties_form.addRow("Origin Y:", origin_y_edit)

        # Layer with buttons
        layer_container = QWidget()
        layer_layout = QHBoxLayout(layer_container)
        layer_layout.setContentsMargins(0, 0, 0, 0)

        layer_edit = QLineEdit(str(getattr(sprite, 'layer', 0)))
        layer_edit.returnPressed.connect(lambda: self.on_property_changed(sprite, 'layer', layer_edit.text()))
        layer_layout.addWidget(layer_edit, 1)

        # Move Forward button (increase layer number)
        move_forward_btn = QPushButton("▲")
        move_forward_btn.setMaximumWidth(30)
        move_forward_btn.setToolTip("Move Forward (increase layer)")
        move_forward_btn.clicked.connect(lambda: self.move_sprite_layer(sprite, 1))
        layer_layout.addWidget(move_forward_btn)

        # Move Backward button (decrease layer number)
        move_backward_btn = QPushButton("▼")
        move_backward_btn.setMaximumWidth(30)
        move_backward_btn.setToolTip("Move Backward (decrease layer)")
        move_backward_btn.clicked.connect(lambda: self.move_sprite_layer(sprite, -1))
        layer_layout.addWidget(move_backward_btn)

        self.properties_form.addRow("Layer:", layer_container)

    def update_viewport(self):
        """Update the Pygame viewport(s)."""
        # Render to main pygame widget (Visual and Split tabs)
        self.render_to_surface(self.pygame_widget)

        # If in split mode, also render to the split pygame widget
        if self.current_view_mode == "Split":
            self.render_to_surface(self.pygame_widget_split)

    def render_to_surface(self, widget):
        """Render scene to a specific pygame widget."""
        surface = widget.get_surface()
        if not surface:
            return

        # Clear background
        surface.fill((60, 60, 65))

        # Render scene
        if self.game.scene_manager and self.game.scene_manager.current_scene:
            scene = self.game.scene_manager.scenes[self.game.scene_manager.current_scene]

            # Draw grid
            from v2_engine.editor import gizmos
            gizmos.draw_grid(surface, self.state.camera, surface.get_size())

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
                    is_selected = sprite == self.state.selected_sprite
                    gizmos.draw_sprite_gizmo(surface, sprite, self.state.camera, is_selected)

        # Update the Qt widget with the rendered surface
        widget.update_from_surface()

    def render_sprite(self, sprite, surface):
        """Render a single sprite to the surface."""
        if not hasattr(sprite, 'image') or sprite.image is None:
            return

        screen_pos = self.state.camera.world_to_screen(sprite.position)

        if self.state.camera.zoom != 1.0:
            original_size = sprite.image.get_size()
            scaled_size = (
                int(original_size[0] * self.state.camera.zoom),
                int(original_size[1] * self.state.camera.zoom)
            )
            scaled_image = pygame.transform.scale(sprite.image, scaled_size)
        else:
            scaled_image = sprite.image

        origin_offset_x = scaled_image.get_width() * sprite.origin.x
        origin_offset_y = scaled_image.get_height() * sprite.origin.y

        render_x = screen_pos.x - origin_offset_x
        render_y = screen_pos.y - origin_offset_y

        surface.blit(scaled_image, (int(render_x), int(render_y)))

    def reset_camera(self):
        """Reset camera to default position."""
        self.state.camera.reset()

    def save_scene(self):
        """Save the current scene to file."""
        if not self.game.scene_manager or not self.game.scene_manager.current_scene:
            print("[Editor] No scene to save")
            return

        scene_name = self.game.scene_manager.current_scene
        scene = self.game.scene_manager.scenes[scene_name]

        # Find scene file path from project config
        import json
        config_path = os.path.join(self.project_path, '2d_project.json')

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

            # Find the scene file path
            scene_file = None
            for scene_info in config.get('scenes', {}).get('scenes', []):
                if scene_info['name'] == scene_name:
                    scene_file = os.path.join(self.project_path, scene_info['file'])
                    break

            if not scene_file:
                # Fallback to guessing
                scene_file = os.path.join(self.project_path, 'scenes', f'{scene_name}.py')
                print(f"[Editor] Warning: Scene file not found in config, using: {scene_file}")

            # Save scene
            self.scene_serializer.save_scene(scene, scene_file)
            print(f"[Editor] Scene saved successfully: {scene_file}")

            # Optional: Save metadata
            metadata_file = scene_file.replace('.py', '.meta.json')
            self.scene_serializer.save_scene_metadata(scene, metadata_file)

            # Refresh code view to show saved changes
            self.refresh_code_view()

        except Exception as e:
            print(f"[Editor] Error saving scene: {e}")
            import traceback
            traceback.print_exc()

    def play_scene(self):
        """Play the scene in a separate window."""
        # Check if game is already running
        if self.play_process and self.play_process.poll() is None:
            print("[Editor] Game is already running")
            return

        # Auto-save before playing
        print("[Editor] Auto-saving scene before play...")
        self.save_scene()

        # Launch game in separate process
        try:
            # Use the v2_engine main entry point to run the game
            python_executable = sys.executable
            game_script = os.path.join(os.path.dirname(__file__), '..', 'main.py')

            # Check if main.py exists
            if not os.path.exists(game_script):
                print(f"[Editor] Error: Game launcher not found at {game_script}")
                # Create a simple launcher script
                self._create_game_launcher(game_script)

            # Get current scene name
            current_scene = self.game.scene_manager.current_scene if self.game.scene_manager else None

            # Launch subprocess with current scene
            args = [python_executable, game_script, self.project_path]
            if current_scene:
                args.append(current_scene)
                print(f"[Editor] Playing scene: {current_scene}")

            self.play_process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"[Editor] Game launched (PID: {self.play_process.pid})")

            # Check if process is still running after a brief moment
            import time
            time.sleep(0.5)
            if self.play_process.poll() is not None:
                # Process exited - read output
                stdout, stderr = self.play_process.communicate(timeout=1)
                print(f"[Editor] Game process exited with code {self.play_process.returncode}")
                if stdout:
                    print(f"[Editor] Game stdout:\n{stdout}")
                if stderr:
                    print(f"[Editor] Game stderr:\n{stderr}")
                self.play_process = None
                return

            # Update Play menu to show Stop option
            # TODO: Add visual feedback in UI

        except Exception as e:
            print(f"[Editor] Error launching game: {e}")
            import traceback
            traceback.print_exc()

    def stop_play(self):
        """Stop the running game."""
        if self.play_process and self.play_process.poll() is None:
            self.play_process.terminate()
            try:
                self.play_process.wait(timeout=2)
                print("[Editor] Game stopped")
            except subprocess.TimeoutExpired:
                print("[Editor] Game didn't stop gracefully, forcing kill...")
                self.play_process.kill()
                self.play_process.wait()
                print("[Editor] Game forcefully killed")
            self.play_process = None
        else:
            print("[Editor] No game running")

    def _create_game_launcher(self, script_path):
        """Create a simple game launcher script if it doesn't exist."""
        launcher_code = '''#!/usr/bin/env python3
"""
V2 Engine Game Launcher
"""
import sys
import os

# Add engine to path
engine_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(engine_root))

from v2_engine.core.game import Game

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python main.py <project_path>")
        sys.exit(1)

    project_path = sys.argv[1]
    game = Game(project_path, editor_mode=False)

    # Initialize engine systems
    if not game.initialize():
        print("[Game] Failed to initialize game engine")
        sys.exit(1)

    # Load entry scene
    entry_scene = game.project_config.get('scenes', {}).get('entry_scene')
    if entry_scene:
        game.scene_manager.load_scene(entry_scene)

    # Run game loop
    game.run()
'''
        os.makedirs(os.path.dirname(script_path), exist_ok=True)
        with open(script_path, 'w') as f:
            f.write(launcher_code)
        print(f"[Editor] Created game launcher: {script_path}")

    def add_sprite(self):
        """Add a new sprite to the scene."""
        if not self.game.scene_manager or not self.game.scene_manager.current_scene:
            print("[Editor] No scene loaded")
            return

        scene = self.game.scene_manager.scenes[self.game.scene_manager.current_scene]

        # Create new sprite at center of viewport
        from v2_engine.sprites.sprite import Sprite

        # Calculate center of viewport in world coords
        viewport_size = self.pygame_widget.get_surface().get_size()
        screen_center = Vector2(viewport_size[0] / 2, viewport_size[1] / 2)
        world_center = self.state.camera.screen_to_world(screen_center)

        # Create sprite
        new_sprite = Sprite(world_center.x, world_center.y)
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

    def copy_sprite(self):
        """Copy the currently selected sprite."""
        if not self.selected_sprite:
            print("[Editor] No sprite selected to copy")
            return

        # Store a reference to the selected sprite for pasting
        self.copied_sprite = self.selected_sprite
        sprite_name = getattr(self.copied_sprite, 'name', self.copied_sprite.__class__.__name__)
        print(f"[Editor] Copied sprite: {sprite_name}")

    def paste_sprite(self):
        """Paste the copied sprite."""
        if not self.copied_sprite:
            print("[Editor] No sprite copied")
            return

        if not self.game.scene_manager or not self.game.scene_manager.current_scene:
            print("[Editor] No scene loaded")
            return

        scene = self.game.scene_manager.scenes[self.game.scene_manager.current_scene]

        # Create new sprite as a copy
        from v2_engine.sprites.sprite import Sprite
        import copy

        # Deep copy the sprite to duplicate all attributes
        new_sprite = Sprite()

        # Copy basic properties
        new_sprite.position = Vector2(self.copied_sprite.position.x + 20, self.copied_sprite.position.y + 20)  # Offset slightly
        new_sprite.origin = Vector2(self.copied_sprite.origin.x, self.copied_sprite.origin.y)
        new_sprite.layer = getattr(self.copied_sprite, 'layer', 0)

        # Copy image
        if hasattr(self.copied_sprite, 'image') and self.copied_sprite.image:
            new_sprite.image = self.copied_sprite.image.copy()

        # Copy name with " (Copy)" suffix
        original_name = getattr(self.copied_sprite, 'name', 'Sprite')
        new_sprite.name = f"{original_name} (Copy)"

        # Add to 'all' group
        if 'all' in scene.sprite_groups:
            scene.sprite_groups['all'].add(new_sprite)
            print(f"[Editor] Pasted sprite: {new_sprite.name}")

            # Update hierarchy
            self.update_hierarchy()

            # Select the new sprite
            self.selected_sprite = new_sprite
            self.state.selected_sprite = new_sprite
            self.update_properties_panel(new_sprite)
        else:
            print("[Editor] No 'all' sprite group found")

    def on_viewport_mouse_press(self, x, y):
        """Handle mouse press in viewport."""
        # Convert screen coords to world coords
        screen_pos = Vector2(x, y)
        world_pos = self.state.camera.screen_to_world(screen_pos)

        # Try to select sprite at this position
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
                        self.selected_sprite = sprite
                        self.state.selected_sprite = sprite
                        self.update_properties_panel(sprite)
                        print(f"[Editor] Selected sprite: {sprite.__class__.__name__}")
                        return

                # No sprite clicked - deselect
                self.selected_sprite = None
                self.state.selected_sprite = None
                self.update_properties_panel(None)

    def on_viewport_mouse_drag(self, x, y):
        """Handle mouse drag in viewport."""
        if self.selected_sprite:
            # Convert screen coords to world coords
            screen_pos = Vector2(x, y)
            world_pos = self.state.camera.screen_to_world(screen_pos)

            # Update sprite position
            self.selected_sprite.position = world_pos
            # Note: Properties panel will update on mouse release

    def on_viewport_mouse_release(self):
        """Handle mouse release - update properties after drag."""
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
            elif property_name in ['width', 'height']:
                # Resize sprite image
                value = int(value_str)
                if value <= 0:
                    print(f"[Editor] Invalid {property_name}: must be > 0")
                    return

                if hasattr(sprite, 'image') and sprite.image:
                    current_width = sprite.image.get_width()
                    current_height = sprite.image.get_height()

                    if property_name == 'width':
                        new_width = value
                        new_height = current_height
                    else:  # height
                        new_width = current_width
                        new_height = value

                    # Scale the image
                    sprite.image = pygame.transform.scale(sprite.image, (new_width, new_height))
                    print(f"[Editor] Resized sprite to {new_width}x{new_height}")

            elif '.' in property_name:
                # Nested property (e.g., position.x, origin.y)
                obj_name, attr_name = property_name.split('.')
                obj = getattr(sprite, obj_name)
                value = float(value_str)
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

    def update_scene_list(self):
        """Update the Scene list in the left panel."""
        import json

        self.scene_list.clear()

        # Read project config to get scene list
        config_path = os.path.join(self.project_path, '2d_project.json')
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

            scenes = config.get('scenes', {}).get('scenes', [])
            current_scene = self.game.scene_manager.current_scene if self.game.scene_manager else None

            for scene_info in scenes:
                scene_name = scene_info['name']
                item = QTreeWidgetItem(self.scene_list, [scene_name])

                # Mark current scene with bold font
                if scene_name == current_scene:
                    from PyQt6.QtGui import QFont
                    font = QFont()
                    font.setBold(True)
                    item.setFont(0, font)

                # Store scene name in item data
                item.setData(0, Qt.ItemDataRole.UserRole, scene_name)

        except Exception as e:
            print(f"[Editor] Error updating scene list: {e}")

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

    def switch_to_scene(self, scene_name: str):
        """Switch to a different scene."""
        if not self.game.scene_manager:
            print("[Editor] No scene manager available")
            return

        if scene_name == self.game.scene_manager.current_scene:
            print(f"[Editor] Already viewing scene: {scene_name}")
            return

        try:
            # Load and transition to the scene
            self.game.scene_manager.load_scene(scene_name)
            self.game.scene_manager._perform_scene_transition()

            # Update UI
            self.update_hierarchy()
            self.refresh_code_view()
            self.update_scene_menu()
            self.update_scene_list()

            # Clear selection
            self.selected_sprite = None
            self.state.selected_sprite = None
            self.update_properties_panel(None)

            print(f"[Editor] Switched to scene: {scene_name}")

        except Exception as e:
            print(f"[Editor] Error switching to scene '{scene_name}': {e}")
            import traceback
            traceback.print_exc()

    def create_new_scene(self):
        """Create a new scene with dialog."""
        # Prompt for scene name
        scene_name, ok = QInputDialog.getText(
            self,
            'New Scene',
            'Enter scene name (e.g., "level_2", "menu"):',
            text='new_scene'
        )

        if not ok or not scene_name:
            return

        # Validate scene name (alphanumeric and underscores only)
        import re
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', scene_name):
            QMessageBox.warning(
                self,
                'Invalid Name',
                'Scene name must start with a letter or underscore and contain only letters, numbers, and underscores.'
            )
            return

        try:
            import json

            # Read project config
            config_path = os.path.join(self.project_path, '2d_project.json')
            with open(config_path, 'r') as f:
                config = json.load(f)

            # Check if scene already exists
            scenes = config.get('scenes', {}).get('scenes', [])
            for scene_info in scenes:
                if scene_info['name'] == scene_name:
                    QMessageBox.warning(
                        self,
                        'Scene Exists',
                        f'A scene named "{scene_name}" already exists.'
                    )
                    return

            # Create scene file path
            class_name = ''.join(word.capitalize() for word in scene_name.split('_')) + 'Scene'
            scene_file = f'scenes/{scene_name}.py'
            scene_file_path = os.path.join(self.project_path, scene_file)

            # Create scenes directory if it doesn't exist
            os.makedirs(os.path.dirname(scene_file_path), exist_ok=True)

            # Generate empty scene file
            scene_code = f'''"""
Scene: {class_name}
Generated by Scribe Engine V2 Editor
"""

import pygame
from v2_engine.core.scene import Scene
from v2_engine.core.camera import Camera
from v2_engine.utils.math import Vector2
from v2_engine.sprites.sprite import Sprite

class {class_name}(Scene):
    """Auto-generated scene."""

    def __init__(self, game):
        super().__init__(game)

        # Initialize sprite groups
        from v2_engine.sprites.group import SpriteGroup
        self.sprite_groups["all"] = SpriteGroup("all")

    def on_enter(self):
        """Called when scene becomes active."""
        super().on_enter()

        # Initialize camera
        screen_width = self.game.screen.get_width()
        screen_height = self.game.screen.get_height()
        self.camera = Camera(screen_width, screen_height)

        # Add sprites here


    def render(self, screen):
        """Render all sprites with camera."""
        # Clear screen
        screen.fill((40, 40, 50))  # Dark gray background

        # Render all sprite groups
        self.sprite_groups["all"].render(screen, self.camera)

'''

            # Write scene file
            with open(scene_file_path, 'w') as f:
                f.write(scene_code)

            # Update project config
            scenes.append({
                'name': scene_name,
                'file': scene_file,
                'class': class_name
            })

            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            print(f"[Editor] Created new scene: {scene_name} at {scene_file}")

            # Reload project config and scenes
            self.game.project_config = self.game.load_project_config()

            # Import and register the new scene
            try:
                module_path = scene_file.replace('/', '.').replace('.py', '')
                import importlib
                module = importlib.import_module(module_path)
                SceneClass = getattr(module, class_name)
                scene_instance = SceneClass(self.game)
                self.game.scene_manager.register_scene(scene_name, scene_instance)
                print(f"[Editor] Registered scene: {scene_name}")
            except Exception as e:
                print(f"[Editor] Error registering scene: {e}")
                import traceback
                traceback.print_exc()

            # Update scene menu and list
            self.update_scene_menu()
            self.update_scene_list()

            # Switch to the new scene
            self.switch_to_scene(scene_name)

        except Exception as e:
            print(f"[Editor] Error creating scene: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                'Error',
                f'Failed to create scene: {str(e)}'
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
