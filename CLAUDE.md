# CLAUDE.md

This file provides guidance when working with code in this repository.

**NOTE**: This repository contains both v1 (text-based) and v2 (scene-based 2D) engines.
Current branch: `v2-development` - See `docs/V2_VISION.md` for v2 architecture details.

## Development Commands

### Core Development
- `python3 ide/gui_launcher.py` - Launch the Scribe Engine GUI interface (primary launcher)
- `python3 v1_engine/main_engine.py` - Launch the v1 CLI menu system (alternative for developers)
- `python3 -m venv venv && source venv/bin/activate` - Set up virtual environment
- `pip install -r requirements.txt` - Install dependencies

### Project Structure (Post-Restructure)
```
ScribeEngine/
├── v1_engine/              # V1 text-based game engine
├── v2_engine/              # V2 scene-based 2D engine (in development)
├── shared/                 # Code shared between v1 and v2
│   ├── build/              # Build system, asset packer, installer
│   ├── storage/            # Save/load system
│   └── utils/              # Config, updates, version, loading window
├── ide/                    # IDE application (handles both v1 & v2)
│   ├── templates/          # IDE UI templates
│   └── static/             # IDE assets
├── docs/                   # Documentation
└── ide_demo/              # V2 IDE prototype
```

### Building and Deployment

**Asset Packer System (Current - v1.3.x):**
- **One-Click Building**: GUI "Build" button creates obfuscated game distributions in 5-15 seconds
- **Universal Player**: ScribePlayer executable (~200MB) handles all games + small game.dat archives
- **Embedded Architecture**: ScribePlayer bundled inside main engine, extracted during builds
- **Protected Assets**: XOR-encrypted, filename-obfuscated game content prevents casual tampering
- **Local Builds**: Distributions created in `<project>/builds/` directory for organization
- **Professional Installation**: First-launch installer with progress UI and encrypted file deployment
- **Secure Caching**: 10x+ faster subsequent launches through encrypted persistent cache
- **Loading Screens**: Branded startup experience with custom game icons

**Engine Distribution (For Engine Creators):**
- `python3 shared/build/build_player.py` - Build universal ScribePlayer executable (done once)
- `python3 shared/build/build_engine.py gui` - Build GUI engine with embedded ScribePlayer (primary distribution)
- `python3 shared/build/build_engine.py` - Build CLI engine executable (developer tool)

### Running Development Server
The engine includes live-reloading development server accessible via:

**GUI Mode (Primary - Integrated IDE):**
1. Run `python3 ide/gui_launcher.py`
2. Uses integrated web interface at `http://127.0.0.1:5000/gui`
3. Provides complete development environment:
   - CodeMirror editor with Scribe Engine syntax highlighting
   - Live preview panel with real-time game updates
   - Debug terminal showing current game state
   - Visual project and file management

**CLI Mode (Developer Alternative):**
1. Run `python3 v1_engine/main_engine.py`
2. Create or load a project via CLI menu
3. Select "Start Development Server" from project menu
4. Access game at `http://127.0.0.1:5000`

## Architecture Overview

Scribe Engine is a Python-based text-based game engine that combines Flask web framework with desktop distribution capabilities. It uses a modular architecture with clear separation between engine logic and game content.

### Core Components

**Main Entry Points:**
- `gui_launcher.py` - Full integrated development environment with CodeMirror editor, syntax highlighting, live preview, and debug terminal
- `main_engine.py` - CLI launcher with project management, development server control, and build orchestration (developer alternative)
- `app.py` - Flask web application serving both game content and the integrated IDE interface
- `webview_wrapper.py` - Desktop wrapper using PyWebview for standalone game executables
- `game_server_wrapper.py` - Wrapper for standalone game distributions with loading window integration
- `build_engine.py` - Builds the engine itself into standalone executables (full IDE or CLI-only versions)
- `build_player.py` - Builds universal ScribePlayer executable for game distributions
- `loading_window.py` - Professional tkinter-based loading screen for application startup
- `update_checker.py` - Automatic update checking and installation system
- `version_info.py` - Centralized version tracking with build metadata

