"""
Scene Code Extractor - Extract sprite-specific code sections from scene files.

Analyzes Python scene files and identifies code blocks related to specific sprites.
"""

import re
import ast
from typing import Optional, Tuple


class SceneCodeExtractor:
    """
    Extract and manipulate sprite-specific code sections in scene files.

    Features:
    - Find sprite creation code by sprite name
    - Extract component attachment code
    - Detect custom overrides and modifications
    - Provide line number ranges for highlighting
    """

    def __init__(self, scene_file_path: str):
        """
        Initialize extractor with scene file.

        Args:
            scene_file_path: Path to scene Python file
        """
        self.scene_file_path = scene_file_path
        self.scene_code = ""
        self.lines = []

        # Load scene file
        try:
            with open(scene_file_path, 'r') as f:
                self.scene_code = f.read()
                self.lines = self.scene_code.split('\n')
        except:
            pass

    def find_sprite_section(self, sprite_name: str) -> Optional[Tuple[int, int, str]]:
        """
        Find the code section for a specific sprite.

        Args:
            sprite_name: Name of the sprite to find

        Returns:
            Tuple of (start_line, end_line, code_section) or None if not found
            Line numbers are 0-indexed
        """
        if not self.lines:
            return None

        # Two possible patterns:
        # Pattern 1: player = SpriteObject("Player", ...)
        # Pattern 2: spriteobject_0 = SpriteObject()
        #            spriteobject_0.name = 'SpriteObject_0'

        start_line = None
        variable_name = None

        # Debug: Show what we're searching for
        print(f"[SceneExtractor] Searching for sprite: '{sprite_name}'")
        print(f"[SceneExtractor] Total lines: {len(self.lines)}")

        # Try Pattern 1: Direct name in constructor
        sprite_creation_pattern_1 = rf'^\s*(\w+)\s*=\s*SpriteObject\s*\(\s*["\']({re.escape(sprite_name)})["\']'

        # Try Pattern 2: Name assignment on separate line
        sprite_name_pattern = rf'^\s*(\w+)\.name\s*=\s*["\']({re.escape(sprite_name)})["\']'

        # First, look for name assignment (Pattern 2 - more common in serialized files)
        for i, line in enumerate(self.lines):
            match = re.search(sprite_name_pattern, line)
            if match:
                variable_name = match.group(1)
                # Find the creation line (should be a few lines above)
                for j in range(max(0, i - 10), i):
                    if f'{variable_name} = SpriteObject(' in self.lines[j]:
                        start_line = j
                        print(f"[SceneExtractor] Found sprite at line {j} (name assigned at {i}): {self.lines[j].strip()}")
                        break
                if start_line is not None:
                    break

        # If Pattern 2 didn't work, try Pattern 1
        if start_line is None:
            for i, line in enumerate(self.lines):
                match = re.search(sprite_creation_pattern_1, line)
                if match:
                    start_line = i
                    variable_name = match.group(1)
                    print(f"[SceneExtractor] Found sprite at line {i}: {line.strip()}")
                    break

        if start_line is None:
            print(f"[SceneExtractor] Sprite '{sprite_name}' not found")
            return None

        # Find end of sprite section
        # Look for:
        # 1. self.add_sprite(variable_name)
        # 2. Next sprite creation
        # 3. End of method
        end_line = start_line

        for i in range(start_line + 1, len(self.lines)):
            line = self.lines[i]

            # Check for add_sprite call
            if f'self.add_sprite({variable_name})' in line or f'self.add_sprite( {variable_name} )' in line:
                end_line = i
                break

            # Check for next sprite creation (start of new section)
            if re.search(r'^\s*\w+\s*=\s*SpriteObject\s*\(', line):
                end_line = i - 1
                break

            # Check for end of method or class
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                end_line = i - 1
                break

            # Check for significant dedent (end of block)
            if i > start_line + 1:
                current_indent = len(line) - len(line.lstrip())
                prev_line = self.lines[i - 1]
                prev_indent = len(prev_line) - len(prev_line.lstrip())

                if line.strip() and current_indent < prev_indent and current_indent <= self._get_indent_level(self.lines[start_line]):
                    end_line = i - 1
                    break

        # If we didn't find a clear end, use the last line with content
        if end_line == start_line:
            for i in range(start_line + 1, len(self.lines)):
                if self.lines[i].strip():
                    end_line = i
                else:
                    break

        # Extract the section
        code_section = '\n'.join(self.lines[start_line:end_line + 1])

        return (start_line, end_line, code_section)

    def _get_indent_level(self, line: str) -> int:
        """Get the indentation level of a line."""
        return len(line) - len(line.lstrip())

    def has_custom_overrides(self, sprite_name: str) -> bool:
        """
        Check if a sprite has custom overrides or modifications.

        Looks for:
        - Custom properties set after component creation
        - Method overrides (component.update = ...)
        - Lambda functions
        - Custom behavior modifications

        Args:
            sprite_name: Name of sprite to check

        Returns:
            True if sprite has custom code beyond standard setup
        """
        section_info = self.find_sprite_section(sprite_name)
        if not section_info:
            return False

        _, _, code_section = section_info

        # Patterns indicating custom overrides
        patterns = [
            r'\.update\s*=',  # Method override
            r'lambda\s+',  # Lambda function
            r'def\s+\w+\s*\(',  # Function definition
            r'#.*custom',  # Comments mentioning custom
            r'#.*override',  # Comments mentioning override
        ]

        for pattern in patterns:
            if re.search(pattern, code_section, re.IGNORECASE):
                return True

        # Check for properties set after component creation
        # Look for lines like: component.some_property = value
        # after add_component() calls
        lines = code_section.split('\n')
        found_add_component = False

        for line in lines:
            if 'add_component' in line:
                found_add_component = True
            elif found_add_component and re.search(r'\.\w+\s*=', line):
                # Found property assignment after component addition
                return True

        return False

    def get_full_scene_code(self) -> str:
        """Get the full scene file code."""
        return self.scene_code

    def get_line_count(self) -> int:
        """Get total number of lines in scene file."""
        return len(self.lines)
