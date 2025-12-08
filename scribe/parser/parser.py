"""
Parser for ScribeEngine template files (.stpl).

The parser takes tokens from the lexer and builds an Abstract Syntax Tree (AST)
consisting of Route objects with their associated code and templates.
"""

import re
from typing import List, Optional
from scribe.parser.lexer import TemplateLexer, Token, TokenType
from scribe.parser.ast_nodes import Route, PythonBlock, TemplateBlock


class TemplateParser:
    """
    Parser for .stpl template files.

    Usage:
        parser = TemplateParser()
        routes = parser.parse_file('app.stpl')

        # Or parse from string:
        routes = parser.parse(content, 'app.stpl')
    """

    def __init__(self):
        self.tokens: List[Token] = []
        self.position = 0
        self.current_token: Optional[Token] = None
        self.filename: Optional[str] = None

    def parse_file(self, filepath: str) -> List[Route]:
        """
        Parse a .stpl file and return list of Route objects.

        Args:
            filepath: Path to the .stpl file

        Returns:
            List of Route objects
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.parse(content, filepath)

    def parse(self, content: str, filename: Optional[str] = None) -> List[Route]:
        """
        Parse template content and return list of Route objects.

        Args:
            content: Template file content
            filename: Optional filename for error messages

        Returns:
            List of Route objects
        """
        self.filename = filename

        # Tokenize
        lexer = TemplateLexer(content, filename)
        self.tokens = lexer.tokenize()
        self.position = 0
        self.current_token = self.tokens[0] if self.tokens else None

        # Parse routes
        routes = []
        while self.current_token and self.current_token.type != TokenType.EOF:
            route = self._parse_route()
            if route:
                routes.append(route)

        return routes

    def _parse_route(self) -> Optional[Route]:
        """
        Parse a single route definition.

        Route structure:
            @route('/path', methods=['GET', 'POST'])
            @decorator1
            @decorator2
            {$
            # Python code
            $}
            <html>template</html>
        """
        # Skip any template content before the first route decorator
        while self.current_token and self.current_token.type == TokenType.TEMPLATE_CONTENT:
            self._advance()

        if not self.current_token or self.current_token.type == TokenType.EOF:
            return None

        # Must start with @route decorator
        if self.current_token.type != TokenType.ROUTE_DECORATOR:
            raise SyntaxError(
                f"Expected @route decorator, got {self.current_token.type.name} "
                f"at line {self.current_token.line_number}"
            )

        # Parse the route decorator
        route_token = self.current_token
        path, methods = self._parse_route_decorator(route_token.value)

        route = Route(
            path=path,
            methods=methods,
            line_number=route_token.line_number,
            source_file=self.filename
        )

        self._advance()

        # Parse any additional decorators
        while self.current_token and self.current_token.type == TokenType.DECORATOR:
            decorator_name = self._parse_decorator(self.current_token.value)
            route.decorators.append(decorator_name)
            self._advance()

        # Parse Python block (optional)
        if self.current_token and self.current_token.type == TokenType.PYTHON_BLOCK_START:
            self._advance()  # Skip {$

            if self.current_token and self.current_token.type == TokenType.PYTHON_CODE:
                route.python_code = self.current_token.value
                self._advance()  # Skip code

            if self.current_token and self.current_token.type == TokenType.PYTHON_BLOCK_END:
                self._advance()  # Skip $}
            else:
                raise SyntaxError(
                    f"Expected Python block end '$}}' at line {self.current_token.line_number if self.current_token else 'EOF'}"
                )

        # Parse template content (everything until next route decorator or EOF)
        template_parts = []
        while self.current_token and \
              self.current_token.type not in (TokenType.ROUTE_DECORATOR, TokenType.EOF):

            if self.current_token.type == TokenType.TEMPLATE_CONTENT:
                template_parts.append(self.current_token.value)
                self._advance()
            else:
                # Unexpected token
                raise SyntaxError(
                    f"Unexpected token {self.current_token.type.name} at line {self.current_token.line_number}"
                )

        route.template = ''.join(template_parts)

        return route

    def _parse_route_decorator(self, decorator_text: str) -> tuple[str, List[str]]:
        """
        Parse @route('/path', methods=['GET', 'POST']) into path and methods.

        Args:
            decorator_text: The decorator text (e.g., "@route('/path', methods=['GET'])")

        Returns:
            Tuple of (path, methods_list)
        """
        # Pattern to match @route('/path') or @route('/path', methods=['GET', 'POST'])
        # This handles both single and double quotes, and optional methods parameter

        # Simple approach: extract the function call arguments
        match = re.match(r'@route\s*\((.*)\)', decorator_text, re.DOTALL)
        if not match:
            raise SyntaxError(f"Invalid @route decorator syntax: {decorator_text}")

        args_str = match.group(1).strip()

        # Parse the path (first argument)
        # Handle both single and double quotes
        path_match = re.match(r'''['"](.*?)['"]''', args_str)
        if not path_match:
            raise SyntaxError(f"Could not extract path from @route decorator: {decorator_text}")

        path = path_match.group(1)

        # Parse methods if present
        methods = ['GET']  # Default
        methods_match = re.search(r'''methods\s*=\s*\[(.*?)\]''', args_str)
        if methods_match:
            methods_str = methods_match.group(1)
            # Extract method names (handle both single and double quotes)
            method_matches = re.findall(r'''['"](.*?)['"]''', methods_str)
            if method_matches:
                methods = [m.upper() for m in method_matches]

        return path, methods

    def _parse_decorator(self, decorator_text: str) -> str:
        """
        Parse a decorator and return its name.

        Examples:
            @require_auth -> 'require_auth'
            @require_role('admin') -> "require_role('admin')"
            @rate_limit(100, per='hour') -> "rate_limit(100, per='hour')"

        Args:
            decorator_text: The decorator text

        Returns:
            Decorator expression (without the @ symbol)
        """
        # Remove the @ symbol and return
        return decorator_text.lstrip('@').strip()

    def _advance(self):
        """Move to the next token."""
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None
