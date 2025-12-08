# ScribeEngine Architecture

This document provides a complete technical architecture specification for implementing ScribeEngine from scratch.

---

## System Overview

ScribeEngine is a **template-driven web framework** that:
1. Parses `.stpl` (Scribe Template) files
2. Extracts route definitions and Python code blocks
3. Generates Flask routes dynamically
4. Executes Python code in a controlled context
5. Renders Jinja2 templates
6. Provides database abstraction layer

---

## Component Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                         ScribeEngine Core                          │
├───────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌────────────────┐                                               │
│  │  CLI Interface │  (scribe new, scribe dev, scribe build)      │
│  └───────┬────────┘                                               │
│          │                                                         │
│          ▼                                                         │
│  ┌────────────────┐                                               │
│  │ Project Loader │  Read scribe.json, discover .stpl files      │
│  └───────┬────────┘                                               │
│          │                                                         │
│          ▼                                                         │
│  ┌────────────────────────────────────────────────────────┐      │
│  │              Template Processing Pipeline               │      │
│  │                                                         │      │
│  │  ┌──────────────┐    ┌──────────────┐    ┌─────────┐ │      │
│  │  │   Lexer      │───▶│   Parser     │───▶│  AST    │ │      │
│  │  │              │    │              │    │         │ │      │
│  │  │ Tokenize     │    │ Build syntax │    │ Route   │ │      │
│  │  │ .stpl files  │    │ tree         │    │ tree    │ │      │
│  │  └──────────────┘    └──────────────┘    └────┬────┘ │      │
│  └──────────────────────────────────────────────┼────────┘      │
│                                                  │                │
│                                                  ▼                │
│  ┌────────────────────────────────────────────────────────┐      │
│  │              Flask Route Generator                      │      │
│  │                                                         │      │
│  │  For each route in AST:                                │      │
│  │    1. Create Flask route decorator                     │      │
│  │    2. Create handler function                          │      │
│  │    3. Register with Flask app                          │      │
│  └────────────────────────┬───────────────────────────────┘      │
│                            │                                      │
│                            ▼                                      │
│  ┌────────────────────────────────────────────────────────┐      │
│  │              Request Handler (per route)                │      │
│  │                                                         │      │
│  │  On HTTP Request:                                      │      │
│  │    1. Create execution context                         │      │
│  │    2. Execute Python code block                        │      │
│  │    3. Build Jinja2 context                             │      │
│  │    4. Render Jinja2 template                           │      │
│  │    5. Return HTTP response                             │      │
│  └────────────────────────┬───────────────────────────────┘      │
│                            │                                      │
│                            ▼                                      │
│  ┌────────────────────────────────────────────────────────┐      │
│  │           Execution Context (Sandboxed)                 │      │
│  │                                                         │      │
│  │  Available to Python code:                             │      │
│  │    • db (database abstraction)                         │      │
│  │    • session (Flask session)                           │      │
│  │    • request (Flask request)                           │      │
│  │    • Auto-loaded modules from lib/                     │      │
│  │    • Helper functions (auth, redirect, etc.)           │      │
│  │    • Safe builtins (no file I/O, no system calls)      │      │
│  └────────────────────────┬───────────────────────────────┘      │
│                            │                                      │
└────────────────────────────┼──────────────────────────────────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │   Database   │  │    Flask     │  │   Jinja2     │
    │  Abstraction │  │   Session    │  │   Engine     │
    │              │  │              │  │              │
    │ • SQLite     │  │ • Cookie     │  │ • Template   │
    │ • PostgreSQL │  │ • Secure     │  │   rendering  │
    │ • MySQL      │  │ • CSRF       │  │ • Auto-escape│
    │ • MSSQL      │  │              │  │              │
    └──────┬───────┘  └──────────────┘  └──────────────┘
           │
           ▼
    ┌──────────────┐
    │   Physical   │
    │   Database   │
    └──────────────┘
