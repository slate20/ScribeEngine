"""
Selection Manager - Manages sprite selection state and operations.

Handles:
- Single and multi-sprite selection
- Copy/paste operations
- Selection state tracking
- Selection change notifications
"""

from PyQt6.QtCore import QObject, pyqtSignal
from v2_engine.utils.math import Vector2


class SelectionManager(QObject):
    """
    Manages sprite selection state and copy/paste operations.

    Signals:
        selection_changed: Emitted when selection changes (list of sprites, primary sprite or None)
    """

    # Signals
    selection_changed = pyqtSignal(list, object)  # [sprites], primary_sprite

    def __init__(self, editor):
        """
        Initialize the selection manager.

        Args:
            editor: Reference to EditorWindow
        """
        super().__init__()
        self.editor = editor

        # Selection state
        self.selected_sprites = []  # List of all selected sprites
        self.selected_sprite = None  # Primary selected sprite
        self.copied_sprite = None  # Sprite in clipboard

    def select(self, sprite, add_to_selection=False):
        """
        Select a sprite (or add to current selection).

        Args:
            sprite: Sprite to select
            add_to_selection: If True, add to selection; if False, clear and select only this sprite
        """
        if add_to_selection:
            # Toggle selection
            if sprite in self.selected_sprites:
                self.selected_sprites.remove(sprite)
                if self.selected_sprite == sprite:
                    self.selected_sprite = self.selected_sprites[0] if self.selected_sprites else None
            else:
                self.selected_sprites.append(sprite)
                self.selected_sprite = sprite  # Most recently selected becomes primary
        else:
            # Single selection
            self.selected_sprites = [sprite]
            self.selected_sprite = sprite

        # Update editor state
        self.editor.state.selected_sprite = self.selected_sprite

        # Emit signal
        self.selection_changed.emit(self.selected_sprites.copy(), self.selected_sprite)

        sprite_name = getattr(sprite, 'name', sprite.__class__.__name__)
        if add_to_selection and len(self.selected_sprites) > 1:
            print(f"[SelectionManager] Multi-select: {len(self.selected_sprites)} sprites (primary: {sprite_name})")
        else:
            print(f"[SelectionManager] Selected: {sprite_name}")

    def clear(self):
        """Deselect all sprites."""
        self.selected_sprites = []
        self.selected_sprite = None
        self.editor.state.selected_sprite = None

        # Emit signal
        self.selection_changed.emit([], None)

        print("[SelectionManager] Deselected all sprites")

    def get_selection(self):
        """
        Get list of currently selected sprites.

        Returns:
            List of selected sprites
        """
        return self.selected_sprites.copy() if self.selected_sprites else []

    def get_primary_selection(self):
        """
        Get the primary selected sprite.

        Returns:
            Primary sprite or None
        """
        return self.selected_sprite

    def has_selection(self):
        """Check if any sprites are selected."""
        return len(self.selected_sprites) > 0

    def is_multi_selection(self):
        """Check if multiple sprites are selected."""
        return len(self.selected_sprites) > 1

    # Copy/Paste operations

    def copy(self):
        """Copy the currently selected sprite to clipboard."""
        if not self.selected_sprite:
            print("[SelectionManager] No sprite selected to copy")
            return

        # Store a reference to the selected sprite for pasting
        self.copied_sprite = self.selected_sprite
        sprite_name = getattr(self.copied_sprite, 'name', self.copied_sprite.__class__.__name__)
        print(f"[SelectionManager] Copied sprite: {sprite_name}")

    def paste(self, scene):
        """
        Paste the copied sprite into the scene.

        Args:
            scene: Scene to paste into

        Returns:
            The newly created sprite or None
        """
        if not self.copied_sprite:
            print("[SelectionManager] No sprite copied")
            return None

        if not scene:
            print("[SelectionManager] No scene provided")
            return None

        # Create new sprite as a copy
        from v2_engine.sprites.sprite_object import SpriteObject

        # Deep copy the sprite to duplicate all attributes
        new_sprite = SpriteObject()

        # Copy basic properties
        new_sprite.position = Vector2(
            self.copied_sprite.position.x + 20,
            self.copied_sprite.position.y + 20
        )  # Offset slightly
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
            print(f"[SelectionManager] Pasted sprite: {new_sprite.name}")
            return new_sprite
        else:
            print("[SelectionManager] No 'all' sprite group found")
            return None

    def has_clipboard(self):
        """Check if there's a sprite in the clipboard."""
        return self.copied_sprite is not None