**Engine Core (`engine/` directory):**
- `core.py` - Central GameEngine class with unified state management, object serialization, and enhanced save/load functionality
- `parser.py` - Parses `.tgame` files (custom story format) into structured data
- `executor.py` - Sandboxed Python execution environment with direct state references
- `state.py` - Modern state management with DefaultPlayer class and JSON serialization
- `storage.py` - Enhanced JSON-based save/load system with metadata, timestamps, and object restoration
- `browser_storage.py` - Browser localStorage-based save system for web hosting environments
- `asset_packer.py` - Obfuscated game archive creation and extraction with XOR encryption
- `game_installer.py` - Professional installation UI for first-launch game setup with encrypted file deployment
- `secure_cache.py` - Encrypted persistent caching system for improved game launch performance

**Web Layer:**
- `templates/` - Jinja2 HTML templates for game interface
- `static/` - CSS and JavaScript assets, including HTMX for dynamic interactions
- Uses HTMX extensively to minimize custom JavaScript while providing rich interactivity
- `game_server.py` - Minimal Flask server for standalone game distributions (gameplay routes only)

### Technology Stack

- **Python 3.12+** with Flask for backend web serving
- **Jinja2** for templating both web pages and in-game content rendering
- **HTMX** for client-side interactivity without heavy JavaScript
- **PyInstaller** + **PyWebview** for packaging games and engine as desktop executables
- **Tkinter** for loading windows and installation UI (standard library)
- **Watchdog** for live-reloading during development
- **Requests** for update checking and GitHub API integration
- **Pillow** for image handling in themes and assets

### Project Structure

Individual game projects are stored in user-defined project root directory. Each project contains:
- `project.json` - Game configuration and metadata
- `*.tgame` files - Story content in custom format with embedded Python logic
- `assets/` - Game-specific assets
- `saves/` - Enhanced save files with metadata, descriptions, timestamps, and object restoration
- Optional custom Python files for extended game logic and custom classes

### Game Content Format

Games use `.tgame` files with a custom syntax supporting:
- Passage-based story structure
- Embedded Python code blocks for game logic
- Jinja2 templating for dynamic content rendering
- Link syntax for navigation between passages

### Python Code Execution in Passages

**Syntax:**
- `{$ ... $}` - Inline Python logic (single statements)
- `{$- ... -$}` - Multi-line Python blocks

**Execution Order:**
1. **Python code executes first** - All `{$ $}` and `{$- -$}` blocks run before any Jinja2 processing
2. **Jinja2 templating renders second** - `{{ }}` expressions process after Python execution completes

**Examples:**
```
:: Combat Example
{$- 
# Multi-line Python block executes first
damage = random.randint(5, 15)
player.health -= damage
combat_result = "victory" if player.health > 0 else "defeat"
-$}

You take {{damage}} damage! {$ # This Python runs before Jinja2 below $}

{% if combat_result == "victory" %}
You survived with {{player.health}} health remaining!
[[Continue->next_passage]]
{% else %}
You have been defeated...
[[Try again->start]]
{% endif %}
```

**Important Note:**
Since Python executes before Jinja2, you cannot use Jinja2 variables inside Python blocks. However, Python variables become available to subsequent Jinja2 expressions in the same passage.

**Working with the Execution Order:**
```
:: Dynamic Combat
{$- 
# Python can access game state and player objects
weapon_damage = player.equipment.get('weapon', {}).get('damage', 1)
enemy_health = 50

# Calculate results before Jinja2 templating
if player.skills.get('Combat', 0) > 5:
    critical_hit = True
    final_damage = weapon_damage * 2
else:
    critical_hit = False  
    final_damage = weapon_damage

enemy_health -= final_damage
-$}

<!-- Jinja2 renders using Python variables -->
{% if critical_hit %}
**CRITICAL HIT!** 
{% endif %}

You deal {{final_damage}} damage! Enemy health: {{enemy_health}}

{% if enemy_health <= 0 %}
Victory! [[Continue->victory]]
{% else %}
Battle continues... [[Next round->combat_round]]
{% endif %}
```

**Potential Workarounds for Complex Cases:**
- Use multiple passages for complex interactions requiring Jinja2 → Python flow
- Store intermediate results in the game state for cross-passage logic
- Leverage Player class methods to encapsulate complex decision logic

### Player Class System

The engine supports flexible Player class definitions:

