import os
import json
import re
from datetime import datetime
from jinja2 import Template, Environment
from markupsafe import Markup
from html import escape
from .parser import GameParser
from .executor import SafeExecutor
from .state import StateManager
from .storage import JSONStorage

class GameEngine:
    def __init__(self, project_path, debug_mode=False):
        self.project_path = project_path
        self.debug_mode = debug_mode
        self.config = {}
        self.passages = {}
        self.systems = {}

        self.parser = GameParser()
        self.storage = JSONStorage(save_dir=os.path.join(self.project_path, 'saves'))
        
        self.load_project()

    def load_project(self):
        """Load and parse a game project."""
        config_path = os.path.join(self.project_path, 'project.json')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Project config not found: {config_path}")
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        # Store theme config for later use
        self.theme_config = self.config.get('theme', {})

        features = self.config.get('features', {})
        self.state_manager = StateManager(features, starting_passage=self.config.get('starting_passage', 'start'))
        self.game_state = self.state_manager.get_initial_state()
        
        python_files = []
        passage_files = []
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
                elif file.endswith('.tgame'):
                    passage_files.append(os.path.join(root, file))
        
        self.executor = SafeExecutor(self.game_state, features, self.debug_mode)
        self.executor.load_systems(python_files)

        for passage_file in sorted(passage_files):
            passages_from_file = self.parser.parse_file(passage_file)
            self.passages.update(passages_from_file)

        # After loading systems, check for custom player class
        systems = self.executor.get_systems()
        if not features.get('use_default_player', True) and 'Player' in systems:
            PlayerClass = systems['Player']
            if isinstance(PlayerClass, type):
                player_instance = PlayerClass()
                # Convert instance to a dictionary, excluding methods
                player_dict = {k: v for k, v in vars(player_instance).items() if not k.startswith('__') and not callable(v)}
                if 'player' not in self.game_state:
                    self.game_state['player'] = {}
                self.game_state['player'].update(player_dict)

        if self.debug_mode:
            print(f"Loaded project '{self.config.get('title', 'Untitled')}'")
            print(f"  - {len(self.passages)} passages from {len(passage_files)} file(s)")
            print(f"  - Systems from {len(python_files)} file(s)")

    def _process_passage_content(self, passage_name, executor, use_raw_content=False):
        """Helper to execute Python blocks and render Jinja for a passage."""
        if passage_name not in self.passages:
            return f"<div class='debug-error'>Passage '{passage_name}' not found.</div>" if self.debug_mode else ""

        passage = self.passages[passage_name]

        content_to_process = passage['raw_content'] if use_raw_content else passage['content']
        processed_content = self.execute_python_blocks(passage, executor, content_to_process=content_to_process)
        
        env = Environment(extensions=['jinja2.ext.do'])
        template = env.from_string(processed_content)
        rendered_content = template.render(**self.get_template_context())
        
        return rendered_content

    def render_passage_content(self, passage_name, executor):
        """Renders a single passage, executing its Python and Jinja logic, and generating HTML with choices."""
        rendered_content = self._process_passage_content(passage_name, executor)
        passage = self.passages[passage_name]
        links = passage['links'] if passage_name not in ['PrePassage', 'PostPassage'] else []
        return self.generate_passage_html(passage_name, rendered_content, links)

    def render_special_passage(self, passage_name, executor=None):
        """Renders a single special-purpose passage (e.g., NavMenu, PrePassage, PostPassage)."""
        # If no executor is passed, create a temporary one.
        # This maintains compatibility for calls outside the main render loop (e.g., NavMenu).
        if executor is None:
            executor = SafeExecutor(self.game_state, self.config.get('features', {}), self.debug_mode)
            executor.load_systems_from_cache(self.executor.get_systems())

        if passage_name == 'NavMenu':
            rendered_content = self._process_passage_content(passage_name, executor, use_raw_content=True)
            
            # Replace links in-place for NavMenu
            def replace_link(match):
                text = match.group(1).strip()
                target = match.group(2).strip()
                # Always use <a> tag for uniformity
                if target.startswith('http://') or target.startswith('https://'):
                    return f'<a href="{target}" class="nav-link">{text}</a>'
                else:
                    return f'<a hx-get="/passage/{target}" hx-target="#game-content" class="nav-link">{text}</a>'

            final_content = self.parser.link_pattern.sub(replace_link, rendered_content)
            return f'<div class="passage" data-passage="{passage_name}"><div class="content">{final_content}</div></div>'
        else:
            return self.render_passage_content(passage_name, executor)

    def render_main_passage(self, passage_name, _recursion_depth=0):
        """Render a main passage, handling silent passages and including Pre/Post passages."""

        # --- Last Passage Tracking ---
        previous_passage_name = self.game_state.get('current_passage')
        if previous_passage_name:
            previous_passage_tags = self.passages.get(previous_passage_name, {}).get('tags', [])
            if 'menu' not in previous_passage_tags:
                self.game_state['last_passage'] = previous_passage_name

        if _recursion_depth > 10: # Max recursion depth for silent passages
            raise RecursionError("Exceeded max silent passage recursion depth. Check for loops.")

        if passage_name not in self.passages:
            raise ValueError(f"Passage '{passage_name}' not found")

        passage = self.passages[passage_name]
        tags = passage.get('tags', [])

        # Create a single executor for this entire rendering sequence
        executor = SafeExecutor(self.game_state, self.config.get('features', {}), self.debug_mode)
        executor.load_systems_from_cache(self.executor.get_systems())

        # Handle silent passages
        if 'silent' in tags:
            self._process_passage_content(passage_name, executor, use_raw_content=True)

            # After executing, find the next passage to redirect to
            links = self.passages[passage_name].get('links', [])
            if not links:
                raise ValueError(f"Silent passage '{passage_name}' has no links to redirect to.")

            # Render the target of the first link to handle dynamic targets like {{...}}
            template_context = self.get_template_context()
            env = Environment()
            first_link_target = links[0][1] # Target is the second item in the tuple
            target_template = env.from_string(first_link_target)
            next_passage_name = target_template.render(**template_context)

            # Recursively call render_main_passage for the next passage
            return self.render_main_passage(next_passage_name, _recursion_depth + 1)

        # --- Regular Passage Rendering ---
        self.game_state['current_passage'] = passage_name
        self.game_state['passage_tags'] = tags

        html_parts = []

        # Generate the OOB swap div ONCE, based on the MAIN passage's tags
        tag_classes = ' '.join(tags)
        html_parts.append(f'<div id="passage-tags-container" class="{tag_classes}" hx-swap-oob="outerHTML"></div>')

        if 'PrePassage' in self.passages:
            html_parts.append(self.render_special_passage('PrePassage', executor))

        html_parts.append(self.render_passage_content(passage_name, executor))

        if 'PostPassage' in self.passages:
            html_parts.append(self.render_special_passage('PostPassage', executor))

        return "".join(html_parts)

    def execute_python_blocks(self, passage, executor, content_to_process=None):
        content = content_to_process if content_to_process is not None else passage['content']
        
        def get_placeholder(i):
            return f"__PYTHON_BLOCK_{i}__"

        for i, python_code in enumerate(passage['python_blocks']):
            content = content.replace(f"{{{{ PYTHON_BLOCK_{i} }}}}", get_placeholder(i), 1)

        for i, python_code in enumerate(passage['python_blocks']):
            placeholder = get_placeholder(i)
            try:
                error = executor.execute_code(python_code)
                replacement = f'<div class="debug-error">{error}</div>' if error and self.debug_mode else ''
                content = content.replace(placeholder, replacement, 1)
            except Exception as e:
                replacement = f'<div class="debug-error">Python Error: {str(e)}</div>' if self.debug_mode else ''
                content = content.replace(placeholder, replacement, 1)
        
        return content
    
    def get_template_context(self):
        context = self.game_state.copy()
        context.update(self.executor.get_systems())

        # Create a player object for the template context
        if 'player' in self.game_state:
            player_data = self.game_state['player'].copy() # Create a copy to avoid modifying the original
            features = self.config.get('features', {})
            systems = self.executor.get_systems()

            if not features.get('use_default_player', True) and 'Player' in systems and isinstance(systems['Player'], type):
                # Remove any keys that are not valid arguments for the Player constructor
                player_data.pop('class_name', None)
                context['player'] = systems['Player'](**player_data)
            else:
                from types import SimpleNamespace
                context['player'] = SimpleNamespace(**player_data)

        context.update({
            'get_flag': lambda name, default=False: self.state_manager.get_flag(self.game_state, name, default),
            'set_flag': lambda name, value=True: self.state_manager.set_flag(self.game_state, name, value),
            'has_item': lambda item: self.state_manager.has_item(self.game_state, item),
            'get_item_count': lambda item: self.state_manager.get_item_count(self.game_state, item),
            'get_variable': self.get_variable, # Expose new get_variable
            'set_variable': self.set_variable, # Expose new set_variable
            'input_field': self.generate_input_html, # Expose input_field macro
            'now': datetime.now, # Add datetime.now to context
        })
        return context
    
    def generate_passage_html(self, passage_name, content, links):
        html_parts = []
        
        html_parts.append(f'<div class="passage" data-passage="{passage_name}">')
        html_parts.append('<div class="content">')
        html_parts.append(content)
        html_parts.append('</div>')
        
        if links:
            html_parts.append('<div class="choices">')
            for text, target, action in links:
                if action:
                    escaped_action = escape(action)
                    html_parts.append(f'''
                        <form hx-post="/action_link" hx-target="#game-content" class="action-link-form">
                            <input type="hidden" name="action" value="{escaped_action}">
                            <input type="hidden" name="target_passage" value="{target}">
                            <button type="submit" class="choice-btn" data-target="{target}">
                                {text if text else "Continue"}
                            </button>
                        </form>
                    ''')
                else:
                    display_text = text if text else "Continue"
                    html_parts.append(f'''
                        <button hx-get="/passage/{target}" 
                                hx-target="#game-content" 
                                class="choice-btn"
                                data-target="{target}">
                            {display_text}
                        </button>
                    ''')
            html_parts.append('</div>')
        
        html_parts.append('</div>')
        
        return ''.join(html_parts)    
    def generate_input_html(self, variable_name: str, input_type: str = 'text', placeholder: str = '', button_text: str = 'Submit', next_passage: str = None, **kwargs) -> str:
        """
        Generates HTML for an input field and a submit button, using HTMX to update game state.
        Args:
            variable_name: The name of the game state variable to update (supports dot notation).
            input_type: The type of input field (e.g., 'text', 'number', 'password').
            placeholder: Placeholder text for the input field.
            button_text: Text for the submit button.
            next_passage: Optional. The name of the passage to advance to after input is submitted.
            **kwargs: Additional HTML attributes for the input field (e.g., 'class', 'id').
        Returns:
            HTML string for the input form.
        """
        input_attrs = ' '.join([f'{k}="{v}"' for k, v in kwargs.items()])
        
        hidden_inputs = f'<input type="hidden" name="variable_name" value="{variable_name}">'
        if next_passage:
            hidden_inputs += f'<input type="hidden" name="next_passage" value="{next_passage}">'

        html = f"""
        <form hx-post="/submit_input" hx-target="#game-content" hx-swap="innerHTML">
            <input type="{input_type}" name="input_value" placeholder="{placeholder}" {input_attrs}>
            {hidden_inputs}
            <button type="submit">{button_text}</button>
        </form>
        """
        return Markup(html)
    
    def save_game(self, slot):
        self.storage.save_game(slot, self.game_state)
    
    def load_game(self, slot):
        saved_state = self.storage.load_game(slot)
        if saved_state:
            self.game_state = saved_state['game_state']
            return True
        return False
    
    def list_saves(self):
        return self.storage.list_saves()
    
    def get_title(self):
        return self.config.get('title', 'Text Adventure')

    def get_variable(self, key: str, default=None):
        """
        Retrieves a variable from game_state using dot notation (e.g., 'player.name').
        """
        parts = key.split('.')
        current = self.game_state
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current

    def set_variable(self, key: str, value):
        """
        Sets a variable in game_state using dot notation (e.g., 'player.name').
        Creates nested dictionaries if they don't exist.
        """
        parts = key.split('.')
        current = self.game_state
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                # Last part, set the value
                if isinstance(current, dict):
                    current[part] = value
                else:
                    # Handle cases where an intermediate part is not a dict
                    raise TypeError(f"Cannot set value for '{key}': '{'.'.join(parts[:i])}' is not a dictionary.")
            else:
                # Not the last part, ensure it's a dictionary
                if isinstance(current, dict):
                    if part not in current or not isinstance(current[part], dict):
                        current[part] = {} # Create if not exists or not a dict
                    current = current[part]
                else:
                    raise TypeError(f"Cannot traverse path for '{key}': '{'.'.join(parts[:i])}' is not a dictionary.")

    def update_state_from_json(self, data: dict):
        """
        Updates game_state with key-value pairs from a dictionary.
        Handles dot notation for nested keys.
        """
        for key, value in data.items():
            self.set_variable(key, value)

    
        

    def _generate_theme_css(self) -> str:
        """Generates a CSS string with :root variables based on the project's theme config."""
        theme_config = self.config.get('theme', {})
        if not theme_config.get('enabled', False):
            return "" # Return empty string if theming is disabled

        css_vars = []
        colors = theme_config.get('colors', {})
        for key, value in colors.items():
            css_vars.append(f"  --{key}-color: {value};")

        fonts = theme_config.get('fonts', {})
        for key, value in fonts.items():
            css_vars.append(f"  --font-family-{key}: {value};")

        if not css_vars:
            return "" # No variables to generate

        return ":root {\n" + "\n".join(css_vars) + "\n}"
