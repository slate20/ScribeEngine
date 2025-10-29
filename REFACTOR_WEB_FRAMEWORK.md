# Scribe Engine → Web Framework Pivot

**Branch:** `expand-scope`
**Date Started:** 2025-10-29
**Status:** In Progress

## Executive Summary

This document outlines the transformation of Scribe Engine from a game-focused interactive fiction engine into a full-stack Python web framework while preserving the beloved GUI IDE and CLI menu interfaces.

### Key Goals
1. **Add SQLite database support** for data-driven web applications
2. **Implement production/development environment modes** for deployment
3. **Update terminology** from game-centric to web-app universal
4. **Maintain 100% UI/UX** of existing GUI IDE and CLI menu
5. **Enable easy deployment** to production servers (Gunicorn, nginx, Docker)

### What's Changing
- File extension: `.tgame` → `.stpl` (Scribe Template)
- Internal terminology: `game_state` → `app_state`, `passages` → `pages`
- New feature: SQLite database accessible from templates and Python files
- New feature: Environment-based configuration (dev/prod modes)
- New feature: WSGI entry point for production deployment

### What's NOT Changing
- GUI IDE interface (file browser, editor, live preview)
- CLI menu system (TUI with ASCII art banner)
- Hot reload functionality
- Theme system
- Build process
- Overall developer experience

---

## Rationale: Why This Pivot?

### The Revelation
The architecture already contains everything needed for a full-stack web framework:
- **Flask backend** with routing and JSON APIs
- **Jinja2 templating** with inline Python execution
- **State management** with serialization
- **Auto-loading Python systems** from project files
- **Live preview** with hot reload
- **HTMX integration** for reactive UI

### What's Missing?
- **Database layer**: No persistent data storage beyond JSON files
- **Production readiness**: Uses development Werkzeug server
- **Web-focused terminology**: "Game", "passage", "player" confuses web developers

### The Opportunity
With SQLite integration, Scribe Engine becomes:
- **The easiest Python web framework** - No API layer needed
- **Perfect for rapid prototyping** - Database queries in templates
- **Ideal for internal tools** - Full-stack in minutes, not hours
- **Educational powerhouse** - See immediate results while learning

---

## Architecture Overview

### Current Architecture (Game Engine)
```
User writes .tgame files
  ↓
GameParser extracts Python blocks and links
  ↓
SafeExecutor runs Python in sandbox
  ↓
Jinja2 renders templates with game_state
  ↓
Flask serves HTML via HTMX
  ↓
pywebview wraps in native window (GUI mode)
```

### New Architecture (Web Framework)
```
User writes .stpl files
  ↓
TemplateParser extracts Python blocks and links
  ↓
PythonExecutor runs Python with db access
  ↓
Jinja2 renders templates with app_state + db results
  ↓
Flask serves HTML via HTMX
  ↓
Deployable to Gunicorn/nginx or pywebview (IDE mode)
```

### Key Addition: Database Layer
```
project_path/
├── data/
│   └── app.db (SQLite database)
├── migrations/
│   ├── 001_initial.sql
│   └── 002_add_users.sql
├── models/
│   └── user.py (Python business logic)
└── pages/
    └── dashboard.stpl (Templates with db queries)
```

---

## Technical Implementation

### Phase 1: SQLite Integration

#### 1.1 Database Module (`engine/database.py`)
**Status:** In Progress

