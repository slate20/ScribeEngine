# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**NOTE: This branch (expand-scope) has pivoted to a full-stack web framework focus, dropping game-specific features.**

Scribe Engine is a Python-based full-stack web framework that makes building web applications incredibly simple. It provides:
- An integrated IDE with syntax highlighting, live preview, and debugging
- Template files (.stpl) combining HTML, Jinja2 templating, and inline Python logic
- SQLite database integration with automatic migrations and query builder
- Fast application builds that package standalone executables
- Production-ready deployment with WSGI support (Gunicorn, uWSGI, Waitress)
- Two distribution modes: GUI version (full IDE) and CLI version (minimal runtime)

### Key Features
- **Auto-loading Python modules**: All `.py` files in your project are automatically loaded
- **Inline Python in templates**: Execute Python code directly in your HTML templates
- **Database support**: Built-in SQLite with migrations, raw SQL, and fluent query builder
- **Hot reload**: Instant updates during development with file watching
- **Environment-based config**: Separate development and production modes

## Common Commands

### Development Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Run the GUI version (integrated IDE)
python gui_launcher.py

# Run the CLI version (minimal development server)
python main_engine.py --project-path /path/to/app

# Run with live-reload for development
python main_engine.py --project-path /path/to/app --watch

# Create a new web application project
python main_engine.py --create my-app --project-root /path/to/projects
```

### Building Executables
```bash
# Full rebuild (GUI + CLI versions)
./full_rebuild.sh

# Build GUI version only
python build_engine.py gui

# Build CLI version only
python build_engine.py

# Build the universal application player (ScribePlayer.exe)
python build_player.py

# Production deployment (using Gunicorn example)
SCRIBE_ENV=production SCRIBE_PROJECT_PATH=/path/to/app SCRIBE_SECRET_KEY=your-secret gunicorn -w 4 -b 0.0.0.0:8000 wsgi:application
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
- Initializing SQLite database and running migrations
- Parsing `.stpl` template files and `.py` system files
- Managing application state through StateManager
- Executing Python code safely via SafeExecutor
- Rendering templates with Jinja2 templating

**Database (`engine/database.py`)**: SQLite integration providing:
- Thread-safe connection management
- Automatic migration system tracking applied changes
- Raw SQL queries with parameterization
- Query builder for fluent interface (`.table('users').where(active=True).all()`)
- Connection pooling and transaction support

**GameParser (`engine/parser.py`)**: Parses `.stpl` template files with custom syntax:
- `:: PassageName` - Defines pages/routes (called "passages" internally)
- `{$ python_code $}` - Inline Python statements
- `{$- python_code -$}` - Multi-line Python blocks
- `[[Link Text->TargetPage]]` - Navigation links
- `{{variable}}` - Jinja2 variable interpolation

**SafeExecutor (`engine/executor.py`)**: Executes Python code within application context:
- Maintains isolated namespace for application logic
- Loads custom Python modules from project files
- Provides safe execution environment with restricted access
- Exposes database (`db`) and helper functions to template code

**StateManager (`engine/state.py`)**: Manages application state including:
- Session data and user variables
- Current page tracking
- History and navigation state
- Player data (legacy feature for text-based adventures)

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
- Minimal Flask server for application runtime
- File watcher for live-reload during development
- Project creation via command-line flags
- Used for testing applications with external editors

**game_server.py**: Standalone application runtime
- Minimal server used in distributed application executables
- No IDE features, only application serving
- Loads from embedded/obfuscated archives

**config.py**: Environment and configuration management
- Development vs production mode separation
- Environment variable handling (SCRIBE_ENV, SCRIBE_PROJECT_PATH, SCRIBE_SECRET_KEY)
- Production validation ensuring required settings present

**wsgi.py**: Production WSGI entry point
- Compatible with Gunicorn, uWSGI, Waitress
- Automatic environment-based configuration
- Production mode validation

### Build System

**AssetPacker (`engine/asset_packer.py`)**:
- Packages application projects into obfuscated `.ega` archives
- XOR-based content obfuscation (not cryptographic security)
- Filename obfuscation to prevent casual inspection
- Embeds application data into standalone executables

**GameInstaller (`engine/game_installer.py`)**:
- First-launch installation UI for distributed applications
- Extracts application data from embedded archive
- Manages app_data directory creation
- Tracks installation state and version

**build_engine.py**: Creates Scribe Engine executables
- Bundles Python, Flask, pywebview, and all dependencies
- Creates both GUI and CLI versions via PyInstaller
- Embeds version info and git commit hash
- Platform-specific builds (Windows/Linux/macOS)

**build_player.py**: Creates universal application player (ScribePlayer.exe)
- Standalone executable for running packaged applications
- Loads `.ega` archives containing application data
- Minimal dependencies, optimized for distribution

**project_templates.py**: Project template generator
- `create_webapp_project()`: Creates new web application projects
- Generates complete project structure with migrations, models, static files
- Includes example code demonstrating database usage

### Flask Applications

All three Flask apps (`app.py`, `main_engine.py`, `game_server.py`) share similar structure but different feature sets:

**app.py** (Full IDE):
- Editor routes: File management, syntax highlighting
- Build routes: Packaging applications into executables
- Preview routes: Live application preview panel
- Debug routes: Variable inspection, state management
- Production mode support with environment-based configuration

**main_engine.py** (Development):
- Application serving routes
- File watcher integration
- Debug mode support
- Project creation CLI

