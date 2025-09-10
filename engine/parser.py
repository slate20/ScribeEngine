import re
from typing import Dict, List, Tuple

class GameParser:
    def __init__(self):
        # Pattern for existing {%- python %}...{%- endpython %} blocks
        self.legacy_python_block_pattern = re.compile(
            r'{\%-?\s*python\s*\%}(.*?){\%-?\s*endpython\s*\%}',
            re.DOTALL
        )
        # Pattern for new {$- ... -$} multiline blocks
        self.python_block_pattern = re.compile(r'{\$-\s*(.*?)\s*-\$}', re.DOTALL)
        
        # Pattern for new {$ ... $} inline statements.
        # It uses a negative lookahead `(?!\\s*-)` to avoid matching the block pattern {$-
        self.python_inline_pattern = re.compile(r'{\$(?!\s*-)(.*?)\$\s*}', re.DOTALL)

        # Pattern for [[links]]
        self.link_pattern = re.compile(r'\[\[(.*?)\s*->\s*(.*?)(?:\s*\|\|\s*(.*?))?\]\]', re.DOTALL)
    
    def parse_file(self, filename: str) -> Dict:
        """Parse a .tgame file into passage data"""
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> Dict:
        """Parse game content into passages using a more robust regex."""
        passages = {}
        # This regex finds a passage header and all its content until the next header or end of file
        passage_pattern = re.compile(r'^::\s*(.+?)(?:\n|$)(.*?)(?=\n^::|\Z)', re.MULTILINE | re.DOTALL)
        
        for match in passage_pattern.finditer(content):
            header = match.group(1).strip()
            passage_content = match.group(2).strip()

            parts = header.split('#')
            passage_name = parts[0].strip()
            tags = [t.strip() for t in parts[1:] if t.strip()]
            
            passages[passage_name] = self.parse_passage(passage_content, tags)
            
        return passages

    def parse_passage(self, content: str, tags: List[str] = None) -> Dict:
        """Parse individual passage content, extracting Python code and links."""
        if tags is None:
            tags = []
        
        python_blocks = []
        
        def extract_python(match):
            # Group 1 contains the code inside the delimiters
            code = match.group(1).strip()
            if code: # Only add non-empty code blocks
                python_blocks.append(code)
                # Return a non-Jinja placeholder that the engine will find and replace after execution
                return f"__PYTHON_BLOCK_{len(python_blocks)-1}__"
            return "" # Return empty string for empty blocks

        # --- Process all Python syntax variants ---
        # The order is important to prevent mis-matching.
        
        # 1. Process legacy {%- python %} blocks
        processed_content = self.legacy_python_block_pattern.sub(extract_python, content)
        
        # 2. Process new {$- ... -$} blocks
        processed_content = self.python_block_pattern.sub(extract_python, processed_content)

        # 3. Process new {$ ... $} inline statements
        processed_content = self.python_inline_pattern.sub(extract_python, processed_content)
        
        # After all python is extracted, handle links
        raw_links = self.link_pattern.findall(processed_content)
        
        # Remove links from the final display content
        processed_content_no_links = self.link_pattern.sub('', processed_content).strip()

        return {
            'content': processed_content_no_links,
            'raw_content': processed_content, # Content with python placeholders but with links
            'python_blocks': python_blocks,
            'links': [(text.strip(), target.strip(), action.strip()) for text, target, action in raw_links],
            'tags': tags
        }