**Default Player (Quickstart):**
```python
# Automatically available when use_default_player: true
player.health -= 20
player.inventory.append("sword")
```

**Custom Player Classes:**
```python
# In player.py - automatically discovered and instantiated
class Player:
    def __init__(self, name="", **kwargs):
        self.name = name
        self.skills = {'Hacking': 5, 'Stealth': 3}
        self.inventory = []
    
    def skill_check(self, skill_name, difficulty):
        return self.skills.get(skill_name, 0) + random.randint(1, 10) >= difficulty
```

**Usage in .tgame files:**
```
:: Hacking Challenge
{$ success = player.skill_check('Hacking', 7) $}
{% if success %}
You successfully bypass the firewall!
{% else %}
Security detected your intrusion attempt.
{% endif %}
```

**Key Features:**
- **Auto-Discovery**: Player classes are automatically found and instantiated
- **Method Preservation**: Custom methods like `skill_check()` work seamlessly
- **State Persistence**: Object attributes survive across passages, engine reloads, and save/load cycles
- **Natural Syntax**: Use standard Python object syntax, no special engine APIs
- **Universal Class Support**: Any custom class with no-argument constructor works automatically

### State Management

The engine provides modern, object-oriented state management:
- **Unified State Architecture**: Single source of truth with direct object references
- **Auto-Instantiated Player Classes**: Custom Player classes are automatically discovered and instantiated
- **Default Player Quickstart**: Built-in DefaultPlayer class with health, energy, and inventory for simple projects
- **Natural Python Syntax**: Direct object access (`player.health -= 20`) instead of helper functions
- **Flattened State Structure**: No artificial nesting - variables exist at the top level where they belong
- **JSON Serialization**: Seamless conversion between objects and JSON for GUI integration
- **Sandboxed Execution**: Safe Python code execution with persistent state changes

### Development Workflow

**For End Users (Primary - Integrated IDE):**
1. Use `gui_launcher.py` or built `scribe-engine-v1.0-[platform]` executable
2. Features include:
   - CodeMirror editor with custom Scribe Engine syntax highlighting
   - Live preview panel with real-time game updates and state persistence
   - Debug terminal showing current game state with object visualization
   - Visual project management with file dialogs
   - Automatic state preservation during file edits and engine reloads
3. **One-Click Building**: Click "Build" button for instant game packaging (5-15 seconds)
4. **Automatic Distribution**: Games built to `<project>/builds/<Title>_Distribution/`
5. **Zero External Dependencies**: No PyInstaller, Python setup, or command-line tools needed

**For Developers (Alternative - External Editor):**
1. Use `main_engine.py` for CLI-based project management
2. Edit `.tgame` files and project configuration in preferred external IDE/editor
3. Development server provides live-reloading with persistent state management
4. Use Asset Packer API for programmatic builds:
   ```python
   from engine.asset_packer import AssetPacker
   packer = AssetPacker()
   info = packer.create_distribution(project_path, output_dir)
   ```

### Recent Enhancements (v1.3.x)

**IDE Improvements:**
- **Multi-File Editing**: Tab-based interface for editing multiple files simultaneously
- **Collapsible File List**: Improved file navigation and organization
- **Enhanced Asset Management**: Better UX/UI for managing game assets
- **Syntax Features**: Autoclosing for angled brackets, improved new file creation
- **Color Picker Tool**: Visual color selection for theme customization

**Navigation System:**
- **NavMenu Enhancements**: Support for conditional content in navigation
- **Flexible Positioning**: Horizontal/vertical navigation bar options
- **Dynamic Rendering**: Real-time updates with HTMX integration

**Development Tools:**
- **Action Buttons**: Quick-access buttons for common tasks
- **delete_var() Function**: Programmatic variable cleanup
- **Enhanced Debug Terminal**: Better state visualization and object inspection

**Build System Optimization:**
- **Installation Step Integration**: Faster subsequent game launches through caching
- **Improved Game Server**: Enhanced route handling and error management
- **Custom Icon Support**: Game-specific icons for branded distributions

**Editor Enhancements:**
- **Live Preview Fixes**: Resolved passage-tag-container bugs
- **File Management**: Improved new file modal and organization
- **Syntax Highlighting**: Enhanced Scribe Engine-specific highlighting

