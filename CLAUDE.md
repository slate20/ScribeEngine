# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Scribe Engine is a text-based game engine for creating interactive stories and visual novels. It provides:
- An integrated IDE with syntax highlighting, live preview, and debugging
- A custom story format (.tgame files) combining Python logic with Jinja2 templating
- Fast game builds (5-15 seconds) that package standalone executables
- Two distribution modes: GUI version (full IDE) and CLI version (minimal runtime)

## Common Commands

### Development Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Run the GUI version (integrated IDE)
python gui_launcher.py

# Run the CLI version (minimal game server)
python main_engine.py --project-path /path/to/game

# Run with live-reload for development
python main_engine.py --project-path /path/to/game --watch
```

### Building Executables
```bash
# Full rebuild (GUI + CLI versions)
./full_rebuild.sh

# Build GUI version only
python build_engine.py gui

# Build CLI version only
python build_engine.py

# Build the universal game player (ScribePlayer.exe)
python build_player.py
```

### Version Management
```bash
# Update version number and metadata
python set_version.py <major.minor.patch>
```

## Architecture

### Core Components

**GameEngine (`engine/core.py`)**: Central engine that orchestrates:
- Loading project configuration from `project.json`
- Parsing `.tgame` story files and `.py` system files
- Managing game state through StateManager
- Executing Python code safely via SafeExecutor
- Rendering passages with Jinja2 templating

**GameParser (`engine/parser.py`)**: Parses `.tgame` files with custom syntax:
- `:: PassageName` - Defines passages (story segments)
- `{$ python_code $}` - Inline Python statements
- `{$- python_code -$}` - Multi-line Python blocks
- `[[Link Text->TargetPassage]]` - Navigation links
- `{{variable}}` - Jinja2 variable interpolation

**SafeExecutor (`engine/executor.py`)**: Executes Python code within game context:
- Maintains isolated namespace for game logic
- Loads custom Python systems from project files
- Provides safe execution environment with restricted access

**StateManager (`engine/state.py`)**: Manages game state including:
- Player data (inventory, stats, variables)
- Current passage tracking
- History and navigation state

**Storage Systems** (`engine/storage.py`, `engine/browser_storage.py`):
- JSONStorage: Server-side save files
- BrowserStorage: Client-side localStorage via JavaScript bridge

### Application Entry Points

**gui_launcher.py**: GUI mode with integrated IDE
- Uses pywebview for native window management
- Serves Flask app (`app.py`) with full editor features
- Manages project selection and configuration via `config_manager.py`
- Provides visual project management and one-click builds

**main_engine.py**: CLI mode for developers
- Minimal Flask server for game runtime
- File watcher for live-reload during development
- Used for testing games with external editors

**game_server.py**: Standalone game runtime
- Minimal server used in distributed game executables
- No IDE features, only game playback
- Loads from embedded/obfuscated archives

### Build System

**AssetPacker (`engine/asset_packer.py`)**:
- Packages game projects into obfuscated `.ega` archives
- XOR-based content obfuscation (not cryptographic security)
- Filename obfuscation to prevent casual inspection
- Embeds game data into standalone executables

**GameInstaller (`engine/game_installer.py`)**:
- First-launch installation UI for distributed games
- Extracts game data from embedded archive
- Manages game_data directory creation
- Tracks installation state and version

**build_engine.py**: Creates Scribe Engine executables
- Bundles Python, Flask, pywebview, and all dependencies
- Creates both GUI and CLI versions via PyInstaller
- Embeds version info and git commit hash
- Platform-specific builds (Windows/Linux/macOS)

**build_player.py**: Creates universal game player (ScribePlayer.exe)
- Standalone executable for running packaged games
- Loads `.ega` archives containing game data
- Minimal dependencies, optimized for distribution

### Flask Applications

All three Flask apps (`app.py`, `main_engine.py`, `game_server.py`) share similar structure but different feature sets:

**app.py** (Full IDE):
- Editor routes: File management, syntax highlighting
- Build routes: Packaging games into executables
- Preview routes: Live game preview panel
- Debug routes: Variable inspection, state management

**main_engine.py** (Development):
- Game playback routes only
- File watcher integration
- Debug mode support

**game_server.py** (Distribution):
- Minimal playback routes
- No editor or build features
- Loads from hardcoded embedded config

### Game Project Structure

A typical game project contains:
```
MyGame/
├── project.json          # Configuration (title, author, features)
├── story.tgame          # Main story passages
├── assets/              # Images, audio, other media
│   └── game_theme.css   # Custom game styling
├── saves/               # Save files (if using server storage)
└── *.py                 # Optional custom Python systems
```

**project.json** keys:
- `title`, `author`: Game metadata
- `starting_passage`: Entry point passage name
- `icon_path`: Game icon for builds
- `features.use_default_player`: Auto-create player object
- `features.save_system`: "server" or "browser"
- `nav.enabled`, `nav.position`: Navigation menu config
- `debug_mode`: Enable debug output

## Development Workflow

### Creating a New Project
1. Launch GUI (`python gui_launcher.py`)
2. Select project directory
3. Use "Create New Project" button
4. Edit `story.tgame` with live preview

### Testing Changes
- GUI: Live preview updates automatically
- CLI: Use `--watch` flag for auto-reload on file changes

### Building for Distribution
1. Click "Build" in GUI (or run `python build_engine.py`)
2. Game is packaged to `dist/` directory
3. Distribute single executable + `.ega` file (or embedded)

### Adding Custom Game Logic
Create `.py` files in project directory with game systems:
```python
# my_combat_system.py
class Combat:
    def attack(self, target, damage):
        target.health -= damage
        return f"Dealt {damage} damage!"

# Accessible in story as: player_systems.combat.attack(enemy, 10)
```

## Key Technical Details

### Story Format (.tgame)
- Python code runs before Jinja2 templating
- Special passages: `NavMenu`, `PrePassage`, `PostPassage`
- Variables in Python scope become Jinja2 context
- Links can be inline (`| inline`) for same-page actions

### Safe Execution
- Python code runs in restricted namespace
- Access to: `player`, `game`, `game_state`, `systems`, `random`, `math`, `datetime`
- No direct file I/O or network access from game scripts
- Custom systems loaded into isolated namespace

### Live Preview
- Uses file watcher (`watchdog`) to detect changes
- Frontend polls `/api/check_reload` for updates
- Game state preserved during hot reload in editor

### Build Process
- PyInstaller creates single executable
- Flask app, templates, and static assets bundled
- Game projects remain separate (not bundled)
- Distributed games include embedded archive

## Configuration

**config_manager.py**: Manages persistent settings in:
- Windows: `%APPDATA%/ScribeEngine/config.json`
- Linux/Mac: `~/.config/scribe_engine/config.json`

Stores:
- Last project root directory
- Update check preferences
- Window state (planned)

## Update System

**update_checker.py**: Checks GitHub releases for new versions
- Configurable check frequency (daily/weekly/startup)
- Version comparison and skip tracking
- GUI update notifications via `LoadingWindow`

## Important Notes

- Virtual environment (`venv/`) contains all dependencies - activate before development
- Git branch structure: `development` for active work (check git status for current branch)
- Windows compatibility: Handle encoding explicitly (UTF-8, UTF-8-SIG, CP1252)
- PyInstaller builds are platform-specific - build on target OS
- `.ega` files are obfuscated, not encrypted - not for sensitive data