**game_server.py** (Distribution):
- Minimal serving routes
- No editor or build features
- Loads from hardcoded embedded config

### Web Application Project Structure

A typical web application project contains:
```
MyApp/
├── project.json          # Configuration (title, database, server)
├── index.stpl           # Main page template
├── *.stpl               # Additional page templates
├── data/                # SQLite database files
│   └── app.db
├── migrations/          # Database migration SQL files
│   ├── 001_initial.sql
│   └── 002_add_table.sql
├── models/              # Python model classes
│   └── user.py
├── static/              # CSS, JS, images
│   └── style.css
├── saves/               # Session/save data (if using server storage)
└── *.py                 # Custom Python modules (auto-loaded)
```

**project.json** keys:
- `title`, `author`: Application metadata
- `starting_passage`: Entry point page name (e.g., "index")
- `project_type`: "webapp" for web applications
- `database.enabled`: Enable SQLite integration
- `database.type`: "sqlite"
- `database.path`: Relative path to database file
- `server.host`, `server.port`: Development server settings
- `server.environment`: "development" or "production"
- `features.use_default_player`: Auto-create player object (legacy)
- `features.save_system`: "server" or "browser"
- `features.hot_reload`: Enable development hot reload
- `nav.enabled`, `nav.position`: Navigation menu config
- `debug_mode`: Enable debug output
- `theme`: CSS theming configuration

## Development Workflow

### Creating a New Project
1. **GUI Method**: Launch GUI (`python gui_launcher.py`)
   - Select project directory
   - Use "Create New Project" button
   - Opens IDE with complete project structure

2. **CLI Method**: Use command-line
   ```bash
   python main_engine.py --create my-app --project-root /path/to/projects
   python main_engine.py --project-path /path/to/projects/my-app --watch
   ```

The created project includes:
- `index.stpl` with example HTML and database queries
- Initial migration (`001_initial.sql`) with sample schema
- Example model class (`models/user.py`)
- Modern CSS styling (`static/style.css`)
- Complete `project.json` configuration

### Testing Changes
- GUI: Live preview updates automatically
- CLI: Use `--watch` flag for auto-reload on file changes

### Building for Distribution
1. Click "Build" in GUI (or run `python build_engine.py`)
2. Application is packaged to `dist/` directory
3. Distribute single executable + `.ega` file (or embedded)

### Deploying to Production
1. **Set environment variables**:
   ```bash
   export SCRIBE_ENV=production
   export SCRIBE_PROJECT_PATH=/var/www/myapp
   export SCRIBE_SECRET_KEY=your-secret-key-here
   ```

2. **Use a production WSGI server**:
   ```bash
   # Gunicorn (recommended)
   gunicorn -w 4 -b 0.0.0.0:8000 wsgi:application

   # uWSGI
   uwsgi --http :8000 --wsgi-file wsgi.py --callable application

   # Waitress (Windows-friendly)
   waitress-serve --port=8000 wsgi:application
   ```

3. **Configure reverse proxy** (Nginx example):
   ```nginx
   location / {
       proxy_pass http://127.0.0.1:8000;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   ```

### Adding Custom Application Logic
Create `.py` files in project directory - they're automatically loaded:
```python
# models/user.py
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def save(self):
        return db.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (self.name, self.email)
        )

    @staticmethod
    def all():
        return db.query("SELECT * FROM users ORDER BY name")

# Accessible in templates as: User.all()
```

### Working with the Database
```python
# In any .stpl template
{$
# Raw SQL queries
users = db.query("SELECT * FROM users WHERE active = ?", (True,))

# Query builder (fluent interface)
users = db.table('users').where(active=True).order_by('name').all()
first_user = db.table('users').where(id=1).first()

# Insert/Update/Delete
user_id = db.execute(
    "INSERT INTO users (name, email) VALUES (?, ?)",
    ("Alice", "alice@example.com")
)

db.execute("UPDATE users SET active = ? WHERE id = ?", (True, user_id))
db.execute("DELETE FROM users WHERE id = ?", (user_id,))

# Commit changes
db.commit()
$}
```

## Key Technical Details

### Template Format (.stpl)
- Python code runs before Jinja2 templating
- Special pages: `NavMenu`, `PrePassage`, `PostPassage`
- Variables in Python scope become Jinja2 context
- Links can be inline (`| inline`) for same-page actions
- Database available as `db` in all Python blocks

### Safe Execution
- Python code runs in restricted namespace
- Access to: `db`, `player`, `game`, `game_state`, `systems`, `random`, `math`, `datetime`, `sqlite3`
- No direct file I/O or network access from template scripts
- Custom modules loaded into isolated namespace
- Database connections are thread-safe with automatic locking

### Live Preview & Hot Reload
- Uses file watcher (`watchdog`) to detect file changes
- Frontend polls `/api/check_reload` for updates
- Application state preserved during hot reload in editor
- Database migrations run automatically on engine restart
- Python module changes require engine restart (automatic in watch mode)

### Build Process
- PyInstaller creates single executable
- Flask app, templates, and static assets bundled
- Application projects remain separate (not bundled)
- Distributed applications include embedded archive

### Database Migrations
- SQL files in `migrations/` directory run automatically on startup
- Files processed in alphabetical order (use numeric prefixes: `001_`, `002_`)
- Applied migrations tracked in `_migrations` table
- Supports multi-statement SQL files
- Use `executescript()` internally for complex migrations

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
