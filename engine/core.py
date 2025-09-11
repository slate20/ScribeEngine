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

    def update_debug_mode(self, debug_mode):
        """Update the debug mode setting and reinitialize executor if needed."""
        self.debug_mode = debug_mode
        # Update the existing executor's debug mode if it exists
        if hasattr(self, 'executor') and self.executor:
            self.executor.debug_mode = debug_mode

    def load_project(self):
        """Load and parse a game project."""
        config_path = os.path.join(self.project_path, 'project.json')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Project config not found: {config_path}")
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        # Store theme config for later use
        self.theme_config = self.config.get('theme', {})
        
        # Update debug mode from project configuration
        self.debug_mode = self.config.get('debug_mode', False)

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

        # Auto-instantiate Player class if found
        systems = self.executor.get_systems()
        if 'Player' in systems and isinstance(systems['Player'], type):
            self.game_state['player'] = systems['Player']()

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
        context = self.get_template_context()
        rendered_content = template.render(**context)
        self.sync_context_to_state(context)
        
        return rendered_content

    def render_passage_content(self, passage_name, executor):
        """Renders a single passage, executing its Python and Jinja logic, and generating HTML with choices."""
        # Always process raw_content to allow Jinja2 expressions within links
        rendered_content = self._process_passage_content(passage_name, executor, use_raw_content=True)
        
        # Re-extract links from the rendered content after Jinja2 evaluation
        # This ensures that any Jinja2 expressions that generate or modify links are processed.
        extracted_links = self.parser.link_pattern.findall(rendered_content)
        
        # Remove links from the final content before passing to HTML generation
        content_without_links = self.parser.link_pattern.sub('', rendered_content).strip()

        passage = self.passages[passage_name]
        
        # Only include links if it's not a special passage like PrePassage or PostPassage
        links_to_use = extracted_links if passage_name not in ['PrePassage', 'PostPassage'] else []

        return self.generate_passage_html(passage_name, content_without_links, links_to_use)

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
            # First, process the passage content to resolve Jinja2 conditionals.
            # We use 'raw_content' because the parser removes links from 'content',
            # but we need the links to be present for Jinja2 to evaluate them.
            rendered_silent_content = self._process_passage_content(passage_name, executor, use_raw_content=True)

            # Now, find the link in the *rendered* content.
            # This will only find the link that passed the Jinja2 condition.
            found_links = self.parser.link_pattern.findall(rendered_silent_content)

            if not found_links:
                raise ValueError(f"Silent passage '{passage_name}' rendered no links to redirect to. Check your Jinja2 conditions.")
            if len(found_links) > 1:
                # This indicates an issue with the passage logic, as only one link
                # should typically remain after Jinja2 evaluation in a silent passage.
                # We'll proceed with the first one, but it's a warning sign.
                print(f"WARNING: Silent passage '{passage_name}' rendered multiple links. Redirecting to the first one found.")

            # The target is the second item in the tuple (text, target, action)
            next_passage_name = found_links[0][1]

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
        """
        Executes Python code found by the parser and replaces the placeholders.
        """
        content = content_to_process if content_to_process is not None else passage['content']
        
        for i, python_code in enumerate(passage['python_blocks']):
            placeholder = f"__PYTHON_BLOCK_{i}__"
            try:
                # Execute the code. The executor has direct access to game_state.
                error = executor.execute_code(python_code)
                
                # If in debug mode and an error occurred, display it. Otherwise, replace with nothing.
                replacement = f'<div class="debug-error">{error}</div>' if error and self.debug_mode else ''
                content = content.replace(placeholder, replacement, 1)
            except Exception as e:
                # Catch exceptions during execution and display them in debug mode.
                replacement = f'<div class="debug-error">Python Error: {str(e)}</div>' if self.debug_mode else ''
                content = content.replace(placeholder, replacement, 1)
        
        return content
    
    def get_template_context(self):
        # Create context that directly references game_state variables
        context = {}
        context.update(self.game_state)  # This creates references to mutable objects
        context.update(self.executor.get_systems())
        context.update({
            'input_field': self.generate_input_html, # Expose input_field macro
            'now': datetime.now, # Add datetime.now to context
        })
        return context

    def sync_context_to_state(self, context: dict):
        """Synchronizes any changes from template context back to the game state."""
        # Sync back any variables that could have been modified during template rendering
        # Skip systems functions and helper functions
        skip_keys = {'input_field', 'now'} | set(self.executor.get_systems().keys())
        
        for key, value in context.items():
            if key not in skip_keys:
                self.game_state[key] = value
    
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

    def update_state_from_json(self, data: dict):
        """
        Updates game_state with key-value pairs from a dictionary.
        Handles dot notation for object attributes.
        """
        for key, value in data.items():
            if '.' in key:
                # Handle dot notation (e.g., 'player.name')
                parts = key.split('.')
                current = self.game_state
                
                # Navigate to the parent object
                for part in parts[:-1]:
                    if part in current:
                        current = current[part]
                    else:
                        # Create nested dict if it doesn't exist
                        current[part] = {}
                        current = current[part]
                
                # Set the final attribute/key
                final_key = parts[-1]
                if hasattr(current, final_key):
                    # It's an object attribute
                    setattr(current, final_key, value)
                else:
                    # It's a dictionary key
                    current[final_key] = value
            else:
                # Simple top-level assignment
                self.game_state[key] = value

    def set_game_state(self, new_state: dict):
        """
        Sets the entire game state to a new state.
        """
        if isinstance(new_state, dict):
            self.game_state = new_state
        else:
            raise TypeError("New game state must be a dictionary.")
    
    def get_serializable_state(self):
        """
        Get game state in JSON-serializable format
        """
        serializable_state = {}
        for key, value in self.game_state.items():
            if hasattr(value, 'to_dict'):
                # Handle Player objects with to_dict method (DefaultPlayer)
                serializable_state[key] = value.to_dict()
            elif hasattr(value, '__dict__'):
                # Handle custom Player classes and other objects
                obj_dict = {k: v for k, v in vars(value).items() if not k.startswith('__') and not callable(v)}
                obj_dict['__class_name__'] = type(value).__name__
                serializable_state[key] = obj_dict
            else:
                # Handle primitives and basic types
                serializable_state[key] = value
        return serializable_state
    
    def restore_state_from_dict(self, state_dict: dict):
        """
        Restore game state from serialized dictionary
        """
        self.game_state.clear()
        
        for key, value in state_dict.items():
            if isinstance(value, dict) and '__class_name__' in value:
                # Restore Player objects
                class_name = value['__class_name__']
                if class_name == 'DefaultPlayer':
                    from .state import DefaultPlayer
                    self.game_state[key] = DefaultPlayer.from_dict(value)
                else:
                    # Handle custom Player classes
                    systems = self.executor.get_systems()
                    if class_name in systems and isinstance(systems[class_name], type):
                        # Create instance and set attributes
                        player_instance = systems[class_name]()
                        for attr_name, attr_value in value.items():
                            if not attr_name.startswith('__'):
                                setattr(player_instance, attr_name, attr_value)
                        self.game_state[key] = player_instance
                    else:
                        # Fallback to dictionary if class not found
                        self.game_state[key] = value
            else:
                # Regular values
                self.game_state[key] = value

    def reset_game_state(self):
        """
        Resets the current game state to the initial state, including project-specific state.
        """
        # Get the base initial state from the state manager
        initial_state = self.state_manager.get_initial_state()
        self.game_state.clear()
        self.game_state.update(initial_state)

        # Re-instantiate Player class if found
        systems = self.executor.get_systems()
        if 'Player' in systems and isinstance(systems['Player'], type):
            self.game_state['player'] = systems['Player']()

        if self.debug_mode:
            print("Game state has been reset (including custom project state).")

    
        

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