### Modern Development Features

**Simplified Game Logic:**
- No more helper functions like `set_flag()` or `get_variable()`
- Direct Python syntax: `health = 100`, `met_wizard = True`
- Object-oriented approach: `player.skills['Hacking'] += 1`

**Enhanced Debugging:**
- Real-time state visualization in GUI debug panel
- JSON-serializable state for easy inspection
- Object method discovery and display
- Automatic state synchronization across all engine components

**Advanced Save/Load System:**
- **Professional UI**: HTMX-powered modal system with visual save slot management
- **Rich Metadata**: Save descriptions, timestamps, passage locations, and play time tracking
- **Object Restoration**: Automatic restoration of custom classes with method preservation
- **Multiple Save Slots**: 6-slot system with 3-column grid layout for optimal organization
- **Export/Import**: Save file sharing and backup capabilities
- **Data Integrity**: Validation and error recovery for corrupted saves
- **Seamless Integration**: Changes to custom objects persist across all engine operations
- **Dual Storage Systems**: Server-side files (default) or browser localStorage (web hosting)

### Build System

**Engine Distribution:**
- `build_engine.py gui` creates the full IDE engine executable (primary distribution for end users)
- `build_engine.py` creates CLI-only engine executable (developer tool)
- Results in `dist_engine/` directory with versioned, platform-specific executables
- GUI version includes integrated editor, syntax highlighting, and debugging tools

**Asset Packer System (Current):**
- **Universal Player**: `build_player.py` creates ScribePlayer.exe (universal game runtime, ~200MB)
- **Fast Game Packaging**: Asset packer creates obfuscated `game.dat` archives in 5-15 seconds
- **One-Click Distribution**: GUI "Build" button uses internal asset packer (no external tools needed)
- **Embedded Player**: ScribePlayer.exe is bundled inside the main engine and extracted during game builds
- **Obfuscated Archives**: Game content is XOR-encrypted and filename-obfuscated to prevent casual tampering
- **Compact Distribution**: Game distribution = ScribePlayer.exe (~200MB) + game.dat (~1-10MB)
- **Professional Installation**: First-launch installer with tkinter UI, progress tracking, and encrypted file deployment
- **Secure Cache System**: Encrypted persistent caching for 10x+ faster subsequent game launches
- **Loading Screen**: Professional branded loading window with custom icon support during startup

**Asset Packer Benefits:**
- **95% Faster Builds**: Seconds instead of minutes (no PyInstaller per game)
- **Smaller Distributions**: ~200MB total vs ~400MB+ per game with old system
- **No External Dependencies**: Developers only need the Scribe Engine IDE
- **Asset Protection**: XOR encryption and filename obfuscation deters casual file modification
- **Consistent Runtime**: All games use the same tested player executable
- **Easy Updates**: Update ScribePlayer once, affects all games
- **Fast Startup**: Secure cache system dramatically improves subsequent launch times
- **Professional Experience**: Branded loading screens and installation wizards for polished player experience

**Legacy Build System (Deprecated):**
- Old `build_tool_standalone.py` system replaced by asset packer
- PyInstaller-based approach was slow and resource-intensive
- Each game required full Python interpreter bundling

## Update System

Scribe Engine includes an automated update checking and installation system that keeps the engine up to date with the latest features and fixes.

### Update Checker Features

**Automatic Version Detection:**
- Uses `version_info.py` module as primary source of truth
- Embedded in executables for persistent version tracking
- Fallback detection from executable names and build scripts
- Semantic versioning comparison (major.minor.patch)

**GitHub Integration:**
- Checks GitHub releases API for latest versions
- Automatic platform-specific asset detection (Windows/Linux/macOS)
- Prefers GUI versions over CLI versions when available
- Downloads and verifies release assets

**User Preferences:**
- Configurable check frequency (startup, daily, weekly)
- Skip version functionality to ignore specific releases
- Last check timestamp tracking
- Enable/disable update checking

**Update Process:**
- Automatic executable backup before update
- Progress indication during download
- Atomic replacement of current executable
- Automatic application restart after update
- Rollback to backup on failure

**Configuration:**
Settings stored in `config_manager` under `update_settings`:
```json
{
  "update_settings": {
    "check_for_updates": true,
    "check_frequency": "daily",
    "last_check": "2025-09-30T12:00:00",
    "skipped_versions": ["1.2.0"]
  }
}
```