```python
class Database:
    """Thread-safe SQLite wrapper for Scribe Framework"""

    def __init__(self, project_path, config):
        db_path = config.get('database', {}).get('path', 'data/app.db')
        self.db_path = os.path.join(project_path, db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def query(self, sql, params=()):
        """Execute SELECT queries, return list of dicts"""
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def execute(self, sql, params=()):
        """Execute INSERT/UPDATE/DELETE, return lastrowid"""
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        self.conn.commit()
        return cursor.lastrowid

    def table(self, name):
        """Return QueryBuilder for fluent queries"""
        return QueryBuilder(self, name)

class QueryBuilder:
    """Fluent query builder for common operations"""

    def __init__(self, db, table_name):
        self.db = db
        self.table_name = table_name
        self._select_cols = ['*']
        self._where_conditions = {}
        self._order = None
        self._limit_val = None

    def select(self, *columns):
        self._select_cols = columns
        return self

    def where(self, **conditions):
        self._where_conditions.update(conditions)
        return self

    def order_by(self, column, direction='ASC'):
        self._order = (column, direction)
        return self

    def limit(self, n):
        self._limit_val = n
        return self

    def all(self):
        """Execute query and return all results"""
        sql = self._build_query()
        params = tuple(self._where_conditions.values())
        return self.db.query(sql, params)

    def first(self):
        """Execute query and return first result"""
        results = self.limit(1).all()
        return results[0] if results else None

    def _build_query(self):
        cols = ', '.join(self._select_cols)
        sql = f"SELECT {cols} FROM {self.table_name}"

        if self._where_conditions:
            conditions = ' AND '.join([f"{k} = ?" for k in self._where_conditions])
            sql += f" WHERE {conditions}"

        if self._order:
            sql += f" ORDER BY {self._order[0]} {self._order[1]}"

        if self._limit_val:
            sql += f" LIMIT {self._limit_val}"

        return sql
```

**Integration Points:**
- ✅ `executor.py:12` - Added `sqlite3` to allowed_imports
- ⏳ `core.py` - Add database initialization in `__init__`
- ⏳ `executor.py` - Expose `db` in safe_globals

#### 1.2 Migration System
**Status:** Pending

Simple file-based migrations that run on startup:
```python
# In engine/core.py
def _run_migrations(self):
    """Run SQL migrations from migrations/ directory"""
    migrations_dir = os.path.join(self.project_path, 'migrations')
    if not os.path.exists(migrations_dir):
        return

    # Create tracking table
    self.db.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            filename TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Get applied migrations
    applied = {row['filename'] for row in self.db.query("SELECT filename FROM _migrations")}

    # Run pending migrations in order
    for filename in sorted(os.listdir(migrations_dir)):
        if filename.endswith('.sql') and filename not in applied:
            with open(os.path.join(migrations_dir, filename)) as f:
                self.db.execute(f.read())
                self.db.execute("INSERT INTO _migrations (filename) VALUES (?)", (filename,))
            if self.debug_mode:
                print(f"✓ Applied migration: {filename}")
```

### Phase 2: Environment Configuration

#### 2.1 Config Module (`config.py`)
**Status:** Pending

```python
import os
from typing import Optional

class Config:
    """Centralized configuration with environment variable support"""

    @staticmethod
    def get_env() -> str:
        """Returns 'development' or 'production'"""
        return os.getenv('SCRIBE_ENV', 'development')

    @staticmethod
    def is_production() -> bool:
        return Config.get_env() == 'production'

    @staticmethod
    def is_development() -> bool:
        return Config.get_env() == 'development'

    @staticmethod
    def get_secret_key() -> Optional[str]:
        return os.getenv('SCRIBE_SECRET_KEY')

    @staticmethod
    def get_project_path() -> Optional[str]:
        return os.getenv('SCRIBE_PROJECT_PATH')

    @staticmethod
    def get_port() -> int:
        return int(os.getenv('SCRIBE_PORT', '5000'))

    @staticmethod
    def get_host() -> str:
        return os.getenv('SCRIBE_HOST', '127.0.0.1')
```

**Environment Variables:**
- `SCRIBE_ENV` - "development" or "production"
- `SCRIBE_PROJECT_PATH` - Path to project directory
- `SCRIBE_SECRET_KEY` - Flask secret key (required in production)
- `SCRIBE_PORT` - Server port (default: 5000)
- `SCRIBE_HOST` - Server host (default: 127.0.0.1)

