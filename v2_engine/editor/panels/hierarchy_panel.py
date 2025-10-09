"""
Hierarchy Panel for Scribe Engine V2 Editor

Displays scene hierarchy, assets browser, and scene list in collapsible sections.
"""

import os
from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget,
    QTreeWidgetItem, QLabel, QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPixmap


class HierarchyPanel(QDockWidget):
    """
    Project hierarchy panel showing:
    - Current scene entities
    - Asset browser with preview
    - All scenes list
    """

    # Signals
    sprite_selected = pyqtSignal(object)  # sprite object
    sprite_delete_requested = pyqtSignal()
    asset_selected = pyqtSignal(str)  # file path
    asset_assign_requested = pyqtSignal()
    scene_selected = pyqtSignal(str)  # scene name
    add_object_requested = pyqtSignal()
    create_scene_requested = pyqtSignal()

    def __init__(self, parent, theme):
        super().__init__("Project", parent)
        self.theme = theme
        self.editor = parent
        self.selected_asset_path = None

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.setMinimumWidth(324)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the hierarchy panel UI."""
        # Scrollable container
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Main container
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(
            self.theme.spacing_small, self.theme.spacing_small,
            self.theme.spacing_small, self.theme.spacing_small
        )
        layout.setSpacing(self.theme.spacing_medium)

        # === Current Scene Section ===
        self.scene_section_header = self._create_collapsible_header(
            "Scene: Loading...", collapsed=False, add_button=False
        )
        layout.addWidget(self.scene_section_header)

        self.scene_section_body = QWidget()
        scene_body_layout = QVBoxLayout(self.scene_section_body)
        scene_body_layout.setContentsMargins(
            self.theme.spacing_medium, self.theme.spacing_small,
            self.theme.spacing_small, self.theme.spacing_small
        )
        scene_body_layout.setSpacing(self.theme.spacing_small)

        # Entities subheader with + button
        self.entities_header = self._create_collapsible_header(
            "Entities", collapsed=False, add_button=True,
            add_callback=lambda: self.add_object_requested.emit()
        )
        scene_body_layout.addWidget(self.entities_header)

        # Entities body (hierarchy tree)
        self.entities_body = QWidget()
        entities_body_layout = QVBoxLayout(self.entities_body)
        entities_body_layout.setContentsMargins(
            self.theme.spacing_medium, self.theme.spacing_small,
            self.theme.spacing_small, self.theme.spacing_small
        )
        entities_body_layout.setSpacing(self.theme.spacing_small)

        # Hierarchy tree
        self.hierarchy_tree = QTreeWidget()
        self.hierarchy_tree.setHeaderHidden(True)
        self.hierarchy_tree.itemClicked.connect(self._on_hierarchy_item_clicked)
        entities_body_layout.addWidget(self.hierarchy_tree)

        # Delete button
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(lambda: self.sprite_delete_requested.emit())
        entities_body_layout.addWidget(delete_button)

        scene_body_layout.addWidget(self.entities_body)
        layout.addWidget(self.scene_section_body)

        # Link headers to bodies
        self.scene_section_header.section_body = self.scene_section_body
        self.entities_header.section_body = self.entities_body

        # === Assets Section ===
        self.assets_section_header = self._create_collapsible_header(
            "Assets", collapsed=True, add_button=False
        )
        layout.addWidget(self.assets_section_header)

        self.assets_section_body = QWidget()
        assets_body_layout = QVBoxLayout(self.assets_section_body)
        assets_body_layout.setContentsMargins(
            self.theme.spacing_medium, self.theme.spacing_small,
            self.theme.spacing_small, self.theme.spacing_small
        )
        assets_body_layout.setSpacing(self.theme.spacing_small)

        # Asset browser tree
        self.asset_tree = QTreeWidget()
        self.asset_tree.setHeaderHidden(True)
        self.asset_tree.itemClicked.connect(self._on_asset_clicked)
        assets_body_layout.addWidget(self.asset_tree)

        # Asset preview
        preview_label = QLabel("Preview:")
        preview_label.setProperty("type", "caption")
        assets_body_layout.addWidget(preview_label)

        self.asset_preview = QLabel()
        self.asset_preview.setMinimumHeight(100)
        self.asset_preview.setMaximumHeight(200)
        self.asset_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.asset_preview.setStyleSheet(
            f"border: 1px solid {self.theme.border_strong}; "
            f"background-color: {self.theme.background_dark};"
        )
        self.asset_preview.setText("No preview")
        assets_body_layout.addWidget(self.asset_preview)

        # Assign button
        self.assign_asset_btn = QPushButton("Assign to Selected Sprite")
        self.assign_asset_btn.setEnabled(False)
        self.assign_asset_btn.clicked.connect(lambda: self.asset_assign_requested.emit())
        assets_body_layout.addWidget(self.assign_asset_btn)

        self.assets_section_body.setVisible(False)  # Start collapsed
        layout.addWidget(self.assets_section_body)
        self.assets_section_header.section_body = self.assets_section_body

        # === All Scenes Section ===
        self.scenes_section_header = self._create_collapsible_header(
            "All Scenes", collapsed=True, add_button=True,
            add_callback=lambda: self.create_scene_requested.emit()
        )
        layout.addWidget(self.scenes_section_header)

        self.scenes_section_body = QWidget()
        scenes_body_layout = QVBoxLayout(self.scenes_section_body)
        scenes_body_layout.setContentsMargins(
            self.theme.spacing_medium, self.theme.spacing_small,
            self.theme.spacing_small, self.theme.spacing_small
        )
        scenes_body_layout.setSpacing(self.theme.spacing_small)

        # Scene list
        self.scene_list = QTreeWidget()
        self.scene_list.setHeaderHidden(True)
        self.scene_list.itemClicked.connect(self._on_scene_list_clicked)
        scenes_body_layout.addWidget(self.scene_list)

        self.scenes_section_body.setVisible(False)  # Start collapsed
        layout.addWidget(self.scenes_section_body)
        self.scenes_section_header.section_body = self.scenes_section_body

        # Add stretch to push everything to top
        layout.addStretch()

        scroll_area.setWidget(container)
        self.setWidget(scroll_area)

    def _create_collapsible_header(self, title, collapsed=False, add_button=False, add_callback=None):
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

    def _on_hierarchy_item_clicked(self, item, column):
        """Handle hierarchy item selection."""
        sprite = item.data(0, Qt.ItemDataRole.UserRole)
        if sprite:
            self.sprite_selected.emit(sprite)

    def _on_asset_clicked(self, item, column):
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
        self.asset_selected.emit(file_path)

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
                # Enable assign button if sprite is selected in editor
                # (editor will handle this through enable_asset_assign)
            else:
                self.asset_preview.setText("Failed to load image")
                self.assign_asset_btn.setEnabled(False)
        except Exception as e:
            print(f"[HierarchyPanel] Error loading asset preview: {e}")
            self.asset_preview.setText("Error loading preview")
            self.assign_asset_btn.setEnabled(False)

    def _on_scene_list_clicked(self, item, column):
        """Handle scene list item click."""
        scene_name = item.data(0, Qt.ItemDataRole.UserRole)
        if scene_name:
            self.scene_selected.emit(scene_name)

    # Public API methods

    def update_hierarchy(self, game):
        """Update the hierarchy tree with scene objects."""
        from v2_engine.sprites.sprite_object import SpriteObject

        self.hierarchy_tree.clear()

        if not game.scene_manager or not game.scene_manager.current_scene:
            return

        # Update scene header with current scene name
        scene_name = game.scene_manager.current_scene
        self.scene_section_header.title_label.setText(f"Scene: {scene_name}")

        scene = game.scene_manager.scenes[scene_name]

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

                    # Add visual indicator based on visibility
                    sprite_item = QTreeWidgetItem(group_item, [display_name])
                    sprite_item.setData(0, Qt.ItemDataRole.UserRole, sprite)  # Store sprite reference

                    # Color based on visibility state
                    is_visible = getattr(sprite, 'visible', True)
                    if is_visible:
                        # White/bright for visible objects
                        sprite_item.setForeground(0, QColor(255, 255, 255))
                    else:
                        # Dim gray for invisible objects (ghosted)
                        sprite_item.setForeground(0, QColor(128, 128, 128))

                group_item.setExpanded(True)

    def update_assets(self, project_path):
        """Populate the asset browser with files from the assets directory."""
        self.asset_tree.clear()

        assets_path = os.path.join(project_path, 'assets')

        if not os.path.exists(assets_path):
            # Create assets directory if it doesn't exist
            os.makedirs(assets_path, exist_ok=True)
            no_assets_item = QTreeWidgetItem(self.asset_tree, ["No assets found"])
            return

        # Supported image extensions
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}

        # Walk through assets directory
        for root, dirs, files in os.walk(assets_path):
            # Get relative path from assets root
            rel_path = os.path.relpath(root, assets_path)

            # Create folder items
            if rel_path == '.':
                parent_item = self.asset_tree.invisibleRootItem()
            else:
                # Create nested tree structure
                path_parts = rel_path.split(os.sep)
                parent_item = self.asset_tree.invisibleRootItem()

                # Find or create parent items
                for part in path_parts:
                    found = False
                    for i in range(parent_item.childCount()):
                        child = parent_item.child(i)
                        if child.text(0) == part and child.data(0, Qt.ItemDataRole.UserRole) is None:
                            parent_item = child
                            found = True
                            break

                    if not found:
                        new_item = QTreeWidgetItem(parent_item, [part])
                        new_item.setData(0, Qt.ItemDataRole.UserRole, None)  # Mark as folder
                        parent_item = new_item

            # Add files
            for file in sorted(files):
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in image_extensions:
                    file_path = os.path.join(root, file)
                    file_item = QTreeWidgetItem(parent_item, [file])
                    file_item.setData(0, Qt.ItemDataRole.UserRole, file_path)  # Store full path

        # Expand all folders by default
        self.asset_tree.expandAll()

    def update_scenes(self, scenes_config, current_scene=None):
        """Update the scene list."""
        self.scene_list.clear()

        for scene_info in scenes_config:
            scene_name = scene_info['name']
            item = QTreeWidgetItem(self.scene_list, [scene_name])

            # Mark current scene with bold font
            if scene_name == current_scene:
                font = QFont()
                font.setBold(True)
                item.setFont(0, font)

            # Store scene name in item data
            item.setData(0, Qt.ItemDataRole.UserRole, scene_name)

    def enable_asset_assign(self, enabled):
        """Enable/disable the asset assign button."""
        self.assign_asset_btn.setEnabled(enabled and self.selected_asset_path is not None)

    def get_selected_asset_path(self):
        """Get the currently selected asset path."""
        return self.selected_asset_path
