# Text Game Engine Design Document

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [File Structure](#file-structure)
5. [Core Components](#core-components)
6. [Game File Format](#game-file-format)
7. [State Management](#state-management)
8. [Python Code Execution](#python-code-execution)
9. [Template System](#template-system)
10. [Web Interface](#web-interface)
11. [Debugging System](#debugging-system)
12. [Storage & Persistence](#storage--persistence)
13. [Styling System](#styling-system)
14. [API Endpoints](#api-endpoints)
15. [Implementation Guide](#implementation-guide)
16. [Security Considerations](#security-considerations)
17. [Testing Strategy](#testing-strategy)
18. [Future Enhancements](#future-enhancements)

## Overview

This text-based game engine allows creators to build interactive fiction games using a combination of plain text, HTML, Jinja2 templating, and embedded Python code. The engine is inspired by Twine but provides more programming flexibility through Python integration.

### Key Features
- **Passage-based storytelling** with dynamic content
- **Embedded Python code** for complex game logic
- **Real-time state management** with flags and variables
- **HTMX-powered interface** for smooth interactions
- **Flexible styling** with custom CSS support
- **Save/Load system** with JSON or SQLite storage
- **Built-in debugging tools** for development
- **Safe code execution** with sandboxed Python environment

### Target Users
- **Game creators** who want more programming power than Twine
- **Developers** building interactive fiction
- **Educators** creating interactive learning experiences
- **Writers** who want to add dynamic elements to their stories

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Browser                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Game UI       │  │   Debug Panel   │  │   Styling   │ │
│  │   (HTMX)        │  │   (Console)     │  │   (CSS)     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP Requests
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Flask Application                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Route Handler │  │   Game Engine   │  │   Template  │ │
│  │                 │  │   Core          │  │   Generator │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Safe Executor │  │   State Manager │  │   Parser    │ │
│  │                 │  │                 │  │             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Data Persistence
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Storage Layer                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Game Files    │  │   Save Files    │  │   Assets    │ │
│  │   (.tgame)      │  │   (JSON/SQLite) │  │   (CSS)     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend
- **Python 3.8+** - Core language
- **Flask** - Web framework
- **Jinja2** - Template engine (included with Flask)
- **SQLite** - Optional database storage
- **JSON** - Default save format

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling
- **HTMX** - Dynamic interactions
- **JavaScript** - Minimal client-side logic

### Development Tools
- **Python Standard Library** - Core functionality
- **Regular Expressions** - Parsing
- **AST Module** - Safe code compilation
- **Traceback** - Error handling

## File Structure

```
text-game-engine/
├── engine/
│   ├── __init__.py
│   ├── core.py              # Main game engine
│   ├── parser.py            # .tgame file parser
│   ├── executor.py          # Safe Python execution
│   ├── state.py             # State management
│   ├── storage.py           # Save/load functionality
│   └── debug.py             # Debugging utilities
├── templates/
│   ├── base.html            # Base HTML template
│   └── game.html            # Game interface template
├── static/
│   ├── css/
│   │   ├── engine.css       # Default styling
│   │   └── themes/          # Optional themes
│   ├── js/
│   │   └── engine.js        # Minimal client-side code
│   └── assets/              # Game assets
├── games/
│   ├── example.tgame        # Example game file
│   └── custom.css           # Custom styling (optional)
├── saves/                   # Save files directory
├── app.py                   # Flask application entry point
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
└── README.md               # Setup instructions
```

## Core Components

### 1. GameEngine Class
The main orchestrator that coordinates all components.

```python
class GameEngine:
    def __init__(self, game_file, debug_mode=False):
        self.game_file = game_file
        self.debug_mode = debug_mode
        self.passages = {}
        self.game_state = self.initialize_state()
        self.parser = GameParser()
        self.executor = SafeExecutor(self.game_state, debug_mode)
        self.storage = JSONStorage()  # or SQLiteStorage()
        
    def load_game(self):
        """Load and parse the game file"""
        
    def render_passage(self, passage_name):
        """Render a passage with all processing"""
        
    def save_game(self, slot):
        """Save current game state"""
        
    def load_save(self, slot):
        """Load saved game state"""
```

### 2. GameParser Class
Parses .tgame files into structured data.

```python
class GameParser:
    def parse_file(self, filename):
        """Parse a .tgame file into passage data"""
        
    def parse_passage(self, content):
        """Parse individual passage content"""
        
    def extract_python_blocks(self, content):
        """Extract and process Python code blocks"""
        
    def extract_links(self, content):
        """Extract Twine-style links"""
```

### 3. SafeExecutor Class
Handles safe execution of embedded Python code.

```python
class SafeExecutor:
    def __init__(self, game_state, debug_mode=False):
        self.game_state = game_state
        self.debug_mode = debug_mode
        self.allowed_imports = ['random', 'math', 'datetime']
        
    def create_safe_globals(self):
        """Create sandboxed execution environment"""
        
    def execute_code(self, code):
        """Execute Python code safely"""
        
    def update_game_state(self, safe_globals):
        """Update game state after execution"""
```

### 4. StateManager Class
Manages game state and provides helper functions.

```python
class StateManager:
    def __init__(self):
        self.current_passage = 'start'
        self.flags = {}
        self.variables = {}
        self.player = self.create_default_player()
        
    def set_flag(self, name, value=True):
        """Set a game flag"""
        
    def get_flag(self, name, default=False):
        """Get a game flag"""
        
    def add_to_inventory(self, item, quantity=1):
        """Add item to player inventory"""
        
    def has_item(self, item):
        """Check if player has item"""
```

## Game File Format

### File Extension
Games are stored in `.tgame` files (Text Game files).

### Basic Syntax

#### Passages
```html
:: passage_name
Content goes here...
```

#### Links
```html
[[Link text->target_passage]]
[[Another link->another_passage]]
```

#### Python Code Blocks
```python
{%- python %}
# Python code here
player.health += 10
set_flag('healed', True)
{%- endpython %}
```

#### Jinja2 Templates
```python
{% if player.health > 50 %}
You feel healthy!
{% else %}
You feel weak...
{% endif %}

Your health: {{ player.health }}
```

#### HTML Content
```html
<p>You can use <strong>HTML</strong> directly in passages.</p>
<div class="special-content">
    Custom styled content
</div>
```

### Complete Example

```python
:: start
Welcome to the Adventure Game!

{%- python %}
player.name = "Hero"
player.health = 100
player.inventory = []
set_flag('game_started', True)
debug("Game initialized")
{%- endpython %}

<h2>{{ player.name }}'s Adventure</h2>
<p>Your health: <span class="health">{{ player.health }}</span></p>

You stand at the entrance of a mysterious cave.

[[Enter the cave->cave_entrance]]
[[Walk away->forest_path]]

:: cave_entrance
You step into the dark cave. The air is cold and damp.

{%- python %}
import random
if random.randint(1, 10) > 7:
    set_flag('found_torch', True)
    add_to_inventory('torch', 1)
    debug("Player found a torch!")
{%- endpython %}

{% if get_flag('found_torch') %}
<p class="success">You found a torch on the ground!</p>
{% endif %}

The cave extends deeper into darkness.

{% if has_item('torch') %}
[[Light the torch and continue->cave_deep]]
{% endif %}
[[Continue in darkness->cave_dark]]
[[Return to entrance->start]]

:: cave_deep
With your torch lighting the way, you can see ancient drawings on the walls.

{%- python %}
player.experience = player.experience + 10 if hasattr(player, 'experience') else 10
set_flag('saw_drawings', True)
{%- endpython %}

The drawings seem to tell a story of ancient treasure hidden deeper in the cave.

[[Examine the drawings closely->examine_drawings]]
[[Continue deeper->treasure_room]]
[[Return to entrance->start]]

:: examine_drawings
{%- python %}
if get_flag('saw_drawings'):
    set_flag('understood_map', True)
    debug("Player understood the map!")
{%- endpython %}

{% if get_flag('understood_map') %}
<p class="discovery">The drawings form a map! You now understand the cave's layout.</p>
{% endif %}

[[Use the map to find treasure->treasure_room]]
[[Return to cave entrance->cave_entrance]]

:: treasure_room
{%- python %}
if get_flag('understood_map'):
    add_to_inventory('gold', 100)
    add_to_inventory('ancient_gem', 1)
    set_flag('found_treasure', True)
    player.score = 1000
else:
    add_to_inventory('gold', 10)
    set_flag('found_small_treasure', True)
    player.score = 100
{%- endpython %}

{% if get_flag('found_treasure') %}
<h3>🏆 Incredible Discovery!</h3>
<p>Thanks to your understanding of the ancient map, you've found the legendary treasure!</p>
<p><strong>You found:</strong></p>
<ul>
    <li>100 gold pieces</li>
    <li>1 ancient gem</li>
</ul>
<p class="score">Final Score: {{ player.score }}</p>
{% else %}
<h3>Small Victory</h3>
<p>You found a small cache of gold coins.</p>
<p><strong>You found:</strong> 10 gold pieces</p>
<p class="score">Final Score: {{ player.score }}</p>
{% endif %}

[[Start new adventure->start]]
```

## State Management

### Game State Structure
```python
game_state = {
    'current_passage': 'start',
    'flags': {},
    'variables': {},
    'player': {
        'name': '',
        'health': 100,
        'inventory': [],
        'score': 0,
        # Additional player attributes...
    },
    'metadata': {
        'game_title': '',
        'author': '',
        'version': '1.0',
        'created_date': '',
        'last_played': ''
    }
}
```

### Built-in Helper Functions
Available in Python code blocks:

```python
# Flag management
set_flag(name, value=True)
get_flag(name, default=False)

# Inventory management
add_to_inventory(item, quantity=1)
remove_from_inventory(item, quantity=1)
has_item(item)
get_item_count(item)

# Player management
set_player_attribute(key, value)
get_player_attribute(key, default=None)

# Variable management
set_variable(key, value)
get_variable(key, default=None)

# Debugging
debug(message)
log_error(message)

# Utility functions
random_int(min, max)
random_choice(list)
```

## Python Code Execution

### Sandboxed Environment
The engine provides a restricted Python environment with:

#### Allowed Built-ins
- Basic types: `int`, `float`, `str`, `bool`, `list`, `dict`
- Utility functions: `len`, `range`, `min`, `max`, `sum`
- Math operations: `abs`, `round`
- String operations: `str.upper`, `str.lower`, `str.strip`

#### Allowed Imports
- `random` - For random number generation
- `math` - For mathematical operations
- `datetime` - For date/time operations

#### Restricted Operations
- File I/O operations
- Network operations
- System calls
- Dangerous built-ins (`eval`, `exec`, `import`, etc.)

### Error Handling
```python
try:
    # Execute user code
    exec(compiled_code, safe_globals, safe_locals)
except SyntaxError as e:
    return f"Syntax Error: {e}"
except NameError as e:
    return f"Name Error: {e}"
except Exception as e:
    return f"Runtime Error: {e}"
```

### Code Block Processing
1. **Extract** Python blocks from passage content
2. **Compile** code using `compile()` function
3. **Execute** in sandboxed environment
4. **Update** game state from execution results
5. **Replace** code blocks with output or remove them

## Template System

### Dynamic Template Generation
The engine generates Jinja2 templates on-the-fly:

```python
def generate_template(passage_data):
    template_parts = []
    
    # Passage wrapper
    template_parts.append('<div class="passage" data-passage="{{ current_passage }}">')
    
    # Content section
    template_parts.append('<div class="content">')
    template_parts.append(passage_data['processed_content'])
    template_parts.append('</div>')
    
    # Choices section
    if passage_data['links']:
        template_parts.append('<div class="choices">')
        for text, target in passage_data['links']:
            template_parts.append(f'''
                <button hx-get="/passage/{target}" 
                        hx-target="#game-content" 
                        class="choice-btn"
                        data-target="{target}">
                    {text}
                </button>
            ''')
        template_parts.append('</div>')
    
    template_parts.append('</div>')
    
    return ''.join(template_parts)
```

### Template Context
Templates have access to:
- `player` - Player object
- `flags` - Game flags dictionary
- `variables` - Game variables dictionary
- `current_passage` - Current passage name
- Helper functions (via custom filters)

## Web Interface

### Base HTML Template
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ game_title or "Text Game Engine" }}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/engine.css') }}">
    {% if custom_css_exists %}
    <link rel="stylesheet" href="{{ url_for('serve_custom_css') }}">
    {% endif %}
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
</head>
<body>
    <div id="game-container">
        <header id="game-header">
            <h1>{{ game_title or "Adventure Game" }}</h1>
            <div id="game-controls">
                <button id="save-btn" onclick="saveGame()">Save</button>
                <button id="load-btn" onclick="loadGame()">Load</button>
                {% if debug_mode %}
                <button id="debug-btn" onclick="toggleDebug()">Debug</button>
                {% endif %}
            </div>
        </header>
        
        <main id="game-content" hx-get="/passage/start" hx-trigger="load">
            <div class="loading">Loading game...</div>
        </main>
        
        {% if debug_mode %}
        <aside id="debug-panel" style="display: none;">
            <h3>Debug Info</h3>
            <div id="debug-content"></div>
        </aside>
        {% endif %}
    </div>
    
    <script src="{{ url_for('static', filename='js/engine.js') }}"></script>
</body>
</html>
```

### HTMX Integration
- **hx-get**: Navigate to passages
- **hx-target**: Update content area
- **hx-trigger**: Auto-load on page load
- **hx-swap**: Control update behavior

## Debugging System

### Debug Mode Features
1. **Console Logging**: All `debug()` calls appear in browser console
2. **Error Display**: Python errors shown in passages (debug mode only)
3. **State Inspection**: Debug panel shows current game state
4. **Passage Navigation**: View all available passages

### Debug Endpoints
```python
@app.route('/debug/state')
def debug_state():
    """Return current game state as JSON"""
    return jsonify(game_engine.game_state)

@app.route('/debug/passages')
def debug_passages():
    """Return list of all passages"""
    return jsonify(list(game_engine.passages.keys()))

@app.route('/debug/passage/<name>')
def debug_passage(name):
    """Return raw passage data"""
    return jsonify(game_engine.passages.get(name, {}))
```

### Client-Side Debug Panel
```javascript
function toggleDebug() {
    const panel = document.getElementById('debug-panel');
    if (panel.style.display === 'none') {
        panel.style.display = 'block';
        updateDebugInfo();
    } else {
        panel.style.display = 'none';
    }
}

function updateDebugInfo() {
    fetch('/debug/state')
        .then(response => response.json())
        .then(data => {
            document.getElementById('debug-content').innerHTML = 
                '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        });
}
```

## Storage & Persistence

### JSON Storage (Default)
```python
class JSONStorage:
    def __init__(self, save_dir='saves'):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
    
    def save_game(self, slot, game_state):
        filename = f"{self.save_dir}/slot_{slot}.json"
        save_data = {
            'game_state': game_state,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0'
        }
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)
    
    def load_game(self, slot):
        filename = f"{self.save_dir}/slot_{slot}.json"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return None
    
    def list_saves(self):
        saves = []
        for filename in os.listdir(self.save_dir):
            if filename.startswith('slot_') and filename.endswith('.json'):
                slot = int(filename.split('_')[1].split('.')[0])
                saves.append(slot)
        return sorted(saves)
```

### SQLite Storage (Optional)
```python
class SQLiteStorage:
    def __init__(self, db_path='game.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS saves (
                slot INTEGER PRIMARY KEY,
                game_state TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                version TEXT DEFAULT '1.0'
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_game(self, slot, game_state):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT OR REPLACE INTO saves (slot, game_state, timestamp)
            VALUES (?, ?, ?)
        ''', (slot, json.dumps(game_state), datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def load_game(self, slot):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            'SELECT game_state, timestamp FROM saves WHERE slot = ?',
            (slot,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'game_state': json.loads(result[0]),
                'timestamp': result[1]
            }
        return None
```

## Styling System

### Default Engine Styles
```css
/* engine.css */
body {
    font-family: 'Georgia', serif;
    line-height: 1.6;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f5f5f5;
}

#game-container {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    padding: 20px;
}

.passage {
    margin-bottom: 20px;
}

.passage .content {
    margin-bottom: 20px;
}

.choices {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.choice-btn {
    padding: 10px 15px;
    border: 2px solid #333;
    background: white;
    cursor: pointer;
    border-radius: 4px;
    font-size: 16px;
    transition: all 0.2s;
}

.choice-btn:hover {
    background: #333;
    color: white;
}

.debug-error {
    background: #ffebee;
    border: 1px solid #e57373;
    color: #c62828;
    padding: 10px;
    border-radius: 4px;
    margin: 10px 0;
}

.success {
    color: #2e7d32;
    font-weight: bold;
}

.health {
    font-weight: bold;
    color: #1976d2;
}

.score {
    font-size: 18px;
    font-weight: bold;
    color: #7b1fa2;
}
```

### Custom CSS Support
Users can create a `custom.css` file that overrides default styles:

```python
@app.route('/custom.css')
def serve_custom_css():
    custom_css_path = os.path.join(game_dir, 'custom.css')
    if os.path.exists(custom_css_path):
        return send_file(custom_css_path, mimetype='text/css')
    return '', 404
```

## API Endpoints

### Core Game Routes
```python
@app.route('/')
def index():
    """Main game page"""

@app.route('/passage/<passage_name>')
def render_passage(passage_name):
    """Render a specific passage"""

@app.route('/save', methods=['POST'])
def save_game():
    """Save current game state"""

@app.route('/load', methods=['POST'])
def load_game():
    """Load saved game state"""

@app.route('/saves')
def list_saves():
    """List available save slots"""
```

### Debug Routes
```python
@app.route('/debug/state')
def debug_state():
    """Get current game state"""

@app.route('/debug/passages')
def debug_passages():
    """List all passages"""

@app.route('/debug/passage/<name>')
def debug_passage(name):
    """Get specific passage data"""
```

### Asset Routes
```python
@app.route('/custom.css')
def serve_custom_css():
    """Serve custom CSS file"""

@app.route('/assets/<path:filename>')
def serve_asset(filename):
    """Serve game assets"""
```

## Implementation Guide

### Phase 1: Core Engine (Week 1-2)
1. Create basic Flask application structure
2. Implement GameParser for basic passage parsing
3. Build SafeExecutor for Python code execution
4. Create StateManager for game state handling
5. Implement basic passage rendering

### Phase 2: Web Interface (Week 3)
1. Create HTML templates with HTMX integration
2. Implement dynamic passage loading
3. Add basic styling system
4. Create save/load functionality

### Phase 3: Advanced Features (Week 4)
1. Add debugging system
2. Implement error handling
3. Add custom CSS support
4. Create helper functions for game creators

### Phase 4: Polish & Testing (Week 5)
1. Add comprehensive error handling
2. Implement security measures
3. Create example games
4. Write documentation

### Development Setup
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install flask jinja2

# 3. Create basic project structure
mkdir text-game-engine
cd text-game-engine
mkdir engine templates static games saves
mkdir static/css static/js

# 4. Start development
python app.py
```

### Required Dependencies
```
# requirements.txt
Flask==2.3.3
Jinja2==3.1.2
Werkzeug==2.3.7
```

## Security Considerations

### Python Code Execution
1. **Restricted Built-ins**: Only safe built-in functions allowed
2. **Limited Imports**: Only approved modules can be imported
3. **No File I/O**: File operations are blocked
4. **No Network Access**: Network operations are blocked
5. **Exception Handling**: All errors are caught and handled safely

### Web Security
1. **Input Validation**: All user inputs are validated
2. **XSS Prevention**: Content is properly escaped
3. **CSRF Protection**: Forms include CSRF tokens
4. **Safe File Handling**: File operations are restricted

### Implementation
```python
# Safe globals for code execution
SAFE_BUILTINS = {
    'len': len, 'str': str, 'int': int, 'float': float,
    'bool': bool, 'list': list, 'dict': dict, 'range': range,
    'min': min, 'max': max, 'sum': sum, 'abs': abs, 'round': round
}

ALLOWED_IMPORTS = {'random', 'math', 'datetime'}

def create_safe_globals():
    return {
        '__builtins__': SAFE_BUILTINS,
        # Add game-specific functions
    }
```

## Testing Strategy

### Unit Tests
```python
# test_parser.py
def test_passage_parsing():
    parser = GameParser()
    content = ":: test\nHello world\n[[Next->next]]"
    result = parser.parse_file_content(content)
    assert 'test' in result
    assert len(result['test']['links']) == 1

# test_executor.py
def test_safe_execution():
    executor = SafeExecutor({}, debug_mode=True)
    code = "x = 5 + 3"
    result = executor.execute_code(code)
    assert result is None  # No error
```

### Integration Tests
```python
# test_engine.py
def test_passage_rendering():
    engine = GameEngine('test.tgame')
    html = engine.render_passage('start')
    assert '<div class="passage"' in html
    assert 'choice-btn' in html
```

### End-to-End Tests
```python
# test_webapp.py
def test_game_flow():
    with app.test_client() as client:
        # Test initial load
        response = client.get('/')
        assert response.status_code == 200
        
        # Test passage navigation
        response = client.get('/passage/start')
        assert response.status_code == 200
        
        # Test save/load
        response = client.post('/save', json={'slot': 1})
        assert response.status_code == 200
```

## Future Enhancements

### Version 2.0 Features
1. **Visual Editor**: Web-based game creation interface
2. **Asset Management**: Image and audio support
3. **Advanced Templating**: Custom template functions
4. **Plugin System**: Extensible functionality

### Version 3.0 Features
1. **Cloud Saves**: Online save synchronization
2. **Social Features**: Game sharing and reviews
3. **AI Integration**: AI-assisted game creation

### Technical Improvements
1. **Performance Optimization**: Caching and lazy loading
2. **Scalability**: Multi-tenant architecture
3. **Monitoring**: Application performance monitoring
4. **CI/CD**: Automated testing and deployment
5. **Documentation**: Interactive tutorials and guides

---

## Conclusion

This design document provides a comprehensive blueprint for building a powerful text-based game engine. The architecture balances flexibility with security, allowing game creators to build complex interactive fiction while maintaining a safe execution environment.

The phased implementation approach ensures steady progress while allowing for iterative improvements. The modular design makes it easy to extend functionality and add new features as needed.

Key success factors:
- **Security**: Safe Python execution environment
- **Usability**: Intuitive game creation workflow
- **Flexibility**: Support for complex game logic
- **Performance**: Efficient rendering and state management
- **Extensibility**: Modular architecture for future enhancements

## Sample Implementation Files

### app.py (Main Application)
```python
from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime
from engine.core import GameEngine
from engine.debug import DebugManager

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change in production

# Initialize game engine
GAME_FILE = 'games/example.tgame'
game_engine = GameEngine(GAME_FILE, debug_mode=True)
debug_manager = DebugManager(game_engine)

@app.route('/')
def index():
    """Main game page"""
    return render_template('game.html', 
                         game_title=game_engine.get_title(),
                         debug_mode=game_engine.debug_mode)

@app.route('/passage/<passage_name>')
def render_passage(passage_name):
    """Render a specific passage"""
    try:
        html = game_engine.render_passage(passage_name)
        return html
    except Exception as e:
        if game_engine.debug_mode:
            return f'<div class="debug-error">Error rendering passage: {str(e)}</div>'
        return '<div class="error">Passage not found</div>'

@app.route('/save', methods=['POST'])
def save_game():
    """Save current game state"""
    try:
        slot = request.json.get('slot', 1)
        game_engine.save_game(slot)
        return jsonify({'status': 'success', 'message': 'Game saved'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/load', methods=['POST'])
def load_game():
    """Load saved game state"""
    try:
        slot = request.json.get('slot', 1)
        success = game_engine.load_game(slot)
        if success:
            return jsonify({'status': 'success', 'message': 'Game loaded'})
        else:
            return jsonify({'status': 'error', 'message': 'Save not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/saves')
def list_saves():
    """List available save slots"""
    saves = game_engine.list_saves()
    return jsonify({'saves': saves})

@app.route('/custom.css')
def serve_custom_css():
    """Serve custom CSS file"""
    custom_css_path = os.path.join('games', 'custom.css')
    if os.path.exists(custom_css_path):
        return send_file(custom_css_path, mimetype='text/css')
    return '', 404

# Debug routes
@app.route('/debug/state')
def debug_state():
    """Get current game state"""
    if not game_engine.debug_mode:
        return jsonify({'error': 'Debug mode disabled'}), 403
    return jsonify(game_engine.game_state)

@app.route('/debug/passages')
def debug_passages():
    """List all passages"""
    if not game_engine.debug_mode:
        return jsonify({'error': 'Debug mode disabled'}), 403
    return jsonify(list(game_engine.passages.keys()))

@app.route('/debug/passage/<name>')
def debug_passage(name):
    """Get specific passage data"""
    if not game_engine.debug_mode:
        return jsonify({'error': 'Debug mode disabled'}), 403
    return jsonify(game_engine.passages.get(name, {}))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### engine/core.py (Game Engine Core)
```python
import os
import json
import re
from datetime import datetime
from jinja2 import Template
from .parser import GameParser
from .executor import SafeExecutor
from .state import StateManager
from .storage import JSONStorage

class GameEngine:
    def __init__(self, game_file, debug_mode=False):
        self.game_file = game_file
        self.debug_mode = debug_mode
        self.passages = {}
        self.parser = GameParser()
        self.state_manager = StateManager()
        self.storage = JSONStorage()
        self.game_state = self.state_manager.get_initial_state()
        
        # Load game file
        self.load_game_file()
    
    def load_game_file(self):
        """Load and parse the game file"""
        if not os.path.exists(self.game_file):
            raise FileNotFoundError(f"Game file not found: {self.game_file}")
        
        self.passages = self.parser.parse_file(self.game_file)
        if self.debug_mode:
            print(f"Loaded {len(self.passages)} passages")
    
    def render_passage(self, passage_name):
        """Render a passage with all processing"""
        if passage_name not in self.passages:
            raise ValueError(f"Passage '{passage_name}' not found")
        
        passage = self.passages[passage_name]
        self.game_state['current_passage'] = passage_name
        
        # Execute Python code blocks
        executor = SafeExecutor(self.game_state, self.debug_mode)
        processed_content = self.execute_python_blocks(passage, executor)
        
        # Process Jinja2 template
        template = Template(processed_content)
        rendered_content = template.render(**self.get_template_context())
        
        # Generate final HTML
        html = self.generate_passage_html(passage_name, rendered_content, passage['links'])
        
        return html
    
    def execute_python_blocks(self, passage, executor):
        """Execute Python code blocks in passage"""
        content = passage['content']
        
        for i, python_code in enumerate(passage['python_blocks']):
            placeholder = f"{{{{ PYTHON_BLOCK_{i} }}}}"
            try:
                error = executor.execute_code(python_code)
                if error and self.debug_mode:
                    content = content.replace(placeholder, f'<div class="debug-error">{error}</div>')
                else:
                    content = content.replace(placeholder, '')
            except Exception as e:
                if self.debug_mode:
                    content = content.replace(placeholder, f'<div class="debug-error">Python Error: {str(e)}</div>')
                else:
                    content = content.replace(placeholder, '')
        
        return content
    
    def get_template_context(self):
        """Get context for Jinja2 template rendering"""
        context = self.game_state.copy()
        context.update({
            'get_flag': self.state_manager.get_flag,
            'has_item': self.state_manager.has_item,
            'get_item_count': self.state_manager.get_item_count,
            'get_variable': self.state_manager.get_variable,
        })
        return context
    
    def generate_passage_html(self, passage_name, content, links):
        """Generate final HTML for passage"""
        html_parts = []
        
        # Passage wrapper
        html_parts.append(f'<div class="passage" data-passage="{passage_name}">')
        
        # Content
        html_parts.append('<div class="content">')
        html_parts.append(content)
        html_parts.append('</div>')
        
        # Links/Choices
        if links:
            html_parts.append('<div class="choices">')
            for text, target in links:
                html_parts.append(f'''
                    <button hx-get="/passage/{target}" 
                            hx-target="#game-content" 
                            class="choice-btn"
                            data-target="{target}">
                        {text}
                    </button>
                ''')
            html_parts.append('</div>')
        
        html_parts.append('</div>')
        
        return ''.join(html_parts)
    
    def save_game(self, slot):
        """Save current game state"""
        self.storage.save_game(slot, self.game_state)
    
    def load_game(self, slot):
        """Load saved game state"""
        saved_state = self.storage.load_game(slot)
        if saved_state:
            self.game_state = saved_state['game_state']
            return True
        return False
    
    def list_saves(self):
        """List available save slots"""
        return self.storage.list_saves()
    
    def get_title(self):
        """Get game title"""
        return self.game_state.get('metadata', {}).get('title', 'Text Adventure')
```

### engine/parser.py (Game File Parser)
```python
import re
from typing import Dict, List, Tuple

class GameParser:
    def __init__(self):
        self.python_block_pattern = re.compile(
            r'\{\%-?\s*python\s*%\}(.*?)\{\%-?\s*endpython\s*%\}',
            re.DOTALL
        )
        self.link_pattern = re.compile(r'\[\[([^-]+)->([^\]]+)\]\]')
    
    def parse_file(self, filename: str) -> Dict:
        """Parse a .tgame file into passage data"""
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> Dict:
        """Parse game content into passages"""
        passages = {}
        
        # Split content by passage headers
        passage_blocks = re.split(r'^:: (.+), content, flags=re.MULTILINE)
        
        # First block is usually empty or contains global settings
        for i in range(1, len(passage_blocks), 2):
            passage_name = passage_blocks[i].strip()
            passage_content = passage_blocks[i + 1].strip()
            
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
        
        return {
            'content': processed_content,
            'python_blocks': python_blocks,
            'links': [(text.strip(), target.strip()) for text, target in links]
        }
```

### engine/executor.py (Safe Python Executor)
```python
import sys
import traceback
from types import SimpleNamespace
from typing import Dict, Any, Optional

class SafeExecutor:
    def __init__(self, game_state: Dict, debug_mode: bool = False):
        self.game_state = game_state
        self.debug_mode = debug_mode
        self.allowed_imports = {'random', 'math', 'datetime'}
        
        # Reference to state manager functions
        self.state_manager = None
    
    def set_state_manager(self, state_manager):
        """Set reference to state manager"""
        self.state_manager = state_manager
    
    def create_safe_globals(self) -> Dict[str, Any]:
        """Create safe execution environment"""
        # Safe built-ins
        safe_builtins = {
            'len': len, 'str': str, 'int': int, 'float': float,
            'bool': bool, 'list': list, 'dict': dict, 'range': range,
            'min': min, 'max': max, 'sum': sum, 'abs': abs, 'round': round,
            'print': self.debug_print, 'isinstance': isinstance,
            'hasattr': hasattr, 'getattr': getattr, 'setattr': setattr
        }
        
        # Create player namespace
        player_dict = self.game_state.get('player', {})
        player_ns = SimpleNamespace(**player_dict)
        
        safe_globals = {
            '__builtins__': safe_builtins,
            'player': player_ns,
            'flags': self.game_state.get('flags', {}),
            'variables': self.game_state.get('variables', {}),
            # Helper functions
            'set_flag': self.set_flag,
            'get_flag': self.get_flag,
            'add_to_inventory': self.add_to_inventory,
            'remove_from_inventory': self.remove_from_inventory,
            'has_item': self.has_item,
            'get_item_count': self.get_item_count,
            'set_variable': self.set_variable,
            'get_variable': self.get_variable,
            'debug': self.debug_print,
            'random': self.safe_import('random'),
            'math': self.safe_import('math'),
            'datetime': self.safe_import('datetime'),
        }
        
        return safe_globals
    
    def safe_import(self, module_name: str):
        """Safely import allowed modules"""
        if module_name in self.allowed_imports:
            return __import__(module_name)
        raise ImportError(f"Module '{module_name}' not allowed")
    
    def execute_code(self, code: str) -> Optional[str]:
        """Execute Python code safely"""
        try:
            safe_globals = self.create_safe_globals()
            safe_locals = {}
            
            # Compile code first to catch syntax errors
            compiled = compile(code, '<passage>', 'exec')
            
            # Execute code
            exec(compiled, safe_globals, safe_locals)
            
            # Update game state
            self.update_game_state(safe_globals)
            
            return None  # No error
            
        except SyntaxError as e:
            error_msg = f"Syntax Error: {str(e)}"
            self.debug_print(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Runtime Error: {str(e)}"
            self.debug_print(error_msg)
            if self.debug_mode:
                traceback.print_exc()
            return error_msg
    
    def update_game_state(self, safe_globals: Dict):
        """Update game state after code execution"""
        # Update player state
        player_ns = safe_globals['player']
        player_dict = {k: v for k, v in vars(player_ns).items() 
                      if not k.startswith('_')}
        self.game_state['player'] = player_dict
        
        # Flags and variables are updated by reference
    
    def debug_print(self, *args):
        """Debug print function"""
        if self.debug_mode:
            message = ' '.join(str(arg) for arg in args)
            print(f"[DEBUG] {message}")
    
    # Helper functions available in game code
    def set_flag(self, name: str, value: bool = True):
        """Set a game flag"""
        self.game_state['flags'][name] = value
        self.debug_print(f"Set flag '{name}' = {value}")
    
    def get_flag(self, name: str, default: bool = False) -> bool:
        """Get a game flag"""
        return self.game_state['flags'].get(name, default)
    
    def add_to_inventory(self, item: str, quantity: int = 1):
        """Add item to inventory"""
        inventory = self.game_state['player'].get('inventory', [])
        
        # Find existing item
        existing = next((i for i in inventory if i.get('name') == item), None)
        if existing:
            existing['quantity'] = existing.get('quantity', 1) + quantity
        else:
            inventory.append({'name': item, 'quantity': quantity})
        
        self.game_state['player']['inventory'] = inventory
        self.debug_print(f"Added {quantity} {item} to inventory")
    
    def remove_from_inventory(self, item: str, quantity: int = 1):
        """Remove item from inventory"""
        inventory = self.game_state['player'].get('inventory', [])
        
        for i, inv_item in enumerate(inventory):
            if inv_item.get('name') == item:
                current_qty = inv_item.get('quantity', 1)
                if current_qty <= quantity:
                    inventory.pop(i)
                else:
                    inv_item['quantity'] = current_qty - quantity
                break
        
        self.debug_print(f"Removed {quantity} {item} from inventory")
    
    def has_item(self, item: str) -> bool:
        """Check if player has item"""
        inventory = self.game_state['player'].get('inventory', [])
        return any(i.get('name') == item for i in inventory)
    
    def get_item_count(self, item: str) -> int:
        """Get count of specific item"""
        inventory = self.game_state['player'].get('inventory', [])
        for inv_item in inventory:
            if inv_item.get('name') == item:
                return inv_item.get('quantity', 0)
        return 0
    
    def set_variable(self, key: str, value: Any):
        """Set a game variable"""
        self.game_state['variables'][key] = value
        self.debug_print(f"Set variable '{key}' = {value}")
    
    def get_variable(self, key: str, default: Any = None) -> Any:
        """Get a game variable"""
        return self.game_state['variables'].get(key, default)
```

### engine/state.py (State Manager)
```python
from typing import Dict, Any, List
from datetime import datetime

class StateManager:
    def __init__(self):
        self.initial_state = self.create_initial_state()
    
    def create_initial_state(self) -> Dict[str, Any]:
        """Create initial game state"""
        return {
            'current_passage': 'start',
            'flags': {},
            'variables': {},
            'player': {
                'name': '',
                'health': 100,
                'inventory': [],
                'score': 0,
                'experience': 0,
                'level': 1
            },
            'metadata': {
                'title': 'Text Adventure',
                'author': '',
                'version': '1.0',
                'created_date': datetime.now().isoformat(),
                'last_played': datetime.now().isoformat()
            }
        }
    
    def get_initial_state(self) -> Dict[str, Any]:
        """Get a copy of initial state"""
        return self.initial_state.copy()
    
    def reset_state(self) -> Dict[str, Any]:
        """Reset to initial state"""
        return self.create_initial_state()
    
    def validate_state(self, state: Dict[str, Any]) -> bool:
        """Validate state structure"""
        required_keys = ['current_passage', 'flags', 'variables', 'player']
        return all(key in state for key in required_keys)
    
    def get_flag(self, state: Dict[str, Any], name: str, default: bool = False) -> bool:
        """Get flag value"""
        return state.get('flags', {}).get(name, default)
    
    def set_flag(self, state: Dict[str, Any], name: str, value: bool = True):
        """Set flag value"""
        if 'flags' not in state:
            state['flags'] = {}
        state['flags'][name] = value
    
    def has_item(self, state: Dict[str, Any], item: str) -> bool:
        """Check if player has item"""
        inventory = state.get('player', {}).get('inventory', [])
        return any(i.get('name') == item for i in inventory)
    
    def get_item_count(self, state: Dict[str, Any], item: str) -> int:
        """Get item count"""
        inventory = state.get('player', {}).get('inventory', [])
        for inv_item in inventory:
            if inv_item.get('name') == item:
                return inv_item.get('quantity', 0)
        return 0
    
    def get_variable(self, state: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Get variable value"""
        return state.get('variables', {}).get(key, default)
    
    def set_variable(self, state: Dict[str, Any], key: str, value: Any):
        """Set variable value"""
        if 'variables' not in state:
            state['variables'] = {}
        state['variables'][key] = value
```

This completes the comprehensive design document with practical implementation examples. The document now provides everything needed to build a fully functional text-based game engine with embedded Python support, debugging capabilities, and a modern web interface powered by Flask and HTMX.