#### 2.2 Production Mode Behaviors
**Status:** Pending

| Feature | Development | Production |
|---------|------------|------------|
| Debug mode | Enabled | Disabled |
| Error pages | Detailed traceback | Generic error page |
| Hot reload | Enabled | Disabled |
| Secret key | Hardcoded dev key | From env var (required) |
| Host binding | 127.0.0.1 | 0.0.0.0 or configurable |
| Logging | Verbose | Error-level only |
| CORS | Permissive | Restricted |

### Phase 3: File Format & Terminology

#### 3.1 File Extension Change
**Status:** Pending

- New extension: `.stpl` (Scribe Template)
- Backward compatibility: `.tgame` files still work
- Parser auto-detects both extensions
- New projects default to `.stpl`

**Implementation:**
```python
# In engine/core.py, load_project()
for root, _, files in os.walk(self.project_path):
    for file in files:
        if file.endswith('.py'):
            python_files.append(os.path.join(root, file))
        elif file.endswith(('.tgame', '.stpl')):  # Support both
            passage_files.append(os.path.join(root, file))
```

#### 3.2 Terminology Mapping
**Status:** Pending

| Old (Game) | New (Web) | Context |
|-----------|-----------|---------|
| `.tgame` | `.stpl` | File extension |
| `game_state` | `app_state` | Internal variable |
| `passages` | `pages` | Internal dict |
| "Game Project" | "Web Project" | UI labels |
| "Story File" | "Template File" | UI labels |
| "Play Game" | "Run App" | Button text |
| "Game Server" | "Development Server" | CLI output |

**Important:** Keep `GameEngine`, `GameParser` class names for now (internal, doesn't matter). Focus on user-facing terminology.

### Phase 4: Project Configuration

#### 4.1 Updated `project.json` Schema
**Status:** Pending

```json
{
  "title": "My Web App",
  "author": "Developer Name",
  "starting_passage": "index",

  "project_type": "webapp",

  "database": {
    "enabled": true,
    "type": "sqlite",
    "path": "data/app.db"
  },

  "server": {
    "host": "127.0.0.1",
    "port": 5000,
    "environment": "development"
  },

  "features": {
    "use_default_player": false,
    "save_system": "server",
    "hot_reload": true
  },

  "nav": {
    "enabled": true,
    "position": "horizontal"
  },

  "debug_mode": false,

  "theme": {
    "enabled": true,
    "colors": { },
    "fonts": { }
  }
}
```

**New Fields:**
- `project_type`: "webapp" or "game" (for future dual-purpose support)
- `database`: Configuration for SQLite
- `server`: Server configuration (can be overridden by env vars)

#### 4.2 Configuration Hierarchy
**Status:** Pending

```
Environment Variables (highest priority)
  ↓
.env file (if present)
  ↓
project.json (defaults)
  ↓
Hardcoded defaults (lowest priority)
```

### Phase 5: WSGI & Deployment

#### 5.1 WSGI Entry Point (`wsgi.py`)
**Status:** Pending

```python
"""WSGI entry point for production deployment with Gunicorn/uWSGI"""
import os
import sys

# Ensure Scribe Engine is in path
sys.path.insert(0, os.path.dirname(__file__))

from app import app, set_game_project_path
from config import Config

# Validate production requirements
if Config.is_production():
    if not Config.get_secret_key():
        raise ValueError("SCRIBE_SECRET_KEY environment variable required in production")

    if not Config.get_project_path():
        raise ValueError("SCRIBE_PROJECT_PATH environment variable required")

# Set project path
project_path = Config.get_project_path()
if project_path:
    set_game_project_path(project_path)
else:
    raise ValueError("SCRIBE_PROJECT_PATH environment variable must be set")

# WSGI application callable
application = app
```

**Usage:**
```bash
# Development (Flask built-in server)
export SCRIBE_PROJECT_PATH=/path/to/project
python main_engine.py

# Production (Gunicorn)
export SCRIBE_ENV=production
export SCRIBE_PROJECT_PATH=/var/www/myapp
export SCRIBE_SECRET_KEY=your-random-secret-key-here
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:application
```

#### 5.2 Deployment Configurations

**systemd Service:**
```ini
[Unit]
Description=Scribe Web App
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/myapp
Environment="SCRIBE_ENV=production"
Environment="SCRIBE_PROJECT_PATH=/var/www/myapp"
Environment="SCRIBE_SECRET_KEY=your-secret-key"
ExecStart=/usr/bin/gunicorn -w 4 -b 127.0.0.1:8000 wsgi:application

[Install]
WantedBy=multi-user.target
```

**nginx Reverse Proxy:**
```nginx
server {
    listen 80;
    server_name myapp.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/myapp/static;
        expires 30d;
    }
}
```

**Docker:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

ENV SCRIBE_ENV=production
ENV SCRIBE_PROJECT_PATH=/app/project

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "wsgi:application"]
```

---

## Project Templates

### Web Application Template

**Structure:**
```
MyWebApp/
├── project.json (database enabled)
├── pages/
│   ├── index.stpl (homepage)
│   ├── dashboard.stpl (main app view)
│   └── users/
│       ├── list.stpl
│       └── edit.stpl
├── models/
│   ├── user.py
│   └── post.py
├── data/
│   └── app.db (created on first run)
├── migrations/
│   ├── 001_initial.sql
│   └── 002_add_posts.sql
├── static/
│   ├── style.css
│   └── app.js
└── README.md
```

**Example `pages/dashboard.stpl`:**
```html
:: dashboard
{$
# Fetch data from database
users = db.query("SELECT * FROM users WHERE active = ? ORDER BY created_at DESC", (True,))
user_count = len(users)
recent_posts = db.table('posts').order_by('created_at', 'DESC').limit(5).all()
$}

