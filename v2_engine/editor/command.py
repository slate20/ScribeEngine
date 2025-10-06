"""
Command pattern implementation for undo/redo system.

Supports all editor operations with configurable history limit.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any
from v2_engine.utils.math import Vector2
import copy


class Command(ABC):
    """
    Base class for all undoable commands.

    Each command encapsulates a single editor operation that can be
    undone and redone.
    """

    @abstractmethod
    def execute(self):
        """Execute the command."""
        pass

    @abstractmethod
    def undo(self):
        """Undo the command."""
        pass

    def redo(self):
        """Redo the command (by default, same as execute)."""
        self.execute()

    def get_description(self) -> str:
        """Get human-readable description of command."""
        return self.__class__.__name__


class MoveCommand(Command):
    """Command for moving sprite(s)."""

    def __init__(self, sprite, old_position: Vector2, new_position: Vector2):
        """
        Initialize move command.

        Args:
            sprite: Sprite to move
            old_position: Original position
            new_position: New position
        """
        self.sprite = sprite
        self.old_position = Vector2(old_position.x, old_position.y)
        self.new_position = Vector2(new_position.x, new_position.y)

    def execute(self):
        """Move sprite to new position."""
        self.sprite.position = Vector2(self.new_position.x, self.new_position.y)

    def undo(self):
        """Move sprite back to old position."""
        self.sprite.position = Vector2(self.old_position.x, self.old_position.y)

    def get_description(self) -> str:
        return f"Move {getattr(self.sprite, 'name', 'Sprite')}"


class RotateCommand(Command):
    """Command for rotating sprite(s)."""

    def __init__(self, sprite, old_rotation: float, new_rotation: float):
        """
        Initialize rotate command.

        Args:
            sprite: Sprite to rotate
            old_rotation: Original rotation in degrees
            new_rotation: New rotation in degrees
        """
        self.sprite = sprite
        self.old_rotation = old_rotation
        self.new_rotation = new_rotation

    def execute(self):
        """Rotate sprite to new angle."""
        self.sprite.rotation = self.new_rotation

    def undo(self):
        """Rotate sprite back to old angle."""
        self.sprite.rotation = self.old_rotation

    def get_description(self) -> str:
        return f"Rotate {getattr(self.sprite, 'name', 'Sprite')}"


class ScaleCommand(Command):
    """Command for scaling sprite(s)."""

    def __init__(self, sprite, old_scale: Vector2, new_scale: Vector2):
        """
        Initialize scale command.

        Args:
            sprite: Sprite to scale
            old_scale: Original scale
            new_scale: New scale
        """
        self.sprite = sprite
        self.old_scale = Vector2(old_scale.x, old_scale.y)
        self.new_scale = Vector2(new_scale.x, new_scale.y)

    def execute(self):
        """Scale sprite to new size."""
        self.sprite.scale = Vector2(self.new_scale.x, self.new_scale.y)

    def undo(self):
        """Scale sprite back to old size."""
        self.sprite.scale = Vector2(self.old_scale.x, self.old_scale.y)

    def get_description(self) -> str:
        return f"Scale {getattr(self.sprite, 'name', 'Sprite')}"


class SetOriginCommand(Command):
    """Command for changing sprite origin point."""

    def __init__(self, sprite, old_origin: Vector2, new_origin: Vector2):
        """
        Initialize set origin command.

        Args:
            sprite: Sprite to modify
            old_origin: Original origin
            new_origin: New origin
        """
        self.sprite = sprite
        self.old_origin = Vector2(old_origin.x, old_origin.y)
        self.new_origin = Vector2(new_origin.x, new_origin.y)

    def execute(self):
        """Set sprite to new origin."""
        self.sprite.origin = Vector2(self.new_origin.x, self.new_origin.y)

    def undo(self):
        """Restore sprite to old origin."""
        self.sprite.origin = Vector2(self.old_origin.x, self.old_origin.y)

    def get_description(self) -> str:
        return f"Set Origin {getattr(self.sprite, 'name', 'Sprite')}"


class DeleteSpriteCommand(Command):
    """Command for deleting sprite(s)."""

    def __init__(self, editor, sprite, sprite_group):
        """
        Initialize delete command.

        Args:
            editor: Editor instance
            sprite: Sprite to delete
            sprite_group: SpriteGroup containing sprite
        """
        self.editor = editor
        self.sprite = sprite
        self.sprite_group = sprite_group
        # Store sprite data for restoration
        self.sprite_data = self._serialize_sprite(sprite)

    def _serialize_sprite(self, sprite):
        """Serialize sprite data for restoration."""
        return {
            'position': Vector2(sprite.position.x, sprite.position.y),
            'rotation': getattr(sprite, 'rotation', 0),
            'scale': Vector2(sprite.scale.x, sprite.scale.y) if hasattr(sprite, 'scale') else Vector2(1, 1),
            'origin': Vector2(sprite.origin.x, sprite.origin.y),
            'name': getattr(sprite, 'name', ''),
            'layer': sprite.layer,
            'image': sprite.image,
            'visible': sprite.visible,
            'components': {type(c): c for c in sprite.components.values()}
        }

    def execute(self):
        """Remove sprite from scene."""
        if self.sprite in self.sprite_group.sprites:
            self.sprite_group.sprites.remove(self.sprite)
            if self.editor.selected_sprite == self.sprite:
                self.editor.selected_sprite = None

    def undo(self):
        """Restore deleted sprite."""
        # Restore sprite to group
        if self.sprite not in self.sprite_group.sprites:
            self.sprite_group.sprites.append(self.sprite)

    def get_description(self) -> str:
        return f"Delete {self.sprite_data['name'] or 'Sprite'}"


class AddSpriteCommand(Command):
    """Command for adding new sprite."""

    def __init__(self, sprite, sprite_group):
        """
        Initialize add sprite command.

        Args:
            sprite: Sprite to add
            sprite_group: SpriteGroup to add to
        """
        self.sprite = sprite
        self.sprite_group = sprite_group

    def execute(self):
        """Add sprite to scene."""
        if self.sprite not in self.sprite_group.sprites:
            self.sprite_group.sprites.append(self.sprite)

    def undo(self):
        """Remove sprite from scene."""
        if self.sprite in self.sprite_group.sprites:
            self.sprite_group.sprites.remove(self.sprite)

    def get_description(self) -> str:
        return f"Add {getattr(self.sprite, 'name', 'Sprite')}"


class ModifyPropertyCommand(Command):
    """Generic command for modifying any sprite property."""

    def __init__(self, obj, property_name: str, old_value: Any, new_value: Any):
        """
        Initialize property modification command.

        Args:
            obj: Object to modify
            property_name: Name of property to modify
            old_value: Original value
            new_value: New value
        """
        self.obj = obj
        self.property_name = property_name
        self.old_value = copy.deepcopy(old_value) if hasattr(old_value, '__dict__') else old_value
        self.new_value = copy.deepcopy(new_value) if hasattr(new_value, '__dict__') else new_value

    def execute(self):
        """Set property to new value."""
        setattr(self.obj, self.property_name, copy.deepcopy(self.new_value) if hasattr(self.new_value, '__dict__') else self.new_value)

    def undo(self):
        """Restore property to old value."""
        setattr(self.obj, self.property_name, copy.deepcopy(self.old_value) if hasattr(self.old_value, '__dict__') else self.old_value)

    def get_description(self) -> str:
        obj_name = getattr(self.obj, 'name', self.obj.__class__.__name__)
        return f"Modify {obj_name}.{self.property_name}"


class BatchCommand(Command):
    """
    Command that executes multiple commands together as a batch.
    Used for multi-sprite operations.
    """

    def __init__(self, commands: List[Command], description: str = "Batch Operation"):
        """
        Initialize batch command.

        Args:
            commands: List of commands to execute together
            description: Description of the batch operation
        """
        self.commands = commands
        self.description = description

    def execute(self):
        """Execute all commands in the batch."""
        for command in self.commands:
            command.execute()

    def undo(self):
        """Undo all commands in reverse order."""
        for command in reversed(self.commands):
            command.undo()

    def redo(self):
        """Redo all commands."""
        for command in self.commands:
            command.redo()

    def get_description(self) -> str:
        return f"{self.description} ({len(self.commands)} sprites)"


class CommandHistory:
    """
    Manages command history for undo/redo operations.

    Maintains a stack of executed commands with configurable history limit.
    """

    def __init__(self, max_history: int = 50):
        """
        Initialize command history.

        Args:
            max_history: Maximum number of commands to keep in history
        """
        self.max_history = max_history
        self.undo_stack: List[Command] = []
        self.redo_stack: List[Command] = []

    def execute(self, command: Command):
        """
        Execute a command and add it to history.

        Args:
            command: Command to execute
        """
        command.execute()
        self.undo_stack.append(command)

        # Limit history size
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)

        # Clear redo stack when new command is executed
        self.redo_stack.clear()

    def undo(self) -> bool:
        """
        Undo the last command.

        Returns:
            True if undo was performed, False if nothing to undo
        """
        if not self.can_undo():
            return False

        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)
        return True

    def redo(self) -> bool:
        """
        Redo the last undone command.

        Returns:
            True if redo was performed, False if nothing to redo
        """
        if not self.can_redo():
            return False

        command = self.redo_stack.pop()
        command.redo()
        self.undo_stack.append(command)
        return True

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self.redo_stack) > 0

    def clear(self):
        """Clear all command history."""
        self.undo_stack.clear()
        self.redo_stack.clear()

    def get_undo_description(self) -> Optional[str]:
        """Get description of command that would be undone."""
        if self.can_undo():
            return self.undo_stack[-1].get_description()
        return None

    def get_redo_description(self) -> Optional[str]:
        """Get description of command that would be redone."""
        if self.can_redo():
            return self.redo_stack[-1].get_description()
        return None
