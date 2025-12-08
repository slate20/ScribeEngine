"""
Lexer for ScribeEngine template files (.stpl).

The lexer tokenizes .stpl files into meaningful tokens:
- Route decorators: @route('/path')
- Other decorators: @require_auth, @custom_decorator
- Python blocks: {$ ... $}
- HTML/Template content: everything else
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    """Types of tokens in a .stpl file."""
    ROUTE_DECORATOR = auto()      # @route('/path', methods=['GET'])
    DECORATOR = auto()             # @require_auth, @rate_limit(...)
    PYTHON_BLOCK_START = auto()    # {$
    PYTHON_BLOCK_END = auto()      # $}
    PYTHON_CODE = auto()           # Code inside {$ ... $}
    TEMPLATE_CONTENT = auto()      # HTML/Jinja2 template
    EOF = auto()                   # End of file


@dataclass
class Token:
    """A single token from the lexer."""
    type: TokenType
    value: str
    line_number: int = 1
    column: int = 1

    def __str__(self):
        value_preview = self.value[:30] + '...' if len(self.value) > 30 else self.value
        return f"Token({self.type.name}, '{value_preview}', line={self.line_number})"


class TemplateLexer:
    """
    Tokenizer for .stpl template files.

    Usage:
        lexer = TemplateLexer(content)
        tokens = lexer.tokenize()
    """

    def __init__(self, content: str, filename: Optional[str] = None):
        self.content = content
        self.filename = filename
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def tokenize(self) -> List[Token]:
        """
        Tokenize the entire template content.

        Returns:
            List of tokens representing the template structure.
        """
        while self.position < len(self.content):
            # Check for decorators (must be at start of line, possibly after whitespace)
            if self._check_decorator():
                continue

            # Check for Python block start
            if self._check_python_block_start():
                continue

            # Otherwise, collect template content until we hit a decorator or Python block
            self._collect_template_content()

        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens

    def _check_decorator(self) -> bool:
        """Check if current position is at a decorator."""
        # Save position in case this isn't actually a decorator
        saved_pos = self.position
        saved_line = self.line
        saved_col = self.column

        # Skip any leading whitespace on the line
        start_of_line_pos = self.position
        while self.position < len(self.content) and self.content[self.position] in ' \t':
            self.position += 1
            self.column += 1

        # Check if we're at @ symbol
        if self.position >= len(self.content) or self.content[self.position] != '@':
            # Not a decorator, restore position
            self.position = saved_pos
            self.line = saved_line
            self.column = saved_col
            return False

        # Extract the decorator line
        line_start = self.position
        line_end = self.position

        # Find the end of the decorator (newline or EOF)
        # Handle decorators with parentheses that might span multiple lines
        paren_count = 0
        in_string = False
        string_char = None

        while line_end < len(self.content):
            char = self.content[line_end]

            # Track string literals
            if char in ('"', "'") and (line_end == 0 or self.content[line_end - 1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False

            # Track parentheses (only when not in string)
            if not in_string:
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                elif char == '\n' and paren_count == 0:
                    break

            line_end += 1

        decorator_text = self.content[line_start:line_end].strip()

        # Determine decorator type
        if decorator_text.startswith('@route'):
            token_type = TokenType.ROUTE_DECORATOR
        else:
            token_type = TokenType.DECORATOR

        self.tokens.append(Token(token_type, decorator_text, self.line, self.column))

        # Advance position
        chars_consumed = line_end - self.position
        for i in range(chars_consumed):
            if self.content[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1

        # Skip the newline if present
        if self.position < len(self.content) and self.content[self.position] == '\n':
            self.position += 1
            self.line += 1
            self.column = 1

        return True

    def _check_python_block_start(self) -> bool:
        """Check if current position is at a Python block start {$"""
        if self.position + 1 < len(self.content) and \
           self.content[self.position:self.position + 2] == '{$':

            # Mark the start
            self.tokens.append(Token(TokenType.PYTHON_BLOCK_START, '{$', self.line, self.column))

            self.position += 2
            self.column += 2

            # Now extract all Python code until we find $}
            code_start = self.position
            code_start_line = self.line
            code_start_col = self.column

            # Find the matching $}
            while self.position < len(self.content):
                if self.position + 1 < len(self.content) and \
                   self.content[self.position:self.position + 2] == '$}':
                    # Found the end
                    code = self.content[code_start:self.position]

                    self.tokens.append(Token(
                        TokenType.PYTHON_CODE,
                        code,
                        code_start_line,
                        code_start_col
                    ))

                    self.tokens.append(Token(TokenType.PYTHON_BLOCK_END, '$}', self.line, self.column))

                    self.position += 2
                    self.column += 2

                    return True

                # Track line numbers within the Python block
                if self.content[self.position] == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1

                self.position += 1

            # If we get here, we didn't find a closing $}
            raise SyntaxError(
                f"Unclosed Python block starting at line {code_start_line}, column {code_start_col}"
            )

        return False

    def _collect_template_content(self):
        """Collect template (HTML/Jinja2) content until next special token."""
        content_start = self.position
        content_start_line = self.line
        content_start_col = self.column

        # Collect content until we hit a decorator or Python block
        while self.position < len(self.content):
            # Check if we're at the start of a decorator (@ at start of line)
            if self._is_at_decorator():
                break

            # Check if we're at Python block start
            if self.position + 1 < len(self.content) and \
               self.content[self.position:self.position + 2] == '{$':
                break

            # Otherwise, consume this character
            if self.content[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1

            self.position += 1

        # Add the template content token (if we collected anything)
        content = self.content[content_start:self.position]
        if content:
            self.tokens.append(Token(
                TokenType.TEMPLATE_CONTENT,
                content,
                content_start_line,
                content_start_col
            ))

    def _is_at_decorator(self) -> bool:
        """Check if we're at a decorator without consuming characters."""
        # Check if we're at the start of a line (possibly with leading whitespace)
        # and the line starts with @

        # Look backwards to see if we're at start of line
        pos = self.position

        # Skip back over any spaces/tabs
        while pos > 0 and self.content[pos - 1] in ' \t':
            pos -= 1

        # Check if we're at start of line (beginning of file or after newline)
        if pos == 0 or self.content[pos - 1] == '\n':
            # Now look forward from current position
            check_pos = self.position
            while check_pos < len(self.content) and self.content[check_pos] in ' \t':
                check_pos += 1

            if check_pos < len(self.content) and self.content[check_pos] == '@':
                return True

        return False