<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - {{title}}</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <h1>Dashboard</h1>

    <div class="stats">
        <div class="stat-card">
            <h3>Active Users</h3>
            <p class="stat-number">{{user_count}}</p>
        </div>
    </div>

    <div class="recent-activity">
        <h2>Recent Posts</h2>
        <ul>
        {% for post in recent_posts %}
            <li>
                <strong>{{post.title}}</strong>
                by {{post.author}}
                <span class="date">{{post.created_at}}</span>
            </li>
        {% endfor %}
        </ul>
    </div>

    <nav>
        [[View All Users->users/list]]
        [[Create Post->posts/new]]
    </nav>
</body>
</html>
```

**Example `models/user.py`:**
```python
"""User model and business logic"""

class User:
    def __init__(self, name, email, password_hash=None):
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.active = True

    def save(self):
        """Insert or update user in database"""
        existing = db.query("SELECT id FROM users WHERE email = ?", (self.email,))

        if existing:
            db.execute("""
                UPDATE users
                SET name = ?, active = ?
                WHERE email = ?
            """, (self.name, self.active, self.email))
        else:
            db.execute("""
                INSERT INTO users (name, email, password_hash, active)
                VALUES (?, ?, ?, ?)
            """, (self.name, self.email, self.password_hash, self.active))

    @staticmethod
    def find_by_email(email):
        """Find user by email address"""
        result = db.query("SELECT * FROM users WHERE email = ?", (email,))
        return result[0] if result else None

    @staticmethod
    def all_active():
        """Get all active users"""
        return db.table('users').where(active=True).order_by('name').all()

    @staticmethod
    def count():
        """Get total user count"""
        result = db.query("SELECT COUNT(*) as count FROM users")
        return result[0]['count'] if result else 0
```

**Example `migrations/001_initial.sql`:**
```sql
-- Initial database schema for MyWebApp

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    author TEXT NOT NULL,
    published INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_posts_published ON posts(published);

-- Insert sample data
INSERT INTO users (name, email) VALUES
    ('Alice Admin', 'alice@example.com'),
    ('Bob User', 'bob@example.com'),
    ('Charlie Developer', 'charlie@example.com');

