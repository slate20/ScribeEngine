"""
Properties Panel Widget for the Scribe V2 Editor.

Displays and allows editing of properties for the selected object
(sprite, scene, etc.).
"""
import os
import uuid
from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QCheckBox, QHBoxLayout, QGridLayout, QPushButton, QColorDialog, QFrame,
    QComboBox, QMessageBox, QScrollArea
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from v2_engine.utils.math import Vector2
from v2_engine.sprites.sprite_object import SpriteObject
from v2_engine.editor.widgets.component_card import ComponentCard
from v2_engine.core.game_state import get_game_state
from v2_engine.editor.widgets.behavior_browser import BehaviorBrowserDialog


class PropertiesPanel(QDockWidget):
    """
    A QDockWidget that displays and allows editing of properties for the
    selected object (sprite, scene, etc.) in the editor.
    """

    def __init__(self, editor_window):
        super().__init__("Properties", editor_window)
        self.editor = editor_window
        self.theme = self.editor.theme

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.setMinimumWidth(416)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)

        self.properties_label = QLabel("No object selected")
        layout.addWidget(self.properties_label)

        self.properties_form = QFormLayout()
        layout.addLayout(self.properties_form)

        layout.addStretch()

        scroll_area.setWidget(container)
        self.setWidget(scroll_area)

    def update_for_selection(self):
        """
        Public method to update the panel based on the current selection
        in the editor state.
        """
        selected_sprites = self.editor.selected_sprites
        if len(selected_sprites) > 1:
            self.update_properties_panel_multi(selected_sprites)
        elif len(selected_sprites) == 1:
            self.update_properties_panel(selected_sprites[0])
        else:
            self.update_properties_panel(None)

    def update_properties_panel(self, sprite):
        """Update properties panel with sprite data."""
        while self.properties_form.count():
            child = self.properties_form.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not sprite:
            self.properties_label.setText("Scene Background")
            if hasattr(self.editor, 'assign_asset_btn'):
                self.editor.assign_asset_btn.setEnabled(False)
            self.show_scene_background_properties()
            return

        sprite_name = getattr(sprite, 'name', sprite.__class__.__name__)
        self.properties_label.setText(f"Selected: {sprite_name}")

        if hasattr(self.editor, 'assign_asset_btn') and hasattr(self.editor, 'selected_asset_path'):
            self.editor.assign_asset_btn.setEnabled(self.editor.selected_asset_path is not None)

        name_edit = QLineEdit(getattr(sprite, 'name', 'Sprite'))
        name_edit.returnPressed.connect(lambda: self.editor.on_property_changed(sprite, 'name', name_edit.text()))
        self.properties_form.addRow("Name:", name_edit)

        if hasattr(sprite, 'image_path') and sprite.image_path:
            asset_full_path = os.path.join(self.editor.project_path, sprite.image_path)
            if not os.path.exists(asset_full_path):
                warning_label = QLabel(f"⚠️ Missing Asset\n{sprite.image_path}")
                warning_label.setStyleSheet(f"color: {self.theme.error}; background-color: {self.theme.background_dark}; padding: {self.theme.spacing_small}px; border: 1px solid {self.theme.error};")
                warning_label.setWordWrap(True)
                self.properties_form.addRow("", warning_label)

        pos_x_edit = QLineEdit(str(round(sprite.position.x, 2)))
        pos_y_edit = QLineEdit(str(round(sprite.position.y, 2)))
        pos_x_edit.returnPressed.connect(lambda: self.editor.on_property_changed(sprite, 'position.x', pos_x_edit.text()))
        pos_y_edit.returnPressed.connect(lambda: self.editor.on_property_changed(sprite, 'position.y', pos_y_edit.text()))
        self.properties_form.addRow("Position X:", pos_x_edit)
        self.properties_form.addRow("Position Y:", pos_y_edit)

        if isinstance(sprite, SpriteObject) and hasattr(sprite, 'image') and sprite.image:
            base_width = sprite.image.get_width()
            base_height = sprite.image.get_height()
            sprite_scale = getattr(sprite, 'scale', Vector2(1, 1))
            width = int(base_width * sprite_scale.x)
            height = int(base_height * sprite_scale.y)

            width_edit = QLineEdit(str(width))
            height_edit = QLineEdit(str(height))
            width_edit.returnPressed.connect(lambda: self.editor.on_property_changed(sprite, 'width', width_edit.text()))
            height_edit.returnPressed.connect(lambda: self.editor.on_property_changed(sprite, 'height', height_edit.text()))
            self.properties_form.addRow("Width:", width_edit)
            self.properties_form.addRow("Height:", height_edit)

        sprite_scale = getattr(sprite, 'scale', Vector2(1, 1))
        scale_x_edit = QLineEdit(str(round(sprite_scale.x, 2)))
        scale_y_edit = QLineEdit(str(round(sprite_scale.y, 2)))
        scale_x_edit.returnPressed.connect(lambda: self.editor.on_property_changed(sprite, 'scale.x', scale_x_edit.text()))
        scale_y_edit.returnPressed.connect(lambda: self.editor.on_property_changed(sprite, 'scale.y', scale_y_edit.text()))
        self.properties_form.addRow("Scale X:", scale_x_edit)
        self.properties_form.addRow("Scale Y:", scale_y_edit)

        sprite_rotation = getattr(sprite, 'rotation', 0)
        rotation_edit = QLineEdit(str(round(sprite_rotation, 1)))
        rotation_edit.returnPressed.connect(lambda: self.editor.on_property_changed(sprite, 'rotation', rotation_edit.text()))
        self.properties_form.addRow("Rotation:", rotation_edit)

        origin_container = QWidget()
        origin_layout = QVBoxLayout(origin_container)
        origin_layout.setContentsMargins(0, 0, 0, 0)
        origin_layout.setSpacing(self.theme.spacing_small)

        origin_inputs = QWidget()
        origin_inputs_layout = QHBoxLayout(origin_inputs)
        origin_inputs_layout.setContentsMargins(0, 0, 0, 0)
        origin_inputs_layout.setSpacing(self.theme.spacing_small)

        origin_x_edit = QLineEdit(str(round(sprite.origin.x, 2)))
        origin_y_edit = QLineEdit(str(round(sprite.origin.y, 2)))
        origin_x_edit.returnPressed.connect(lambda: self.editor.on_property_changed(sprite, 'origin.x', origin_x_edit.text()))
        origin_y_edit.returnPressed.connect(lambda: self.editor.on_property_changed(sprite, 'origin.y', origin_y_edit.text()))

        origin_inputs_layout.addWidget(QLabel("X:"))
        origin_inputs_layout.addWidget(origin_x_edit, 1)
        origin_inputs_layout.addWidget(QLabel("Y:"))
        origin_inputs_layout.addWidget(origin_y_edit, 1)
        origin_layout.addWidget(origin_inputs)

        presets_widget = QWidget()
        presets_layout = QGridLayout(presets_widget)
        presets_layout.setContentsMargins(0, 0, 0, 0)
        presets_layout.setSpacing(2)

        presets = [
            ("TL", 0.0, 0.0, "Top-Left"), ("TC", 0.5, 0.0, "Top-Center"), ("TR", 1.0, 0.0, "Top-Right"),
            ("ML", 0.0, 0.5, "Middle-Left"), ("C", 0.5, 0.5, "Center"), ("MR", 1.0, 0.5, "Middle-Right"),
            ("BL", 0.0, 1.0, "Bottom-Left"), ("BC", 0.5, 1.0, "Bottom-Center"), ("BR", 1.0, 1.0, "Bottom-Right"),
        ]

        for i, (label, x, y, tooltip) in enumerate(presets):
            btn = QPushButton(label)
            btn.setMaximumWidth(35)
            btn.setMaximumHeight(25)
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda checked, ox=x, oy=y, s=sprite: self.editor.set_origin_preset(s, ox, oy))
            row = i // 3
            col = i % 3
            presets_layout.addWidget(btn, row, col)

        origin_layout.addWidget(presets_widget)
        self.properties_form.addRow("Origin:", origin_container)

        layer_container = QWidget()
        layer_layout = QHBoxLayout(layer_container)
        layer_layout.setContentsMargins(0, 0, 0, 0)
        layer_edit = QLineEdit(str(getattr(sprite, 'layer', 0)))
        layer_edit.returnPressed.connect(lambda: self.editor.on_property_changed(sprite, 'layer', layer_edit.text()))
        layer_layout.addWidget(layer_edit, 1)

        move_forward_btn = QPushButton("▲")
        move_forward_btn.setMaximumWidth(30)
        move_forward_btn.setToolTip("Move Forward (increase layer)")
        move_forward_btn.clicked.connect(lambda: self.editor.move_sprite_layer(sprite, 1))
        layer_layout.addWidget(move_forward_btn)

        move_backward_btn = QPushButton("▼")
        move_backward_btn.setMaximumWidth(30)
        move_backward_btn.setToolTip("Move Backward (decrease layer)")
        move_backward_btn.clicked.connect(lambda: self.editor.move_sprite_layer(sprite, -1))
        layer_layout.addWidget(move_backward_btn)
        self.properties_form.addRow("Layer:", layer_container)

        visible_checkbox = QCheckBox("Visible (runtime rendering)")
        visible_checkbox.setChecked(getattr(sprite, 'visible', True))
        visible_checkbox.stateChanged.connect(lambda state: self.editor.on_visible_changed(sprite, state == 2))
        self.properties_form.addRow("Visible:", visible_checkbox)

        color_container = QWidget()
        color_layout = QHBoxLayout(color_container)
        color_layout.setContentsMargins(0, 0, 0, 0)
        sprite_color = getattr(sprite, 'color', (255, 255, 255))
        if hasattr(sprite, 'image') and sprite.image:
            try:
                center_color = sprite.image.get_at((sprite.image.get_width() // 2, sprite.image.get_height() // 2))
                sprite_color = (center_color.r, center_color.g, center_color.b)
            except:
                pass
        
        color_btn = QPushButton()
        color_btn.setMaximumWidth(100)
        color_btn.setStyleSheet(f"background-color: rgb({sprite_color[0]}, {sprite_color[1]}, {sprite_color[2]}); border: 1px solid {self.theme.border_strong};")
        color_btn.clicked.connect(lambda: self.open_color_picker(sprite))
        color_layout.addWidget(color_btn)

        color_label = QLabel(f"RGB({sprite_color[0]}, {sprite_color[1]}, {sprite_color[2]})")
        color_layout.addWidget(color_label)
        self.properties_form.addRow("Color:", color_container)

        persistent_checkbox = QCheckBox("Make this sprite persistent across scenes")
        is_persistent = getattr(sprite, 'is_persistent', False)
        persistent_checkbox.setChecked(is_persistent)
        persistent_checkbox.stateChanged.connect(lambda state: self.on_persistent_changed(sprite, state == 2))
        self.properties_form.addRow("Persistent:", persistent_checkbox)

        if is_persistent:
            entity_id = getattr(sprite, 'entity_id', '')
            entity_id_container = QWidget()
            entity_id_layout = QHBoxLayout(entity_id_container)
            entity_id_layout.setContentsMargins(0, 0, 0, 0)
            entity_id_edit = QLineEdit(entity_id or '')
            entity_id_edit.setPlaceholderText("Auto-generated if empty")
            entity_id_edit.returnPressed.connect(lambda: self.on_entity_id_changed(sprite, entity_id_edit.text()))
            entity_id_layout.addWidget(entity_id_edit)
            info_label = QLabel("ℹ️")
            info_label.setToolTip("Unique identifier for this persistent entity. Leave empty for auto-generation.")
            entity_id_layout.addWidget(info_label)
            self.properties_form.addRow("Entity ID:", entity_id_container)

        self.add_components_section(sprite)

    def update_properties_panel_multi(self, sprites):
        """Update properties panel for multiple selected sprites."""
        while self.properties_form.count():
            child = self.properties_form.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not sprites:
            self.update_properties_panel(None)
            return

        count = len(sprites)
        self.properties_label.setText(f"Multiple Objects ({count} selected)")

        if hasattr(self.editor, 'assign_asset_btn'):
            self.editor.assign_asset_btn.setEnabled(False)

        info_label = QLabel(f"Select a single sprite to edit properties.\n{count} sprites selected.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"color: {self.theme.text_secondary}; padding: {self.theme.spacing_medium}px;")
        self.properties_form.addRow("", info_label)

        deselect_btn = QPushButton("Deselect All")
        deselect_btn.clicked.connect(self.editor.deselect_all)
        self.properties_form.addRow("", deselect_btn)

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
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.properties_form.addRow(separator)

        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(self.theme.spacing_small)

        components_label = QLabel("Behaviors")
        components_label.setProperty("type", "header")
        header_layout.addWidget(components_label)
        header_layout.addStretch()

        add_btn = QPushButton("+")
        add_btn.setFixedSize(28, 28)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.accent_primary}; color: white; font-weight: bold;
                font-size: 18px; border: none; border-radius: 14px; padding: 0px; text-align: center;
            }}
            QPushButton:hover {{ background-color: {self.theme.accent_hover}; }}
        """)
        add_btn.setToolTip("Add Behavior")
        add_btn.clicked.connect(lambda: self.show_add_component_dialog(sprite))
        header_layout.addWidget(add_btn)
        self.properties_form.addRow(header_container)

        if hasattr(sprite, 'components') and sprite.components:
            for component_type, component in sprite.components.items():
                card = ComponentCard(component, sprite, self.editor)
                card.remove_requested.connect(lambda comp_type=component.__class__: self.remove_component_from_sprite(sprite, comp_type))
                card.property_changed.connect(lambda prop_name, value, c=component, s=sprite: self.on_component_property_changed(c, prop_name, value, s))
                card.edit_code_requested.connect(self.editor.on_edit_behavior_code)
                self.properties_form.addRow(card)

    def remove_component_from_sprite(self, sprite, component_type):
        """Remove a component from the sprite."""
        reply = QMessageBox.question(
            self,
            'Remove Component',
            f'Remove {component_type.__name__} component?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            sprite.remove_component(component_type)
            self.update_for_selection()
            self.editor.update_viewport()

    def on_component_property_changed(self, component, attr_name, value, sprite):
        """Handle component property changes."""
        current_value = getattr(component, attr_name)
        try:
            if isinstance(current_value, bool):
                new_value = bool(value)
            elif isinstance(current_value, int):
                new_value = int(value)
            elif isinstance(current_value, float):
                new_value = float(value)
            else:
                new_value = value

            if current_value != new_value:
                setattr(component, attr_name, new_value)
                self.editor.update_viewport()
        except (ValueError, TypeError):
            pass # Ignore conversion errors

    def show_add_component_dialog(self, sprite):
        """Show behavior browser dialog to add components."""
        from v2_engine.editor.widgets.behavior_browser import BehaviorBrowserDialog

        dialog = BehaviorBrowserDialog(self.editor, sprite, self.theme, self.editor.project_path)
        dialog.new_behavior_created.connect(self.editor.on_new_behavior_created)

        if dialog.exec():
            selected_components = dialog.get_selected_components()
            for component_class, properties in selected_components:
                component = component_class(sprite)
                for prop, value in properties.items():
                    setattr(component, prop, value)
                sprite.add_component(component)
            self.update_for_selection()
            self.editor.update_viewport()

    def on_persistent_changed(self, sprite, is_persistent: bool):
        """Handle persistent checkbox state change."""
        sprite.is_persistent = is_persistent
        if is_persistent:
            if not sprite.entity_id:
                sprite_name = getattr(sprite, 'name', 'sprite')
                sprite.entity_id = f"{sprite_name}_{uuid.uuid4().hex[:8]}"
            game_state = get_game_state()
            current_scene_name = self.editor.game.scene_manager.current_scene if self.editor.game.scene_manager else None
            game_state.register_persistent(sprite, sprite.entity_id, home_scene=current_scene_name)
        else:
            game_state = get_game_state()
            if sprite.entity_id and sprite.entity_id in game_state.persistent_entities:
                del game_state.persistent_entities[sprite.entity_id]
            sprite.entity_id = None
        self.update_for_selection()
        self.editor.update_gamestate_panel()

    def on_entity_id_changed(self, sprite, new_id: str):
        """Handle entity ID change."""
        old_id = sprite.entity_id
        game_state = get_game_state()
        if not new_id.strip():
            sprite_name = getattr(sprite, 'name', 'sprite')
            new_id = f"{sprite_name}_{uuid.uuid4().hex[:8]}"
        sprite.entity_id = new_id
        if old_id and old_id in game_state.persistent_entities:
            del game_state.persistent_entities[old_id]
        if sprite.is_persistent:
            game_state.register_persistent(sprite, new_id)
        self.update_for_selection()
        self.editor.update_gamestate_panel()

    def open_color_picker(self, sprite):
        """Open color picker dialog and update sprite color."""
        current_color = getattr(sprite, 'color', (255, 255, 255))
        if hasattr(sprite, 'image') and sprite.image:
            try:
                center_color = sprite.image.get_at((sprite.image.get_width() // 2, sprite.image.get_height() // 2))
                current_color = (center_color.r, center_color.g, center_color.b)
            except:
                pass
        initial_color = QColor(*current_color)
        color = QColorDialog.getColor(initial_color, self, "Choose Object Color", QColorDialog.ColorDialogOption.DontUseNativeDialog)
        if color.isValid():
            new_color = (color.red(), color.green(), color.blue())
            sprite.color = new_color
            if hasattr(sprite, 'image') and sprite.image:
                sprite.image.fill(new_color)
            self.update_for_selection()
            self.editor.update_viewport()

    def show_scene_background_properties(self):
        """Show scene background properties when no sprite is selected."""
        if not self.editor.game.scene_manager or not self.editor.game.scene_manager.current_scene:
            return

        scene = self.editor.game.scene_manager.scenes[self.editor.game.scene_manager.current_scene]

        color_container = QWidget()
        color_layout = QHBoxLayout(color_container)
        color_layout.setContentsMargins(0, 0, 0, 0)

        bg_color = scene.background_color
        color_btn = QPushButton()
        color_btn.setStyleSheet(f"background-color: rgb({bg_color[0]}, {bg_color[1]}, {bg_color[2]}); min-height: 25px;")
        color_btn.setMaximumWidth(100)
        color_btn.clicked.connect(self.editor.pick_background_color)
        color_layout.addWidget(color_btn)

        color_label = QLabel(f"RGB({bg_color[0]}, {bg_color[1]}, {bg_color[2]})")
        color_layout.addWidget(color_label)
        color_layout.addStretch()
        self.properties_form.addRow("Background Color:", color_container)

        bg_image = scene.background_image or "None"
        image_label = QLabel(bg_image)
        image_label.setWordWrap(True)
        self.properties_form.addRow("Background Image:", image_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.properties_form.addRow(separator)

        grid_label = QLabel("Grid Settings")
        grid_label.setProperty("type", "header")
        self.properties_form.addRow(grid_label)

        grid_visible_checkbox = QCheckBox("Show Grid (G)")
        grid_visible_checkbox.setChecked(self.editor.state.camera.grid_visible)
        grid_visible_checkbox.stateChanged.connect(lambda state: self.editor.toggle_grid_visibility(state == Qt.CheckState.Checked.value))
        self.properties_form.addRow("", grid_visible_checkbox)

        grid_size_combo = QComboBox()
        grid_sizes = [8, 16, 24, 32, 48, 64, 128]
        for size in grid_sizes:
            grid_size_combo.addItem(f"{size}px", size)

        current_grid_size = self.editor.state.camera.grid_size
        index = grid_size_combo.findData(current_grid_size)
        if index >= 0:
            grid_size_combo.setCurrentIndex(index)

        grid_size_combo.currentIndexChanged.connect(self.editor.on_grid_size_changed)
        self.properties_form.addRow("Grid Size:", grid_size_combo)

        snap_checkbox = QCheckBox("Snap to Grid")
        snap_checkbox.setChecked(self.editor.state.camera.snap_to_grid)
        snap_checkbox.stateChanged.connect(lambda state: setattr(self.editor.state.camera, 'snap_to_grid', state == Qt.CheckState.Checked.value))
        self.properties_form.addRow("", snap_checkbox)