**CLI Interface:**
```
🎉 Update Available!
Current version: v1.3.0
Latest version: v1.3.2
Release page: https://github.com/slate20/ScribeEngine/releases/tag/v1.3.2

Options:
1. Update now
2. Skip this version
3. Remind me later
```

**GUI Integration:**
- Returns update info dict for GUI dialogs
- Non-blocking background checks
- User-friendly update notifications

## Game Installation System

Distributed games use a professional installation system for first-launch setup, providing a polished player experience and improved performance.

### Installation Features

**Professional UI:**
- Tkinter-based installation wizard
- Custom game icon and title display
- Real-time progress tracking
- Cancellation support with cleanup

**Encrypted Deployment:**
- Files extracted from `game.dat` archive
- XOR encryption with project-specific keys
- Filename obfuscation for tamper resistance
- Organized installation to `game_data/` directory

**Installation Process:**
1. First launch detects missing installation
2. Professional loading window appears
3. Archive validation and integrity checking
4. Files extracted and encrypted to local directory
5. Installation metadata and manifest creation
6. Completion marker for future launches

**Performance Optimization:**
- Files installed to platform-appropriate cache directory
- Subsequent launches skip installation (10x+ faster)
- Installation validation on each launch
- Automatic repair for corrupted installations

**Installation Metadata:**
```json
{
  "game_title": "My Game",
  "installed_date": "2025-09-30T12:00:00",
  "file_count": 42,
  "encryption_key_hash": "abc123...",
  "filename_mapping": {...},
  "version": "1.0"
}
```

**Directory Structure:**
```
game_data/
├── .install_complete
├── install_info.json
├── f12345_ZmlsZW5hbWU.enc  # Encrypted game files
├── f12345_cHJvamVjdA.enc
└── assets/
    └── f12345_aW1hZ2U.enc
```

## Save/Load System

Scribe Engine features a comprehensive save/load system that combines professional UI design with robust backend functionality. The system supports two storage modes: server-side file storage (default) and browser localStorage (for web hosting).

### User Interface Features

**HTMX-Powered Modals:**
- **Consistent Layout**: Fixed 800px modal with responsive 3-column save slot grid
- **Visual Feedback**: Real-time slot selection, loading states, and success/error messaging
- **Keyboard Shortcuts**: F5/Ctrl+S for save, F9/Ctrl+L for load, Escape to close
- **Mobile Responsive**: Adapts to 2-column (tablet) and 1-column (mobile) layouts

**Save Slot Management:**
- **6 Save Slots**: Optimal balance between choice and organization
- **Rich Metadata Display**: Save descriptions, timestamps, passage locations, play time
- **Visual State Indicators**: Populated vs. empty slots with distinct styling
- **Overwrite Protection**: Clear warnings when overwriting existing saves

**Advanced Actions:**
- **Export/Import**: JSON-based save file sharing and backup
- **Delete Confirmation**: Protected deletion with confirmation dialogs
- **Batch Operations**: Efficient management of multiple save files

### Storage Systems

**Server-Side Storage (Default - `engine/storage.py`):**
- **File-Based**: Saves stored as JSON files in project `saves/` directory
- **Full Server Control**: Complete access to file system for management operations
- **Ideal For**: Desktop applications and servers with file system access

**Browser Cache Storage (`engine/browser_storage.py`):**
- **localStorage-Based**: Saves stored in browser's localStorage API
- **Web Hosting Friendly**: No server-side file operations required
- **Cross-Session Persistence**: Data survives browser restarts and page reloads
- **Storage Limits**: Typically 5-10MB per domain (varies by browser)
- **Ideal For**: Web hosting environments without file system access

**Project Configuration:**
```json
{
  "features": {
    "save_system": "server"  // or "browser"
  }
}
```

### Backend Architecture

**Enhanced Storage System (Both Modes):**
```python
# Save format with rich metadata
{
    'game_state': {...},           # Complete serialized game state
    'description': 'Boss Fight',   # User-provided description
    'passage_name': 'dragon_lair', # Current passage for navigation
    'timestamp': '2024-01-15...',  # Last modified
    'created_timestamp': '...',    # Creation time
    'playtime': 3600,             # Total play time in seconds
    'version': '2.0',             # Save format version
    'engine_version': '2.0'       # Engine compatibility
}
```