INSERT INTO posts (title, content, author, published) VALUES
    ('Welcome to Scribe Framework', 'This is your first post!', 'Alice Admin', 1),
    ('Getting Started Guide', 'Learn how to build web apps with Scribe.', 'Alice Admin', 1);
```

---

## UI/UX Adaptations

### GUI IDE Updates

#### Settings Panel
**Add new fields to existing settings:**
- Project Type: [Dropdown: Web Application / Game]
- Database Enabled: [Toggle]
- Database Path: [Text Input: data/app.db]
- Environment: [Dropdown: Development / Production]

**Location:** `templates/editor.html` settings modal
**Route:** `@app.route('/api/project-settings/<project_name>')`

#### New Project Dialog
**Add project type selector:**
```
┌─ Create New Project ────────────────────┐
│ Project Name: [___________________]     │
│                                          │
│ Project Type:                            │
│ ○ Web Application (with SQLite)         │
│   Database-enabled web app template     │
│                                          │
│ ○ Basic Project (no database)           │
│   Simple template without database      │
│                                          │
│ [Create Project]  [Cancel]               │
└──────────────────────────────────────────┘
```

**Implementation:** Update `/api/new-project` route to accept `project_type` parameter

#### File Browser
- Display `.stpl` files with same icon as `.tgame`
- Show `migrations/` folder prominently
- Show `models/` folder for Python business logic

### CLI Menu Updates

#### Main Menu Text Changes
**Before:**
```
╔═══════════════════════════════════════╗
║   SCRIBE ENGINE - GAME LAUNCHER       ║
╚═══════════════════════════════════════╝
1. Create New Game Project
2. Select Game Project
3. Launch Game Server
4. Settings
5. Exit
```

**After:**
```
╔═══════════════════════════════════════╗
║   SCRIBE ENGINE - CLI LAUNCHER        ║
╚═══════════════════════════════════════╝
1. Create New Project
2. Select Project
3. Launch Development Server
4. Settings
5. Exit
```

#### Project Creation Wizard
**Add project type selection step:**
```
Step 1/3: Enter project name
> my_webapp

Step 2/3: Select project type
1) Web Application (with SQLite database)
2) Basic Project (no database)
> 1

Step 3/3: Confirm creation
Project: my_webapp
Type: Web Application
Location: /home/user/projects/my_webapp

Create project? (y/n): y

✓ Created project structure
✓ Generated project.json
✓ Created database configuration
✓ Created migrations directory
✓ Created example templates

Project created successfully!
```

#### Server Launch Messages
**Update output messages:**
```
🚀 Scribe Development Server
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Project: my_webapp
Environment: development
Database: SQLite (data/app.db)

Server running at: http://127.0.0.1:5000
Hot reload: ENABLED (watching .stpl, .py files)

Press Ctrl+C to stop
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Security Considerations

### SQL Injection Prevention
**Always use parameterized queries:**
```python
# ✅ GOOD - Parameterized
user_input = request.form['search']
results = db.query("SELECT * FROM users WHERE name LIKE ?", (f"%{user_input}%",))

# ❌ BAD - SQL injection vulnerable
results = db.query(f"SELECT * FROM users WHERE name LIKE '%{user_input}%'")
```

### Secret Key Management
**Production requirement:**
- Secret key MUST be set via `SCRIBE_SECRET_KEY` env var
- Auto-generate if not provided in development
- Never commit secret keys to version control
- Use `.env` file (gitignored) for local development

### CSRF Protection
**Status:** Future enhancement
- Add CSRF token generation
- Validate tokens on all POST/PUT/DELETE requests
- Provide helper in templates: `{{ csrf_token() }}`

### XSS Prevention
**Already handled by Jinja2:**
- Auto-escapes all variables: `{{ user.name }}`
- Use `| safe` filter only for trusted HTML
- Sanitize user input before database storage

