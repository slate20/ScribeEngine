"""
Code editor widget for editing Python behavior scripts.

Uses QsciScintilla for professional code editing with syntax highlighting,
code completion, and other IDE-like features.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QColor
from PyQt6.Qsci import QsciScintilla, QsciLexerPython, QsciAPIs

from v2_engine.editor.theme import EditorTheme


class CodeEditor(QWidget):
    """
    Professional Python code editor with syntax highlighting and completion.

    Features:
    - Python syntax highlighting
    - Code completion for Component API
    - Line numbers
    - Auto-indentation
    - Save and Save & Reload buttons
    - Keyboard shortcuts (Ctrl+S, Ctrl+Shift+S)

    Signals:
        file_saved: Emitted when file is saved (path: str)
        file_saved_and_reload: Emitted when Save & Reload clicked (path: str)
    """

    file_saved = pyqtSignal(str)  # Emits file path
    file_saved_and_reload = pyqtSignal(str)  # Emits file path for hot-reload

    def __init__(self, theme: EditorTheme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.current_file = None
        self.is_modified = False

        self._setup_ui()
        self._setup_editor()
        self._setup_code_completion()

    def _setup_ui(self):
        """Create editor layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.theme.spacing_small)

        # Header with file name and buttons
        header_layout = QHBoxLayout()
        header_layout.setSpacing(self.theme.spacing_small)

        self.file_label = QLabel("No file open")
        self.file_label.setStyleSheet(f"""
            QLabel {{
                color: {self.theme.text_primary};
                font-size: {self.theme.font_size_normal}px;
                font-weight: bold;
                padding: {self.theme.padding_compact}px;
            }}
        """)
        header_layout.addWidget(self.file_label, 1)

        # Save button
        self.save_btn = QPushButton("Save")
        self.save_btn.setShortcut("Ctrl+S")
        self.save_btn.clicked.connect(self._on_save_clicked)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.background_light};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border_strong};
                border-radius: {self.theme.radius_small}px;
                padding: {self.theme.padding_compact}px 16px;
                font-size: {self.theme.font_size_normal}px;
            }}
            QPushButton:hover {{
                background-color: {self.theme.background_hover};
            }}
            QPushButton:disabled {{
                color: {self.theme.text_disabled};
                background-color: {self.theme.background_dark};
            }}
        """)
        header_layout.addWidget(self.save_btn)

        # Save & Reload button
        self.save_reload_btn = QPushButton("Save & Reload")
        self.save_reload_btn.setShortcut("Ctrl+Shift+S")
        self.save_reload_btn.clicked.connect(self._on_save_reload_clicked)
        self.save_reload_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.accent_primary};
                color: white;
                border: none;
                border-radius: {self.theme.radius_small}px;
                padding: {self.theme.padding_compact}px 16px;
                font-size: {self.theme.font_size_normal}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.theme.accent_hover};
            }}
            QPushButton:disabled {{
                background-color: {self.theme.background_light};
                color: {self.theme.text_disabled};
            }}
        """)
        header_layout.addWidget(self.save_reload_btn)

        layout.addLayout(header_layout)

        # QsciScintilla editor
        self.editor = QsciScintilla()
        layout.addWidget(self.editor, 1)

    def _setup_editor(self):
        """Configure QsciScintilla editor settings."""
        # Font
        font = QFont(self.theme.font_family_code, self.theme.font_size_normal)
        self.editor.setFont(font)

        # Line numbers
        self.editor.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.editor.setMarginWidth(0, "0000")
        self.editor.setMarginsForegroundColor(QColor(self.theme.text_secondary))
        self.editor.setMarginsBackgroundColor(QColor(self.theme.background_light))

        # Current line highlighting
        self.editor.setCaretLineVisible(True)
        self.editor.setCaretLineBackgroundColor(QColor(self.theme.background_hover))

        # Indentation
        self.editor.setIndentationsUseTabs(False)
        self.editor.setTabWidth(4)
        self.editor.setAutoIndent(True)

        # Brace matching
        self.editor.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        self.editor.setMatchedBraceBackgroundColor(QColor(self.theme.accent_primary))

        # Colors
        self.editor.setPaper(QColor(self.theme.background_mid))
        self.editor.setColor(QColor(self.theme.text_primary))

        # Python lexer for syntax highlighting
        # IMPORTANT: Lexer must have parent (self.editor) to avoid segfault
        lexer = QsciLexerPython(self.editor)
        lexer.setDefaultFont(font)
        lexer.setFont(font)

        # Customize lexer colors to match theme
        lexer.setColor(QColor(self.theme.text_primary), QsciLexerPython.Default)
        lexer.setColor(QColor("#9CDCFE"), QsciLexerPython.ClassName)  # Light blue
        lexer.setColor(QColor("#DCDCAA"), QsciLexerPython.FunctionMethodName)  # Yellow
        lexer.setColor(QColor("#CE9178"), QsciLexerPython.SingleQuotedString)  # Orange
        lexer.setColor(QColor("#CE9178"), QsciLexerPython.DoubleQuotedString)  # Orange
        lexer.setColor(QColor("#6A9955"), QsciLexerPython.Comment)  # Green
        lexer.setColor(QColor("#569CD6"), QsciLexerPython.Keyword)  # Blue
        lexer.setColor(QColor("#B5CEA8"), QsciLexerPython.Number)  # Light green

        self.editor.setLexer(lexer)

        # Store lexer reference to prevent garbage collection
        self.lexer = lexer

        # Auto-completion
        self.editor.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.editor.setAutoCompletionThreshold(2)  # Show after 2 characters
        self.editor.setAutoCompletionCaseSensitivity(False)

        # Modification tracking
        self.editor.modificationChanged.connect(self._on_modification_changed)

    def _setup_code_completion(self):
        """Set up code completion API with Component-specific methods."""
        apis = QsciAPIs(self.editor.lexer())

        # Component base class API
        component_methods = [
            "def __init__(self, sprite):",
            "def update(self, dt):",
            "def on_collision(self, other):",
            "self.sprite",
            "self.sprite.position",
            "self.sprite.position.x",
            "self.sprite.position.y",
            "self.sprite.rotation",
            "self.sprite.scale",
            "self.sprite.visible",
            "self.sprite.scene",
            "self.sprite.scene.input",
            "self.sprite.scene.input.key_held",
            "self.sprite.scene.input.key_pressed",
            "self.sprite.scene.input.key_released",
            "self.sprite.get_component",
            "self.sprite.has_component",
            "self.sprite.add_component",
            "self.sprite.remove_component",
            "from v2_engine.components.component import Component",
            "from v2_engine.utils.math import Vector2",
        ]

        for method in component_methods:
            apis.add(method)

        apis.prepare()

    def load_file(self, file_path: str):
        """
        Load a Python file into the editor.

        Args:
            file_path: Absolute path to the file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.editor.setText(content)
            self.current_file = file_path
            self.is_modified = False

            # Update UI
            import os
            filename = os.path.basename(file_path)
            self.file_label.setText(filename)
            self.save_btn.setEnabled(False)
            self.save_reload_btn.setEnabled(False)

        except Exception as e:
            print(f"[CodeEditor] Error loading file: {e}")

    def save_file(self) -> bool:
        """
        Save current file.

        Returns:
            True if saved successfully, False otherwise
        """
        if not self.current_file:
            return False

        try:
            content = self.editor.text()
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)

            self.is_modified = False
            self.save_btn.setEnabled(False)
            self.save_reload_btn.setEnabled(False)

            print(f"[CodeEditor] Saved: {self.current_file}")
            return True

        except Exception as e:
            print(f"[CodeEditor] Error saving file: {e}")
            return False

    def _on_modification_changed(self, modified: bool):
        """Handle text modification state change."""
        self.is_modified = modified
        self.save_btn.setEnabled(modified)
        self.save_reload_btn.setEnabled(modified)

        # Update file label with * indicator
        if self.current_file:
            import os
            filename = os.path.basename(self.current_file)
            if modified:
                self.file_label.setText(f"{filename} *")
            else:
                self.file_label.setText(filename)

    def _on_save_clicked(self):
        """Handle Save button click."""
        if self.save_file():
            self.file_saved.emit(self.current_file)

    def _on_save_reload_clicked(self):
        """Handle Save & Reload button click."""
        if self.save_file():
            self.file_saved_and_reload.emit(self.current_file)

    def has_unsaved_changes(self) -> bool:
        """Check if editor has unsaved changes."""
        return self.is_modified

    def clear(self):
        """Clear editor and reset state."""
        self.editor.clear()
        self.current_file = None
        self.is_modified = False
        self.file_label.setText("No file open")
        self.save_btn.setEnabled(False)
        self.save_reload_btn.setEnabled(False)

    def setPlainText(self, text: str):
        """
        Set editor text (compatibility method for QTextEdit API).

        Note: This sets text without associating a file path,
        so save functionality will be disabled.

        Args:
            text: Text content to display
        """
        self.editor.setText(text)
        self.current_file = None
        self.is_modified = False
        self.file_label.setText("No file open")
        self.save_btn.setEnabled(False)
        self.save_reload_btn.setEnabled(False)

    def setText(self, text: str):
        """Alias for setPlainText (compatibility)."""
        self.setPlainText(text)

    def text(self) -> str:
        """Get current editor text."""
        return self.editor.text()

    def toPlainText(self) -> str:
        """Get current editor text (compatibility method for QTextEdit API)."""
        return self.editor.text()