```

---

## Core Components

### 1. **Template Lexer**

**Responsibility:** Convert raw `.stpl` file content into tokens.

**Input:** Raw file string
```python
@route('/home')
{$
name = "World"
$}
<h1>Hello {{ name }}</h1>
```

**Output:** Token stream
```python
[
    Token(type='ROUTE_DECORATOR', value='@route', args=['/home']),
    Token(type='PYTHON_BLOCK_START', value='{$'),
    Token(type='PYTHON_CODE', value='name = "World"\n'),
    Token(type='PYTHON_BLOCK_END', value='$}'),
    Token(type='HTML', value='<h1>Hello {{ name }}</h1>')
]
```

**Implementation:** See [06_TEMPLATE_PARSER.md](06_TEMPLATE_PARSER.md)

---

### 2. **Template Parser**

**Responsibility:** Build Abstract Syntax Tree (AST) from tokens.

**Input:** Token stream
**Output:** Route AST

```python
Route(
    path='/home',
    methods=['GET'],
    decorators=[],
    python_code='name = "World"\n',
    template='<h1>Hello {{ name }}</h1>',
    line_number=1
)
```

**Implementation:** See [06_TEMPLATE_PARSER.md](06_TEMPLATE_PARSER.md)

---

### 3. **Flask Route Generator**

**Responsibility:** Convert Route AST into Flask route handlers.

**Input:** Route AST
**Output:** Flask route registration

**Pseudocode:**
```python
def generate_flask_route(route_ast, app):
    """Generate and register Flask route from AST"""

    def handler():
        # 1. Create execution context
        context = ExecutionContext(
            db=get_database(),
            session=flask.session,
            request=flask.request,
            helpers=load_helpers()
        )

        # 2. Execute Python code block
        context.execute(route_ast.python_code)

        # 3. Build Jinja2 context from execution results
        template_context = context.get_variables()

        # 4. Render Jinja2 template
        html = render_jinja2(route_ast.template, template_context)

        # 5. Return response
        return html

    # Register with Flask
    app.route(
        route_ast.path,
        methods=route_ast.methods,
        endpoint=f"route_{route_ast.name}"
    )(handler)