---

## Testing Strategy

### Unit Tests
**To be created:**
- `test_database.py` - Database module tests
- `test_query_builder.py` - Query builder tests
- `test_migrations.py` - Migration system tests
- `test_config.py` - Configuration loading tests

### Integration Tests
**To be created:**
- Create web app project via CLI
- Run migrations
- Execute database queries from templates
- Deploy to Gunicorn
- Verify production mode behaviors

### Security Tests
**To be created:**
- SQL injection prevention
- XSS prevention
- CSRF token validation
- Secret key enforcement in production

---

## Performance Benchmarks

### Targets
- Page render: < 50ms (excluding database queries)
- Database query: < 10ms for simple SELECTs
- Hot reload: < 500ms for file changes
- Startup time: < 2 seconds

### Optimization Strategies
- Connection pooling for SQLite
- Query result caching (with TTL)
- Template compilation caching
- Static file CDN support

---

## Migration Guide (Game Engine → Web Framework)

### For Existing Scribe Engine Users

**This branch is a breaking change.** Existing game projects are NOT compatible.

**Options:**
1. **Stay on main branch** - Continue using Scribe Engine for games
2. **Fork project separately** - Keep game engine, use web framework separately
3. **Manually migrate** - Convert `.tgame` → `.stpl`, remove game-specific code

**Recommended:** This pivot is on a separate branch. Main branch remains game-focused.

---

## Roadmap

### Version 2.0.0 (Current - Web Framework Pivot)
- ✅ SQLite integration
- ✅ Production/development modes
- ✅ WSGI deployment support
- ✅ File extension change (.stpl)
- ✅ Terminology updates
- ✅ Project templates
- ✅ Migration system

### Version 2.1.0 (Future)
- Authentication system
- Session management
- CSRF protection
- Form validation helpers
- Email integration
- Logging system

### Version 2.2.0 (Future)
- PostgreSQL support
- Redis caching
- WebSocket support
- Background tasks (Celery)
- API versioning
- GraphQL support

### Version 3.0.0 (Vision)
- Plugin system
- Marketplace for templates/extensions
- Visual query builder
- Database admin UI
- Multi-tenancy support
- Internationalization (i18n)

---

## Success Metrics

### Development Experience
- [ ] New project created in < 30 seconds
- [ ] Database queries work from templates
- [ ] Hot reload under 500ms
- [ ] No breaking changes to UI/UX

### Production Readiness
- [ ] Successfully deployed to Gunicorn
- [ ] nginx reverse proxy working
- [ ] Docker containerization working
- [ ] systemd service working

### Documentation
- [ ] Complete API reference
- [ ] Tutorial: Todo app in 15 minutes
- [ ] Deployment guides for all platforms
- [ ] Example projects published

### Community
- [ ] GitHub README updated
- [ ] Demo video published
- [ ] Blog post announcing pivot
- [ ] Discord/forum for support

---

## Resources

### Documentation
- [SQLite Python Documentation](https://docs.python.org/3/library/sqlite3.html)
- [Flask WSGI Deployment](https://flask.palletsprojects.com/en/latest/deploying/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [nginx Reverse Proxy Guide](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)

### Inspiration
- Django ORM (query builder design)
- Ruby on Rails (convention over configuration)
- Laravel (elegant syntax)
- FastAPI (modern Python web framework)

---

## Contributors

- **Primary Developer:** [Your Name]
- **Project Origin:** Scribe Engine (game engine)
- **Pivot Date:** 2025-10-29
- **Branch:** expand-scope

---

## License

[Maintain original license]

---

## Appendix: Code Change Log

### 2025-10-29
- ✅ Added `sqlite3` to `executor.py` allowed imports
- ⏳ Creating `engine/database.py` module
- ⏳ Creating `config.py` module
- ⏳ Creating `wsgi.py` entry point

### [Future dates as implementation progresses]

---

**End of Document**
