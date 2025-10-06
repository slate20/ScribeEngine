"""
ComponentCard - Beautiful, collapsible card widget for displaying component/behavior properties.

Displays components with:
- Category color badge
- Collapsible sections
- Filtered properties (only editor-relevant)
- Professional appearance
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QFormLayout, QLineEdit, QCheckBox, QDoubleSpinBox, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from v2_engine.editor.theme import get_theme


class ComponentCard(QWidget):
    """
    Collapsible card widget for displaying a component/behavior.

    Features:
    - Category color badge (Physics, Rendering, Gameplay, etc.)
    - Collapsible to hide/show properties
    - Clean header with behavior name
    - Remove button (×)
    - Filtered properties (only editor-relevant)
    """

    # Signals
    remove_requested = pyqtSignal(object)  # Emits component type when remove clicked
    property_changed = pyqtSignal(str, object)  # Emits (property_name, new_value)
    edit_code_requested = pyqtSignal(object)  # Emits component when edit code clicked

    def __init__(self, component, sprite, parent=None):
        """
        Initialize component card.

        Args:
            component: Component instance to display
            sprite: Sprite this component is attached to
            parent: Parent widget
        """
        super().__init__(parent)
        self.component = component
        self.sprite = sprite
        self.theme = get_theme()
        self.collapsed = True  # Default to collapsed

        self.setup_ui()

    def setup_ui(self):
        """Setup the card UI."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, self.theme.spacing_small)
        layout.setSpacing(0)

        # === Card Frame ===
        self.card_frame = QFrame()
        self.card_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme.background_light};
                border: 1px solid {self.theme.border_subtle};
                border-radius: {self.theme.radius_medium}px;
            }}
        """)

        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # === Header (clickable to collapse) ===
        self.header = QWidget()
        self.header.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header.mousePressEvent = self.toggle_collapsed

        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(self.theme.spacing_medium, self.theme.spacing_medium,
                                        self.theme.spacing_medium, self.theme.spacing_medium)
        header_layout.setSpacing(self.theme.spacing_small)

        # Category badge (colored dot)
        category = self.get_component_category()
        badge_color = self.theme.get_category_color(category)

        self.badge = QLabel("●")
        self.badge.setFont(QFont("Segoe UI", 16))
        self.badge.setStyleSheet(f"color: {badge_color};")
        self.badge.setToolTip(f"Category: {category}")
        header_layout.addWidget(self.badge)

        # Component name (using friendly "Behavior" terminology)
        component_name = self.component.__class__.__name__
        self.name_label = QLabel(component_name)
        self.name_label.setFont(QFont(self.theme.font_family_ui, self.theme.font_size_normal, QFont.Weight.Bold))
        header_layout.addWidget(self.name_label)

        # Category label (small, secondary)
        self.category_label = QLabel(category)
        self.category_label.setProperty("type", "caption")
        self.category_label.setStyleSheet(f"color: {badge_color}; font-size: {self.theme.font_size_small}pt;")
        header_layout.addWidget(self.category_label)

        header_layout.addStretch()

        # Collapse indicator
        self.collapse_indicator = QLabel("▼")
        self.collapse_indicator.setFont(QFont("Segoe UI", 12))
        self.collapse_indicator.setFixedSize(20, 20)
        self.collapse_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.collapse_indicator)

        # Edit Code button (available for all behaviors)
        self.edit_code_btn = QPushButton("📝")
        self.edit_code_btn.setFixedSize(26, 26)
        self.edit_code_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.accent_primary};
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 13px;
                padding: 0px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {self.theme.accent_hover};
            }}
        """)
        self.edit_code_btn.setToolTip("Edit behavior code")
        self.edit_code_btn.clicked.connect(self.on_edit_code_clicked)
        header_layout.addWidget(self.edit_code_btn)

        # Remove button
        self.remove_btn = QPushButton("×")
        self.remove_btn.setFixedSize(26, 26)
        self.remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.error};
                color: white;
                font-weight: bold;
                font-size: 18px;
                border: none;
                border-radius: 13px;
                padding: 0px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {self.theme.warning};
            }}
        """)
        self.remove_btn.setToolTip("Remove behavior")
        self.remove_btn.clicked.connect(self.on_remove_clicked)
        header_layout.addWidget(self.remove_btn)

        card_layout.addWidget(self.header)

        # === Body (properties) ===
        self.body = QWidget()
        body_layout = QVBoxLayout(self.body)
        body_layout.setContentsMargins(self.theme.spacing_medium + 20, self.theme.spacing_small,
                                      self.theme.spacing_medium, self.theme.spacing_medium)
        body_layout.setSpacing(self.theme.spacing_small)

        # Properties form
        self.properties_form = QFormLayout()
        self.properties_form.setSpacing(self.theme.spacing_small)
        self.properties_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Add filtered properties
        self.add_properties()

        body_layout.addLayout(self.properties_form)
        card_layout.addWidget(self.body)

        layout.addWidget(self.card_frame)

        # Set initial collapsed state
        self.body.setVisible(not self.collapsed)
        self.collapse_indicator.setText("▶" if self.collapsed else "▼")

    def get_component_category(self):
        """
        Determine component category based on type.

        Returns:
            str: Category name (Physics, Rendering, Gameplay, etc.)
        """
        component_name = self.component.__class__.__name__.lower()

        # Physics category
        if any(keyword in component_name for keyword in ['rigidbody', 'collider', 'physics', 'collision']):
            return "Physics"

        # Rendering category
        if any(keyword in component_name for keyword in ['sprite', 'render', 'camera', 'animation']):
            return "Rendering"

        # Gameplay category
        if any(keyword in component_name for keyword in ['controller', 'player', 'input', 'movement']):
            return "Gameplay"

        # Interaction category
        if any(keyword in component_name for keyword in ['trigger', 'dialogue', 'interaction', 'spawn']):
            return "Interaction"

        # AI category
        if any(keyword in component_name for keyword in ['ai', 'behavior', 'patrol', 'chase']):
            return "AI"

        # Audio category
        if any(keyword in component_name for keyword in ['audio', 'sound', 'music']):
            return "Audio"

        # Default
        return "Gameplay"

    def add_properties(self):
        """Add filtered component properties to the form."""
        # Get component properties
        properties = self.get_filtered_properties()

        for prop_name, prop_value in properties.items():
            # Create appropriate editor for property type
            editor = self.create_property_editor(prop_name, prop_value)
            if editor:
                # Create label with friendly name
                label = prop_name.replace('_', ' ').title() + ":"
                self.properties_form.addRow(label, editor)

    def get_filtered_properties(self):
        """
        Get component properties filtered for editor display.

        Filters out:
        - Private properties (starting with _)
        - Internal properties (sprite, methods)
        - Non-editable properties

        Returns:
            dict: Filtered properties {name: value}
        """
        properties = {}

        for attr_name in dir(self.component):
            # Skip private/protected
            if attr_name.startswith('_'):
                continue

            # Skip methods
            if callable(getattr(self.component, attr_name)):
                continue

            # Skip common internal properties
            if attr_name in ['sprite', 'enabled', 'components']:
                continue

            # Get value
            try:
                value = getattr(self.component, attr_name)
                properties[attr_name] = value
            except:
                continue

        return properties

    def create_property_editor(self, prop_name, prop_value):
        """
        Create appropriate editor widget for property type.

        Args:
            prop_name: Property name
            prop_value: Current property value

        Returns:
            QWidget: Editor widget for this property type
        """
        # Boolean properties -> Checkbox
        if isinstance(prop_value, bool):
            checkbox = QCheckBox()
            checkbox.setChecked(prop_value)
            checkbox.stateChanged.connect(
                lambda state: self.on_property_changed(prop_name, state == Qt.CheckState.Checked.value)
            )
            return checkbox

        # Float properties -> Double spin box
        elif isinstance(prop_value, float):
            spinbox = QDoubleSpinBox()
            spinbox.setRange(-10000, 10000)
            spinbox.setDecimals(2)
            spinbox.setValue(prop_value)
            spinbox.valueChanged.connect(
                lambda value: self.on_property_changed(prop_name, value)
            )
            return spinbox

        # Int properties -> Spin box
        elif isinstance(prop_value, int):
            spinbox = QSpinBox()
            spinbox.setRange(-10000, 10000)
            spinbox.setValue(prop_value)
            spinbox.valueChanged.connect(
                lambda value: self.on_property_changed(prop_name, value)
            )
            return spinbox

        # String/other properties -> Line edit
        elif isinstance(prop_value, (str, type(None))):
            lineedit = QLineEdit(str(prop_value) if prop_value is not None else "")
            lineedit.editingFinished.connect(
                lambda: self.on_property_changed(prop_name, lineedit.text())
            )
            return lineedit

        # Complex types (lists, dicts, objects) -> Display as read-only text
        else:
            label = QLabel(str(prop_value))
            label.setProperty("type", "caption")
            label.setWordWrap(True)
            return label

    def on_property_changed(self, prop_name, new_value):
        """
        Handle property value change.

        Args:
            prop_name: Name of property that changed
            new_value: New value
        """
        # Update component
        try:
            setattr(self.component, prop_name, new_value)
            self.property_changed.emit(prop_name, new_value)
        except Exception as e:
            print(f"[ComponentCard] Error setting {prop_name}: {e}")

    def toggle_collapsed(self, event):
        """Toggle collapsed state."""
        self.collapsed = not self.collapsed
        self.body.setVisible(not self.collapsed)

        # Update collapse indicator
        self.collapse_indicator.setText("▶" if self.collapsed else "▼")

    def on_remove_clicked(self):
        """Handle remove button click."""
        self.remove_requested.emit(self.component.__class__)

    def on_edit_code_clicked(self):
        """Handle edit code button click."""
        self.edit_code_requested.emit(self.component)