**Object Serialization System:**
- **Universal Class Support**: Any custom class with no-argument constructor works automatically
- **Method Preservation**: Object methods are fully functional after restoration
- **Nested Object Handling**: Complex object hierarchies are properly serialized/restored
- **Default Player Integration**: Built-in `DefaultPlayer` class with custom serialization

**API Integration:**
- **HTMX Routes**: `/modal/save`, `/modal/load`, `/modal/save/confirm`, etc.
- **Metadata Endpoints**: Rich save information for UI components
- **Export/Import**: RESTful endpoints for save file operations
- **Validation**: Server-side save file integrity checking
- **Browser Mode**: JavaScript code generation for localStorage operations
- **Unified Interface**: Same API routes work for both storage systems

### Custom Class Requirements

For automatic save/load compatibility, custom classes must meet these requirements:

- ✅ **No-argument constructor**: `def __init__(self):` or `def __init__(self, param="default"):`
- ✅ **Project directory**: Class files must be in the game project directory
- ✅ **Standard Python**: Use normal Python syntax and data types
- ✅ **Method design**: All methods work automatically after restoration

**Example Compatible Class:**
```python
# quest_manager.py
class QuestManager:
    def __init__(self):  # ✅ No required arguments
        self.active_quests = []      # ✅ Serializable attributes
        self.completed = {}          # ✅ Standard data types
    
    def start_quest(self, quest_id): # ✅ Methods work after loading
        self.active_quests.append(quest_id)
```

### Usage Patterns

**In Game Code:**
```
:: save_example
{$ 
# Create custom objects - they'll auto-save
quest_manager = QuestManager()
quest_manager.start_quest("dragon_hunt")
player.location = "mountain_cave"
$}

Progress saved automatically when using Save/Load buttons.

Current quests: {{quest_manager.active_quests|length}}
Location: {{player.location}}
```

**Save/Load Flow:**
1. Player clicks Save → Modal opens with 6-slot grid
2. Select slot → Details panel shows current passage and description field
3. Enter description → Confirm save with rich metadata
4. Player clicks Load → Modal shows populated saves with metadata
5. Select save → Preview shows save details and actions (export/delete)
6. Confirm load → Game state fully restored with working object methods

**Storage Mode Behavior:**
- **Server Mode**: Direct file operations, immediate persistence, unlimited storage
- **Browser Mode**: JavaScript execution, localStorage API, 5-10MB limits, export for backup

### Configuring Browser Cache Storage

**When to Use Browser Cache Mode:**
- Web hosting environments that don't allow server-side file operations
- Static hosting services (GitHub Pages, Netlify, Vercel, etc.)
- Shared hosting with restricted file system access
- Games deployed as pure client-side applications

**Configuration Steps:**
1. Open project settings in the Scribe Engine GUI
2. Set "Save System" dropdown to "Browser cache saves (web hosting)"
3. Save project configuration
4. Deploy game files to web hosting service
5. Players' saves will automatically use browser localStorage

**Browser Compatibility:**
- **Modern Browsers**: Full support (Chrome, Firefox, Safari, Edge)
- **Storage Capacity**: 5-10MB typical limit (varies by browser and device)
- **Persistence**: Data survives browser restarts, cleared by user or storage cleanup
- **Cross-Device**: Saves are device/browser specific (not synced across devices)

**Player Experience:**
- **Save Operations**: Identical UI and functionality to server mode
- **Export Feature**: Players can download saves as JSON files for backup
- **Import Feature**: Players can upload previously exported save files
- **Storage Monitoring**: Automatic warnings when approaching storage limits

**Technical Implementation:**
- **JavaScript Generation**: Server returns executable JavaScript instead of performing file operations
- **localStorage API**: Cross-session persistence with structured JSON data
- **HTMX Integration**: Seamless modal updates and dynamic content loading
- **Project-Specific Keys**: Multiple games on same domain use separate storage namespaces

## Version Management

Scribe Engine uses a centralized version tracking system to ensure consistent version information across all components.

### Version Info Module (`version_info.py`)

