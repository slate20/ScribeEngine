"""
Save/Load Dialog for Scribe Engine V2 Editor.

Professional save/load system with 6 slots, metadata display, and export/import functionality.
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget,
    QPushButton, QLabel, QLineEdit, QMessageBox, QFileDialog,
    QFrame, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class SaveSlotWidget(QWidget):
    """Widget representing a single save slot."""

    def __init__(self, slot_number, metadata=None, parent=None):
        super().__init__(parent)
        self.slot_number = slot_number
        self.metadata = metadata or {}

        self.setup_ui()

    def setup_ui(self):
        """Create the slot UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Create frame for slot
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.Box)
        frame.setLineWidth(2)

        if self.metadata:
            # Occupied slot - show metadata
            frame.setStyleSheet("""
                QFrame {
                    background-color: #3a3a3a;
                    border: 2px solid #4a9eff;
                    border-radius: 6px;
                }
                QFrame:hover {
                    background-color: #4a4a4a;
                }
            """)
        else:
            # Empty slot
            frame.setStyleSheet("""
                QFrame {
                    background-color: #2a2a2a;
                    border: 2px solid #555;
                    border-radius: 6px;
                }
                QFrame:hover {
                    background-color: #3a3a3a;
                }
            """)

        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(5)

        # Slot number header
        header = QLabel(f"Slot {self.slot_number + 1}")
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(11)
        header.setFont(header_font)
        header.setStyleSheet("color: #4a9eff;")
        frame_layout.addWidget(header)

        if self.metadata:
            # Description
            desc = self.metadata.get('description', 'No description')
            desc_label = QLabel(desc if desc else "No description")
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #e0e0e0; font-size: 10pt;")
            frame_layout.addWidget(desc_label)

            # Scene name
            scene = self.metadata.get('scene_name', 'Unknown')
            scene_label = QLabel(f"Scene: {scene}")
            scene_label.setStyleSheet("color: #888; font-size: 9pt;")
            frame_layout.addWidget(scene_label)

            # Timestamp
            timestamp = self.metadata.get('timestamp', '')
            if timestamp:
                time_str = self._format_timestamp(timestamp)
                time_label = QLabel(time_str)
                time_label.setStyleSheet("color: #888; font-size: 9pt;")
                frame_layout.addWidget(time_label)

        else:
            # Empty slot message
            empty_label = QLabel("Empty Slot")
            empty_label.setStyleSheet("color: #666; font-size: 10pt; font-style: italic;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            frame_layout.addWidget(empty_label)

        frame_layout.addStretch()
        layout.addWidget(frame)

        # Store frame for click detection
        self.frame = frame
        self.frame.mousePressEvent = self.on_click

        # Make frame expand
        frame.setMinimumHeight(120)

    def on_click(self, event):
        """Handle click on slot."""
        if event.button() == Qt.MouseButton.LeftButton:
            parent = self.parent()
            while parent and not isinstance(parent, (SaveDialog, LoadDialog)):
                parent = parent.parent()
            if parent:
                parent.slot_selected(self.slot_number)

    def _format_timestamp(self, timestamp_str):
        """Format timestamp as relative time."""
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            now = datetime.now()
            delta = now - timestamp

            if delta.days > 0:
                return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
            elif delta.seconds >= 3600:
                hours = delta.seconds // 3600
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif delta.seconds >= 60:
                minutes = delta.seconds // 60
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                return "Just now"
        except:
            return timestamp_str


class SaveDialog(QDialog):
    """Dialog for saving game state to a slot."""

    def __init__(self, game_state, project_path, current_scene, parent=None):
        super().__init__(parent)
        self.game_state = game_state
        self.project_path = project_path
        self.current_scene = current_scene
        self.selected_slot = None

        self.setWindowTitle("Save Game")
        self.setModal(True)
        self.resize(900, 600)

        self.setup_ui()
        self.load_slot_data()

    def setup_ui(self):
        """Create the dialog UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Select Save Slot")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #4a9eff; margin-bottom: 10px;")
        layout.addWidget(title)

        # Slot grid (2 columns x 3 rows = 6 slots)
        grid = QGridLayout()
        grid.setSpacing(15)

        self.slot_widgets = []
        for i in range(6):
            slot_widget = SaveSlotWidget(i)
            self.slot_widgets.append(slot_widget)
            row = i // 2
            col = i % 2
            grid.addWidget(slot_widget, row, col)

        layout.addLayout(grid)

        # Description input (shown when slot selected)
        self.description_group = QGroupBox("Save Description")
        self.description_group.setVisible(False)
        desc_layout = QVBoxLayout()

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Enter a description for this save...")
        self.description_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 11pt;
                background-color: #3c3c41;
                border: 1px solid #555;
                border-radius: 4px;
                color: #e0e0e0;
            }
        """)
        desc_layout.addWidget(self.description_input)

        self.description_group.setLayout(desc_layout)
        layout.addWidget(self.description_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.setDefault(True)
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.perform_save)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

    def load_slot_data(self):
        """Load metadata for all save slots."""
        for i, slot_widget in enumerate(self.slot_widgets):
            metadata = self.game_state.get_save_metadata(i, self.project_path)
            if metadata:
                # Recreate widget with metadata
                new_widget = SaveSlotWidget(i, metadata)
                # Replace in grid
                grid = slot_widget.parent().layout()
                row = i // 2
                col = i % 2
                grid.removeWidget(slot_widget)
                slot_widget.deleteLater()
                grid.addWidget(new_widget, row, col)
                self.slot_widgets[i] = new_widget

    def slot_selected(self, slot_number):
        """Handle slot selection."""
        self.selected_slot = slot_number
        self.description_group.setVisible(True)
        self.save_btn.setEnabled(True)

        # Check if overwriting
        metadata = self.game_state.get_save_metadata(slot_number, self.project_path)
        if metadata:
            # Pre-fill with existing description
            self.description_input.setText(metadata.get('description', ''))

        self.description_input.setFocus()

    def perform_save(self):
        """Save game to selected slot."""
        if self.selected_slot is None:
            return

        description = self.description_input.text()

        # Check if overwriting
        metadata = self.game_state.get_save_metadata(self.selected_slot, self.project_path)
        if metadata:
            reply = QMessageBox.question(
                self,
                "Overwrite Save?",
                f"Slot {self.selected_slot + 1} already contains a save.\nOverwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Perform save
        result = self.game_state.save_to_file(
            self.selected_slot,
            self.current_scene,
            description,
            self.project_path
        )

        if result:
            QMessageBox.information(self, "Save Successful", f"Game saved to Slot {self.selected_slot + 1}")
            self.accept()
        else:
            QMessageBox.critical(self, "Save Failed", "Failed to save game. Check console for errors.")


class LoadDialog(QDialog):
    """Dialog for loading game state from a slot."""

    def __init__(self, game_state, project_path, parent=None):
        super().__init__(parent)
        self.game_state = game_state
        self.project_path = project_path
        self.selected_slot = None

        self.setWindowTitle("Load Game")
        self.setModal(True)
        self.resize(900, 700)

        self.setup_ui()
        self.load_slot_data()

    def setup_ui(self):
        """Create the dialog UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Select Save Slot to Load")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #4a9eff; margin-bottom: 10px;")
        layout.addWidget(title)

        # Slot grid (2 columns x 3 rows = 6 slots)
        grid = QGridLayout()
        grid.setSpacing(15)

        self.slot_widgets = []
        for i in range(6):
            slot_widget = SaveSlotWidget(i)
            self.slot_widgets.append(slot_widget)
            row = i // 2
            col = i % 2
            grid.addWidget(slot_widget, row, col)

        layout.addLayout(grid)

        # Selected slot actions
        self.actions_group = QGroupBox("Actions")
        self.actions_group.setVisible(False)
        actions_layout = QHBoxLayout()

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_save)
        actions_layout.addWidget(self.delete_btn)

        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self.export_save)
        actions_layout.addWidget(self.export_btn)

        actions_layout.addStretch()

        self.actions_group.setLayout(actions_layout)
        layout.addWidget(self.actions_group)

        # Main buttons
        button_layout = QHBoxLayout()

        import_btn = QPushButton("Import Save...")
        import_btn.clicked.connect(self.import_save)
        button_layout.addWidget(import_btn)

        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        self.load_btn = QPushButton("Load")
        self.load_btn.setDefault(True)
        self.load_btn.setEnabled(False)
        self.load_btn.clicked.connect(self.perform_load)
        button_layout.addWidget(self.load_btn)

        layout.addLayout(button_layout)

    def load_slot_data(self):
        """Load metadata for all save slots."""
        for i, slot_widget in enumerate(self.slot_widgets):
            metadata = self.game_state.get_save_metadata(i, self.project_path)
            if metadata:
                # Recreate widget with metadata
                new_widget = SaveSlotWidget(i, metadata)
                # Replace in grid
                grid = slot_widget.parent().layout()
                row = i // 2
                col = i % 2
                grid.removeWidget(slot_widget)
                slot_widget.deleteLater()
                grid.addWidget(new_widget, row, col)
                self.slot_widgets[i] = new_widget

    def slot_selected(self, slot_number):
        """Handle slot selection."""
        # Check if slot has data
        metadata = self.game_state.get_save_metadata(slot_number, self.project_path)
        if not metadata:
            QMessageBox.information(self, "Empty Slot", "This save slot is empty.")
            return

        self.selected_slot = slot_number
        self.actions_group.setVisible(True)
        self.load_btn.setEnabled(True)

    def perform_load(self):
        """Load game from selected slot."""
        if self.selected_slot is None:
            return

        # Confirm load
        reply = QMessageBox.question(
            self,
            "Load Save?",
            f"Load game from Slot {self.selected_slot + 1}?\nCurrent progress will be lost if not saved.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # Perform load
        success = self.game_state.load_from_file(self.selected_slot, self.project_path)

        if success:
            QMessageBox.information(self, "Load Successful", f"Game loaded from Slot {self.selected_slot + 1}")
            self.accept()
        else:
            QMessageBox.critical(self, "Load Failed", "Failed to load game. Check console for errors.")

    def delete_save(self):
        """Delete the selected save."""
        if self.selected_slot is None:
            return

        reply = QMessageBox.question(
            self,
            "Delete Save?",
            f"Permanently delete save in Slot {self.selected_slot + 1}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        success = self.game_state.delete_save(self.selected_slot, self.project_path)

        if success:
            QMessageBox.information(self, "Delete Successful", f"Save deleted from Slot {self.selected_slot + 1}")
            # Refresh UI
            self.load_slot_data()
            self.selected_slot = None
            self.actions_group.setVisible(False)
            self.load_btn.setEnabled(False)
        else:
            QMessageBox.critical(self, "Delete Failed", "Failed to delete save.")

    def export_save(self):
        """Export the selected save to a file."""
        if self.selected_slot is None:
            return

        # Get save filename
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Save File",
            f"save_slot_{self.selected_slot + 1}.json",
            "JSON Files (*.json)"
        )

        if not file_path:
            return

        success = self.game_state.export_save(self.selected_slot, file_path, self.project_path)

        if success:
            QMessageBox.information(self, "Export Successful", f"Save exported to:\n{file_path}")
        else:
            QMessageBox.critical(self, "Export Failed", "Failed to export save.")

    def import_save(self):
        """Import a save file to a slot."""
        # Get import file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Save File",
            "",
            "JSON Files (*.json)"
        )

        if not file_path:
            return

        # Ask which slot to import to
        from PyQt6.QtWidgets import QInputDialog
        slot, ok = QInputDialog.getInt(
            self,
            "Select Slot",
            "Import to which slot? (1-6):",
            1, 1, 6, 1
        )

        if not ok:
            return

        slot_index = slot - 1

        # Check if overwriting
        metadata = self.game_state.get_save_metadata(slot_index, self.project_path)
        if metadata:
            reply = QMessageBox.question(
                self,
                "Overwrite Save?",
                f"Slot {slot} already contains a save.\nOverwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        success = self.game_state.import_save(file_path, slot_index, self.project_path)

        if success:
            QMessageBox.information(self, "Import Successful", f"Save imported to Slot {slot}")
            # Refresh UI
            self.load_slot_data()
        else:
            QMessageBox.critical(self, "Import Failed", "Failed to import save. Check that it's a valid save file.")
