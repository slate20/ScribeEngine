"""
Abstract Syntax Tree (AST) node definitions for ScribeEngine templates.

These classes represent the parsed structure of .stpl files.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PythonBlock:
    """Represents a Python code block: {$ ... $}"""
    code: str
    line_number: int = 0

    def __str__(self):
        return f"PythonBlock(lines={len(self.code.splitlines())}, start_line={self.line_number})"


@dataclass
class TemplateBlock:
    """Represents an HTML/Jinja2 template block"""
    content: str
    line_number: int = 0

    def __str__(self):
        return f"TemplateBlock(length={len(self.content)}, start_line={self.line_number})"


@dataclass
class Route:
    """
    Represents a complete route definition.

    A route consists of:
    - Path pattern (e.g., '/posts/<int:post_id>')
    - HTTP methods (GET, POST, etc.)
    - Optional decorators (@require_auth, @rate_limit, etc.)
    - Python code block to execute
    - HTML/Jinja2 template to render
    """
    path: str
    methods: List[str] = field(default_factory=lambda: ['GET'])
    decorators: List[str] = field(default_factory=list)
    python_code: Optional[str] = None
    template: Optional[str] = None
    line_number: int = 0
    source_file: Optional[str] = None

    # Extracted from path pattern
    path_parameters: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Extract path parameters from the route path."""
        import re
        # Extract parameters like <int:post_id>, <username>, etc.
        pattern = r'<(?:(?P<type>\w+):)?(?P<name>\w+)>'
        matches = re.finditer(pattern, self.path)
        self.path_parameters = [match.group('name') for match in matches]

    def __str__(self):
        methods_str = ','.join(self.methods)
        decorators_str = f" [{', '.join(self.decorators)}]" if self.decorators else ""
        return f"Route({self.path} [{methods_str}]{decorators_str})"

    def get_function_name(self):
        """
        Generate a unique function name for this route.

        Examples:
            '/' -> 'route_root'
            '/about' -> 'route_about'
            '/posts/<int:post_id>' -> 'route_posts_post_id'
        """
        import re
        # Remove leading/trailing slashes
        path = self.path.strip('/')
        if not path:
            return 'route_root'

        # Replace slashes with underscores
        path = path.replace('/', '_')

        # Remove parameter type annotations and angle brackets
        path = re.sub(r'<(?:\w+:)?(\w+)>', r'\1', path)

        # Replace any remaining special characters with underscores
        path = re.sub(r'[^a-zA-Z0-9_]', '_', path)

        return f'route_{path}'
