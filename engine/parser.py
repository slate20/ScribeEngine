import re
from typing import Dict, List, Tuple

class GameParser:
    def __init__(self):
        # Pattern for existing {%- python %}...{%- endpython %} blocks
        self.legacy_python_block_pattern = re.compile(
            r'{%-\s*python\s*%}(.*?){%-\s*endpython\s*%}',
            re.DOTALL
        )
        # Pattern for new {$- ... -$} multiline blocks
        self.python_block_pattern = re.compile(r'{\$-\s*(.*?)\s*-\$}', re.DOTALL)
        
        # Pattern for new {$ ... $} inline statements.
        # It uses a negative lookahead `(?!\s*-)` to avoid matching the block pattern {$-
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

        # Step 1: Find all links and temporarily replace them with placeholders.
        links_found = []
        def link_replacer(match):
            links_found.append(match.group(0)) # Store the full link, e.g., "[[Go->somewhere||{$...$}]]"
            return f"__LINK_PLACEHOLDER_{len(links_found)-1}__"
        
        content_with_links_hidden = self.link_pattern.sub(link_replacer, content)

        # Step 2: Extract all Python blocks from the content where links are hidden.
        python_blocks = []
        def extract_python(match):
            code = match.group(1).strip()
            if code:
                python_blocks.append(code)
                return f"__PYTHON_BLOCK_{len(python_blocks)-1}__"
            return ""

        content_with_python_placeholders = self.legacy_python_block_pattern.sub(extract_python, content_with_links_hidden)
        content_with_python_placeholders = self.python_block_pattern.sub(extract_python, content_with_python_placeholders)
        content_with_python_placeholders = self.python_inline_pattern.sub(extract_python, content_with_python_placeholders)

        # Step 3: Put the links back into the content that has python placeholders.
        final_content_for_jinja = content_with_python_placeholders
        for i, link_text in enumerate(links_found):
            final_content_for_jinja = final_content_for_jinja.replace(f"__LINK_PLACEHOLDER_{i}__", link_text)

        # Step 4: Parse the links from the original text to extract actions correctly.
        parsed_links = []
        for link_text in links_found:
            match = self.link_pattern.match(link_text)
            if match:
                text, target, action = match.groups()
                action = (action or "").strip() # Ensure action is a non-None string

                # If the action is a Python block, extract the raw code for the executor.
                if action.startswith('{$') and action.endswith('$}'):
                    action = action[2:-2].strip()
                # Deprecate Jinja execution by no longer processing it here.
                elif action.startswith('{%') and action.endswith('%}'):
                    action = "" # Ignore old Jinja syntax in actions.
                
                parsed_links.append((text.strip(), target.strip(), action))

        # Step 5: Create the final display content (without links).
        content_for_display = self.link_pattern.sub('', final_content_for_jinja).strip()

        return {
            'content': content_for_display,
            'raw_content': final_content_for_jinja, # Has python placeholders and full links for Jinja
            'python_blocks': python_blocks,
            'links': parsed_links,
            'tags': tags
        }