**Centralized Version Source:**
- Single source of truth for version information
- Embedded in all built executables
- Persists regardless of executable renaming
- Automatically updated during build process

**Version Metadata:**
```python
VERSION_INFO = {
    "major": 1,
    "minor": 3,
    "patch": 2,
    "version": "1.3.2",
    "build_date": "2025-09-26T14:09:56",
    "commit_hash": "a7d6c7d"
}
```

**API Functions:**
- `get_version()` - Returns version string (e.g., "1.3.2")
- `get_version_info()` - Returns full metadata dictionary
- `set_version(version)` - Updates version during build process
- `set_build_metadata(build_date, commit_hash)` - Sets build metadata

**Integration:**
- Used by `update_checker.py` for version detection
- Displayed in GUI "About" dialogs
- Included in executable filenames during builds
- Tracked in git commits and releases

**Build Process Integration:**
```python
# build_engine.py sets version before building
import version_info
version_info.set_version("1.3.2")
version_info.set_build_metadata(
    build_date=datetime.now().isoformat(),
    commit_hash=get_git_commit_hash()
)
```

## Loading Window System

Professional startup experience for both the Scribe Engine IDE and distributed games.

### Features

**Tkinter-Based UI:**
- Lightweight, dependency-free implementation
- Custom branding with icon support (.ico and .png)
- Indeterminate progress bar for smooth animation
- Status text updates during startup

**Customization:**
- Game title and subtitle configuration
- Custom icon paths for branded experience
- Centered window positioning
- Professional dark theme styling

**Threading Integration:**
- Runs startup functions in background thread
- Non-blocking UI updates
- Automatic closure when startup completes
- Error handling and reporting

**Usage Pattern:**
```python
from loading_window import LoadingWindow

loading_window = LoadingWindow(
    title="My Game",
    subtitle="Loading...",
    icon_path="/path/to/icon.png"
)

def startup_function():
    # Perform startup tasks
    return True

loading_window.run_with_loading(startup_function)
```

**Integration Points:**
- `gui_launcher.py` - Engine IDE startup
- `game_server_wrapper.py` - Standalone game startup
- `engine/game_installer.py` - Installation progress display

## Code Conventions

- Python 3.12+ required
- **Object-Oriented Game State**: Use direct object access instead of helper functions
- **Natural Python Syntax**: Write standard Python code in `{$ $}` blocks
- **Player Class Auto-Discovery**: Name your player class `Player` in any `.py` file
- **Flat State Structure**: Avoid artificial nesting like `flags` or `variables` dictionaries
- **Sandboxed Execution**: Game logic runs in secure environment with persistent state
- **Web Interface**: Built with HTMX patterns for dynamic updates without heavy JavaScript
- **CSS Organization**: `engine.css` for core UI, `theme.css` for customization

### Game Development Best Practices

**State Management:**
```
:: Example Passage
{$- 
# ✅ Good - Multi-line Python block for complex logic
damage = random.randint(1, 10)
player.health -= damage
met_wizard = True
score += 100

if player.health <= 0:
    game_over = True
-$}

{$ simple_variable = "inline_assignment" $} <!-- ✅ Good - Inline for simple statements -->

Your health: {{player.health}} <!-- Jinja2 renders after Python -->

# ❌ Avoid - Old helper function approach
{$ set_variable('player.health', get_variable('player.health') - damage) $}
{$ set_flag('met_wizard', True) $}
```

**Player Classes:**
```python
# ✅ Good - Clean, discoverable class
class Player:
    def __init__(self, name=""):
        self.name = name
        self.skills = {}
    
    def level_up_skill(self, skill_name):
        self.skills[skill_name] = self.skills.get(skill_name, 0) + 1

# Usage in .tgame files:
:: Skill Training
{$ player.level_up_skill('Combat') $}
You've improved your combat skills! Current level: {{player.skills.Combat}}
```

**Template Integration:**
```html
<!-- ✅ Good - Direct object access -->
<p>Health: {{player.health}}/{{player.max_health}}</p>
<p>Skills: {{player.skills}}</p>

<!-- ✅ Good - Method calls work seamlessly -->
{% if player.skill_check('Hacking', 8) %}
    <p>Hack successful!</p>
{% endif %}
```
