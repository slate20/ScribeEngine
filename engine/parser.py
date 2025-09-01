import re
from typing import Dict, List, Tuple

class GameParser:
    def __init__(self):
        self.python_block_pattern = re.compile(
            r'\{\%-?\s*python\s*\%\}(.*?)\{\%-?\s*endpython\s*\%\}',
            re.DOTALL
        )
        self.link_pattern = re.compile(r'\[\[([^-]+)->([^\]]+)\]\]')
    
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
            passage_name = match.group(1).strip()
            passage_content = match.group(2).strip()
            passages[passage_name] = self.parse_passage(passage_content)
            
        return passages
    
    def parse_passage(self, content: str) -> Dict:
        """Parse individual passage content"""
        # Extract Python code blocks
        python_blocks = []
        
        def extract_python(match):
            code = match.group(1).strip()
            python_blocks.append(code)
            return f"{{{{ PYTHON_BLOCK_{len(python_blocks)-1} }}}}"
        
        # Replace Python blocks with placeholders
        processed_content = self.python_block_pattern.sub(extract_python, content)
        
        # Extract links
        links = self.link_pattern.findall(processed_content)
        
        # Remove links from the processed content to avoid displaying them raw
        processed_content_no_links = self.link_pattern.sub('', processed_content).strip()

        return {
            'content': processed_content_no_links,
            'raw_content': processed_content,
            'python_blocks': python_blocks,
            'links': [(text.strip(), target.strip()) for text, target in links]
        }