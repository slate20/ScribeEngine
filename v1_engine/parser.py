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

        # Pattern for [[links]] with optional inline flag
        self.link_pattern = re.compile(r'\[\[(.*?)\s*->\s*(.*?)(?:\s*\|\|\s*(.*?))?(?:\s*\|\s*(inline))?\]\]', re.DOTALL)

        # Pattern for <<action buttons>>
        self.action_button_pattern = re.compile(r'<<(.*?)(?:\s*->\s*(.*?))?(?:\s*\|\|\s*(.*?))??>>', re.DOTALL)
    
    def parse_file(self, filename: str) -> Dict:
        """Parse a .tgame file into passage data"""
        # Try different encodings to handle Windows compatibility
        encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'iso-8859-1']
        content = None
        
        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            # Fallback: read as binary and decode with error handling
            with open(filename, 'rb') as f:
                raw_content = f.read()
            content = raw_content.decode('utf-8', errors='replace')
        
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

        # Step 1: Find all links and action buttons, temporarily replace with placeholders.
        links_found = []
        def link_replacer(match):
            links_found.append(match.group(0)) # Store the full link, e.g., "[[Go->somewhere||{$...$}]]"
            return f"__LINK_PLACEHOLDER_{len(links_found)-1}__"

        action_buttons_found = []
        def action_button_replacer(match):
            action_buttons_found.append(match.group(0)) # Store the full action button
            return f"__ACTION_BUTTON_PLACEHOLDER_{len(action_buttons_found)-1}__"

        # Replace both links and action buttons
        content_with_links_hidden = self.link_pattern.sub(link_replacer, content)
        content_with_elements_hidden = self.action_button_pattern.sub(action_button_replacer, content_with_links_hidden)

        # Step 2: Extract all Python blocks from the content where links are hidden.
        python_blocks = []
        def extract_python(match):
            code = match.group(1).strip()
            if code:
                python_blocks.append(code)
                return f"__PYTHON_BLOCK_{len(python_blocks)-1}__"
            return ""

        content_with_python_placeholders = self.legacy_python_block_pattern.sub(extract_python, content_with_elements_hidden)
        content_with_python_placeholders = self.python_block_pattern.sub(extract_python, content_with_python_placeholders)
        content_with_python_placeholders = self.python_inline_pattern.sub(extract_python, content_with_python_placeholders)

        # Step 3: Parse links (keep existing logic for backward compatibility)
        parsed_links = []
        inline_links = []
        regular_link_indices = []
        inline_link_indices = []

        for i, link_text in enumerate(links_found):
            match = self.link_pattern.match(link_text)
            if match:
                text, target, action, inline_flag = match.groups()
                action = (action or "").strip()

                # Process action
                if action.startswith('{$') and action.endswith('$}'):
                    action = action[2:-2].strip()
                elif action.startswith('{%') and action.endswith('%}'):
                    action = ""

                link_data = (text.strip(), target.strip(), action)

                if inline_flag:
                    inline_links.append(link_data)
                    inline_link_indices.append(i)
                else:
                    parsed_links.append(link_data)
                    regular_link_indices.append(i)

        # Step 4: Parse action buttons (new processing)
        action_buttons = []
        for action_button_text in action_buttons_found:
            match = self.action_button_pattern.match(action_button_text)
            if match:
                text, target, action = match.groups()
                text = (text or "").strip()
                target = (target or "").strip()
                action = (action or "").strip()

                # Process action code
                if action.startswith('{$') and action.endswith('$}'):
                    action = action[2:-2].strip()
                elif action.startswith('{%-') and action.endswith('-%}'):
                    action = action[3:-3].strip()

                action_buttons.append((text, target, action))

        # Step 4: Restore links selectively
        final_content_for_jinja = content_with_python_placeholders

        # Replace inline links with Jinja2 function calls that will capture context
        for i in inline_link_indices:
            link_data = inline_links[inline_link_indices.index(i)]
            text, target, action = link_data

            # Convert inline link to a Jinja2 function call that captures specific context variables
            # Look for variable names in the action code to determine what to capture
            import re
            var_names = set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', action))

            # Create context capture for variables that look like template variables
            context_args = []
            for var_name in var_names:
                if var_name not in ['temp_item', 'result', 'self', 'True', 'False', 'None']:
                    context_args.append(f"{var_name}={var_name}")

            context_str = ', '.join(context_args) if context_args else ''
            function_call = f"{{{{ inline_link('{text}', '{target}', '{action}'{', ' + context_str if context_str else ''}) }}}}"
            final_content_for_jinja = final_content_for_jinja.replace(f"__LINK_PLACEHOLDER_{i}__", function_call)

        # Put back regular links (they'll be extracted later)
        for i in regular_link_indices:
            link_text = links_found[i]
            final_content_for_jinja = final_content_for_jinja.replace(f"__LINK_PLACEHOLDER_{i}__", link_text)

        # Convert action buttons to template function calls
        for i, action_button_text in enumerate(action_buttons_found):
            if i < len(action_buttons):
                text, target, action = action_buttons[i]

                # Auto-detect variables in action code for context capture
                import re
                var_names = set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', action))

                # Create context capture arguments
                context_args = []
                for var_name in var_names:
                    if var_name not in ['temp_item', 'result', 'self', 'True', 'False', 'None']:
                        context_args.append(f"{var_name}={var_name}")

                context_str = ', '.join(context_args) if context_args else ''
                function_call = f"{{{{ action_button_tag('{text}', '{target}', '{action}'{', ' + context_str if context_str else ''}) }}}}"
                final_content_for_jinja = final_content_for_jinja.replace(f"__ACTION_BUTTON_PLACEHOLDER_{i}__", function_call)

        # Step 5: Create the final display content
        # For display content, we need to remove regular links but keep inline links
        content_for_display = final_content_for_jinja

        # Remove only regular links from display content
        for i in regular_link_indices:
            link_text = links_found[i]
            content_for_display = content_for_display.replace(link_text, '', 1)

        content_for_display = content_for_display.strip()

        return {
            'content': content_for_display,
            'raw_content': final_content_for_jinja, # Has python placeholders and full links for Jinja
            'python_blocks': python_blocks,
            'links': parsed_links, # Regular links (extracted to bottom)
            'inline_links': inline_links, # Inline links (rendered in-place)
            'action_buttons': action_buttons, # Action buttons (rendered in-place with context)
            'tags': tags
        }