```

**Implementation:** See [10_FLASK_INTEGRATION.md](10_FLASK_INTEGRATION.md)

---

### 4. **Execution Context**

**Responsibility:** Provide controlled Python execution environment.

**Features:**
- Sandboxed execution (no unsafe operations)
- Pre-loaded helpers and modules
- Variable isolation between requests
- State management

**Available Objects:**

| Object | Type | Description |
|--------|------|-------------|
| `db` | DatabaseAdapter | Database operations |
| `session` | Flask session proxy | User session data |
| `request` | Flask request proxy | Current HTTP request |
| `auth` | AuthHelper | Authentication helpers |
| `redirect()` | Function | HTTP redirect helper |
| `abort()` | Function | HTTP error responses |
| `csrf()` | Function | CSRF token generation |
| `flash()` | Function | Flash messages |
| Auto-loaded modules | Various | From `lib/*.py` |

**Security:**
- **Allowed:** Basic Python (loops, conditionals, functions)
- **Allowed:** String, list, dict operations
- **Allowed:** Database queries via `db` object
- **Blocked:** File I/O (`open()`, `read()`, `write()`)
- **Blocked:** Network operations (`socket`, `urllib`)
- **Blocked:** System calls (`os.system()`, `subprocess`)
- **Blocked:** Importing arbitrary modules

**Implementation:** See [07_EXECUTION_CONTEXT.md](07_EXECUTION_CONTEXT.md)

---

### 5. **Database Adapter**

**Responsibility:** Provide unified interface to multiple database backends.

**Supported Databases:**
- SQLite (default, built-in)
- PostgreSQL (via psycopg2 + SQLAlchemy)
- MySQL (via mysqlclient + SQLAlchemy)
- MSSQL (via pymssql + SQLAlchemy)

**API Surface:**

```python
class DatabaseAdapter:
    # Query operations
    def query(self, sql, params=None) -> List[Row]
    def execute(self, sql, params=None) -> int  # Returns affected rows
    def commit(self)
    def rollback(self)

    # Convenience methods
    def find(self, table, id) -> Row
    def where(self, table, **conditions) -> List[Row]
    def insert(self, table, **values) -> int  # Returns new ID
    def update(self, table, values, **conditions) -> int
    def delete(self, table, **conditions) -> int

    # Query builder (fluent interface)
    def table(self, name) -> QueryBuilder
```

**Implementation:** See [08_DATABASE_ABSTRACTION.md](08_DATABASE_ABSTRACTION.md)

---

### 6. **Module Loader**

**Responsibility:** Auto-load Python files from `lib/` directory.

**Process:**
1. Scan `lib/` directory for `.py` files
2. Import each module
3. Extract functions and classes
4. Inject into execution context

**Example:**

```python
# lib/helpers.py
def format_date(date):
    return date.strftime('%Y-%m-%d')

class Validator:
    @staticmethod
    def email(value):
        return '@' in value
```

**Becomes available in templates:**
```python
{$
formatted = format_date(user['created_at'])
is_valid = Validator.email(user['email'])
$}
```

**Implementation:**
```python
import os
import importlib.util

def load_modules(lib_dir):
    """Load all .py files from lib/ directory"""
    modules = {}

    for filename in os.listdir(lib_dir):
        if filename.endswith('.py'):
            module_name = filename[:-3]
            filepath = os.path.join(lib_dir, filename)

            # Load module
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Extract public functions and classes
            for name in dir(module):
                if not name.startswith('_'):
                    obj = getattr(module, name)
                    if callable(obj) or isinstance(obj, type):
                        modules[name] = obj

    return modules
```

---

### 7. **Migration System**

**Responsibility:** Apply database schema changes.

**Process:**
1. Read SQL files from `migrations/` directory
2. Sort alphabetically (001_*, 002_*, etc.)
3. Track applied migrations in `_migrations` table
4. Apply unapplied migrations in order

**Migration Tracking Table:**
```sql
CREATE TABLE IF NOT EXISTS _migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT UNIQUE NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Algorithm:**
```python
def apply_migrations(db, migrations_dir):
    # Ensure tracking table exists
    db.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Get applied migrations
    applied = {row['filename'] for row in db.query("SELECT filename FROM _migrations")}

    # Get migration files
    files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])

    # Apply unapplied migrations
    for filename in files:
        if filename not in applied:
            filepath = os.path.join(migrations_dir, filename)
            with open(filepath, 'r') as f:
                sql = f.read()

            # Execute migration
            db.execute(sql)

            # Record as applied
            db.execute("INSERT INTO _migrations (filename) VALUES (?)", (filename,))
            db.commit()

            print(f"✓ Applied migration: {filename}")
```

**Implementation:** See [09_MIGRATION_SYSTEM.md](09_MIGRATION_SYSTEM.md)

---

## Data Flow

### **Request Lifecycle**

```
1. HTTP Request Arrives
   │
   ├─▶ Flask receives request
   │   └─▶ Matches route pattern
   │
2. Route Handler Invoked
   │
   ├─▶ Create execution context
   │   ├─ Load database connection
   │   ├─ Load session
   │   ├─ Load auto-loaded modules
   │   └─ Load helpers
   │
3. Execute Python Block
   │
   ├─▶ Run code in sandboxed environment
   │   ├─ Access db, session, request
   │   ├─ Set variables
   │   └─ May return redirect() early
   │
4. Build Template Context
   │
   ├─▶ Extract variables from execution context
   │   └─ Add default helpers (csrf, flash_messages, etc.)
   │
5. Render Jinja2 Template
   │
   ├─▶ Jinja2 processes template with context
   │   ├─ {{ variable }} substitution
   │   ├─ {% for %}, {% if %} logic
   │   └─ Filters and functions
   │
6. Return HTTP Response
   │
   └─▶ Send HTML to client
```

---

## Security Model

### **Execution Sandbox**

**Allowed Operations:**
- Standard Python (loops, conditionals, functions, classes)
- String, list, dict, set operations
- Math operations
- Date/time operations
- Database queries via `db` object
- Session access via `session` object
- Request data via `request` object

**Blocked Operations:**
- File I/O: `open()`, `read()`, `write()`, `os` module
- Network: `socket`, `urllib`, `requests`
- System: `os.system()`, `subprocess`, `eval()`, `exec()`
- Importing: Only whitelisted modules (random, math, datetime)

**Implementation:**
```python
def create_safe_globals():
    """Create restricted builtins for code execution"""

    # Safe builtins
    safe_builtins = {
        # Types
        'int': int, 'float': float, 'str': str, 'bool': bool,
        'list': list, 'dict': dict, 'tuple': tuple, 'set': set,

        # Functions
        'len': len, 'range': range, 'enumerate': enumerate,
        'zip': zip, 'map': map, 'filter': filter, 'sorted': sorted,
        'min': min, 'max': max, 'sum': sum, 'abs': abs,

        # Type checking
        'isinstance': isinstance, 'type': type,

        # String operations
        'print': safe_print,  # Custom implementation

        # Blocked: open, __import__, eval, exec, compile
    }

    return {'__builtins__': safe_builtins}
```

### **SQL Injection Prevention**

**Always use parameterized queries:**

```python
# ✓ SAFE
users = db.query("SELECT * FROM users WHERE username = ?", (username,))

# ✗ UNSAFE (never do this)
users = db.query(f"SELECT * FROM users WHERE username = '{username}'")
```

**Database adapter automatically parameterizes:**
```python
# ✓ SAFE
users = db.where('users', username=username)
# Internally: SELECT * FROM users WHERE username = ?
```

### **CSRF Protection**

**Enabled by default** using Flask-WTF.

**In templates:**
```html
<form method="POST">
    {{ csrf() }}  <!-- Injects hidden CSRF token -->
    <!-- form fields -->
</form>
```

**Automatic validation:** Flask validates token on all POST/PUT/DELETE requests.

### **XSS Prevention**

**Jinja2 auto-escapes** HTML by default:

```html
{{ user_input }}  <!-- Automatically escaped -->
{{ user_input | safe }}  <!-- Manual override (use carefully) -->
```

**In Python blocks:**
```python
{$
from markupsafe import escape
safe_output = escape(user_input)
$}
```

---

## Performance Considerations

### **Template Caching**

**Parse once, reuse:**
- Templates parsed at startup
- AST cached in memory
- Re-parse only if file modified (dev mode)
- No re-parsing in production

### **Database Connection Pooling**

**SQLite:** Single connection (file-based, no pooling needed)
**PostgreSQL/MySQL/MSSQL:** SQLAlchemy connection pool

```python
engine = create_engine(
    connection_string,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True  # Verify connections
)
```

### **Execution Context Reuse**

**Each request gets new context** (for security/isolation), but:
- Auto-loaded modules loaded once at startup
- Database connections pooled
- Helper functions pre-compiled

---

## Error Handling

### **Template Parsing Errors**

```python
# File: app.stpl, line 10
@route('/home'
{$ name = "World" $}

# Error:
SyntaxError: Missing closing parenthesis in route decorator
  File: app.stpl
  Line: 10
  Code: @route('/home'
             ^
```

### **Python Execution Errors**

```python
{$
user = db.find('users', user_id)  # user_id not defined
$}

# Error (debug mode):
NameError: name 'user_id' is not defined
  File: app.stpl
  Route: /dashboard
  Line: 23
  Code: user = db.find('users', user_id)
```

### **Database Errors**

```python
{$
db.execute("SELECT * FROM nonexistent_table")
$}

# Error:
DatabaseError: Table 'nonexistent_table' does not exist
  File: app.stpl
  Route: /home
  Line: 15
```

**In production:** Generic error pages (don't leak internals)
**In development:** Full stack traces

---

## Configuration System

**File:** `scribe.json`

**Schema:** See [13_CONFIGURATION.md](13_CONFIGURATION.md)

**Loading:**
```python
import json

def load_config(project_dir):
    config_path = os.path.join(project_dir, 'scribe.json')
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Apply defaults
    config = apply_defaults(config)

    # Validate
    validate_config(config)

    return config
```

---

## File Organization

### **Recommended Structure**

```
project/
├── scribe.json              # Configuration
├── app.stpl                 # Routes (simple apps)
├── routes/                  # Routes (complex apps)
│   ├── auth.stpl
│   ├── posts.stpl
│   └── admin.stpl
├── lib/                     # Auto-loaded Python modules
│   ├── auth.py
│   ├── models.py
│   └── helpers.py
├── migrations/              # Database migrations
│   ├── 001_initial.sql
│   └── 002_add_posts.sql
├── static/                  # Static files
│   ├── css/
│   ├── js/
│   └── images/
├── data/                    # SQLite database (gitignored)
│   └── app.db
└── venv/                    # Python virtual environment
```

---

## Next Steps

For detailed implementation guides, continue to:

- **[05_TEMPLATE_SPECIFICATION.md](05_TEMPLATE_SPECIFICATION.md)** - Complete syntax reference
- **[06_TEMPLATE_PARSER.md](06_TEMPLATE_PARSER.md)** - Parser implementation
- **[08_DATABASE_ABSTRACTION.md](08_DATABASE_ABSTRACTION.md)** - Database layer
- **[10_FLASK_INTEGRATION.md](10_FLASK_INTEGRATION.md)** - Flask integration
