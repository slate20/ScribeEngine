# ScribeEngine 2.0 - Development Guide for Claude

## Project Overview

ScribeEngine 2.0 is a **ground-up rewrite** of a Python web framework that eliminates boilerplate by allowing developers to write Python code directly in templates. This is a fresh start with no existing codebase to maintain.

### What We're Building

A modern Python web framework where developers can:
- Define routes using `@route('/path')` decorators in `.stpl` template files
- Write Python logic inline using `{$ ... $}` blocks
- Use Jinja2 for HTML templating
- Access a unified database API that works across SQLite, PostgreSQL, MySQL, and MSSQL
- Auto-load helper modules from a `lib/` directory
- Get security (CSRF, sessions, auth) by default

**Think:** The simplicity of PHP's inline code, but with Python's ecosystem and modern security practices.

---

## Documentation

All architectural documentation is in `/home/mvenhaus/Projects/ScribeEngine/new-architecture/`:

- **README.md** - Implementation roadmap and overview
- **00_INDEX.md** - Navigation index
- **01_OVERVIEW.md** - Vision, philosophy, and what makes this unique (5,200 words)
- **02_QUICK_START.md** - Example login app walkthrough (3,800 words)
- **03_ARCHITECTURE.md** - Complete system design (4,500 words)
- **05_TEMPLATE_SPECIFICATION.md** - Complete `.stpl` syntax (6,200 words)
- **08_DATABASE_ABSTRACTION.md** - Multi-database support (4,100 words)
- **10_FLASK_INTEGRATION.md** - Flask route generation (3,900 words)
- **IMPLEMENTATION_SUMMARY.md** - This file summarizes all documentation

**Total: ~28,000 words of comprehensive specification**

**When implementing:** Reference these docs for detailed specifications. They contain complete examples, pseudocode, and implementation guidance.

---

## Current State

**STATUS: Phase 2A COMPLETE ✅ - GUI IDE Implemented** (Updated: 2025-12-07)

### What Exists
- ✅ Complete architectural documentation (~28,000 words)
- ✅ **ALL Phase 1 components implemented** (~8,000 lines of code)
- ✅ **Phase 2A GUI IDE implemented** (~3,000 lines of code)
- ✅ **Standalone binary distribution** (PyInstaller) with IDE
- ✅ **Production-ready** (Waitress WSGI server included)
- ✅ **Working login example** (fully functional)
- ✅ **Web-based IDE** (Monaco Editor with .stpl syntax highlighting)
- ✅ **Installation system** (smart installer with GitHub integration)

### Implemented Components (Phase 1 + 2A)
- ✅ Template parser (lexer + parser for `.stpl` files) - **DONE**
- ✅ Flask route generator - **DONE**
- ✅ Database abstraction layer (SQLite working, others planned) - **SQLite DONE**
- ✅ Execution context (sandboxed Python execution with return support) - **DONE**
- ✅ Auto-loading module system - **DONE**
- ✅ Migration system - **DONE**
- ✅ Authentication helpers (@require_auth, password hashing) - **DONE**
- ✅ Session management - **DONE**
- ✅ CSRF protection - **DONE**
- ✅ CLI tool (`scribe new`, `scribe dev`, `scribe serve`, `scribe gui`, `scribe uninstall`) - **DONE**
- ✅ Distributable standalone binary - **DONE**
- ✅ **Web-based IDE (Monaco Editor)** - **DONE** 🆕
- ✅ **Hot-reload file watching** - **DONE** 🆕

### Current Capabilities
**You can now:**
- Create new projects: `scribe new myapp`
- Run development server: `scribe dev`
- Run production server: `scribe serve` (Waitress, no warnings)
- **Launch web-based IDE: `scribe gui`** 🆕
- Write Python in templates with `{$ ... $}` blocks
- Use `return redirect()`, `return jsonify()`, etc. in templates
- Query SQLite database with `db.find()`, `db.where()`, fluent queries
- Protect routes with `@require_auth` decorator
- Auto-load helper functions from `lib/` directory
- Run database migrations from `migrations/` directory
- **Edit files in browser-based IDE with syntax highlighting** 🆕
- **View database tables and data in IDE** 🆕
- **Preview routes in live iframe** 🆕
- **Auto-reload server on file changes** 🆕
- Deploy as standalone binary (no Python installation required)
- Uninstall with `scribe uninstall`

**See PROGRESS.md for detailed status and metrics.**

---

## Project Structure (Target)

```
ScribeEngine/
├── scribe/                      # Main package
│   ├── __init__.py             # Package init, version info
│   ├── cli.py                  # CLI commands (Click-based)
│   ├── app.py                  # Flask app creation and configuration
│   │
│   ├── gui/                    # Web-based IDE 🆕
│   │   ├── __init__.py         # Blueprint initialization
│   │   ├── routes.py           # IDE API endpoints
│   │   ├── templates/          # IDE HTML templates
│   │   │   └── ide.html        # Main IDE interface
│   │   └── static/             # IDE assets
│   │       ├── css/ide.css     # IDE styling
│   │       └── js/ide.js       # IDE JavaScript
│   │
│   ├── parser/                 # Template parsing
│   │   ├── __init__.py
│   │   ├── lexer.py           # Tokenize .stpl files
│   │   ├── parser.py          # Build AST from tokens
│   │   └── ast_nodes.py       # Route, PythonBlock, etc.
│   │
│   ├── database/               # Database abstraction
│   │   ├── __init__.py
│   │   ├── base.py            # DatabaseAdapter abstract class
│   │   ├── sqlite.py          # SQLite implementation
│   │   ├── postgresql.py      # PostgreSQL implementation
│   │   ├── mysql.py           # MySQL implementation
│   │   ├── mssql.py           # MSSQL implementation
│   │   └── query_builder.py  # Fluent query builder
│   │
│   ├── execution/              # Code execution
│   │   ├── __init__.py
│   │   ├── context.py         # Execution context (sandboxed)
│   │   └── builtins.py        # Safe builtins for templates
│   │
│   ├── helpers/                # Built-in helpers
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication (@require_auth, etc.)
│   │   ├── forms.py           # Form helpers (csrf(), flash())
│   │   └── response.py        # redirect(), abort(), etc.
│   │
│   ├── migrations/             # Migration system
│   │   ├── __init__.py
│   │   └── runner.py          # Migration application logic
│   │
│   ├── loader/                 # Module auto-loading
│   │   ├── __init__.py
│   │   └── module_loader.py   # Load lib/*.py files
│   │
│   └── templates/              # Project scaffolding templates
│       └── new_project/       # Template for 'scribe new'
│           ├── scribe.json
│           ├── app.stpl
│           └── lib/.gitkeep
│
├── tests/                      # Test suite
│   ├── test_parser.py
│   ├── test_database.py
│   ├── test_execution.py
│   └── test_integration.py
│
├── examples/                   # Example applications
│   ├── hello_world/
│   ├── login_system/
│   └── blog/
│
├── setup.py                    # Package setup (pip install)
├── requirements.txt            # Dependencies
├── README.md                   # User-facing README
├── CLAUDE.md                   # This file
└── new-architecture/           # All specification docs
```

---

## Technology Stack

### Core
- **Python**: 3.10+ (for modern syntax and type hints)
- **Flask**: 3.x (web framework foundation)
- **Jinja2**: 3.x (template rendering)
- **Click**: 8.x (CLI framework)

### Database
- **SQLite**: Built-in to Python (default database)
- **SQLAlchemy**: 2.x (for PostgreSQL, MySQL, MSSQL)
- **psycopg2**: PostgreSQL driver
- **pymysql**: MySQL driver
- **pymssql**: MSSQL driver

### Security
- **Flask-WTF**: CSRF protection
- **Werkzeug**: Password hashing utilities

### Build & Distribution
- **PyInstaller**: 6.x (create standalone executables)
- **setuptools**: Package distribution

### Testing
- **pytest**: 7.x (testing framework)
- **pytest-flask**: Flask testing utilities

---

## Development Phases

### Phase 1: Core Foundation (Current Focus)
**Goal:** Get a basic hello world and login example working

**Must Build:**
1. ✅ **Template Lexer** - Tokenize `.stpl` files
2. ✅ **Template Parser** - Build AST from tokens
3. ✅ **Flask Route Generator** - Convert AST to Flask routes
4. ✅ **Execution Context** - Safe Python execution environment
5. ✅ **Database Adapter** - SQLite implementation
6. ✅ **Auth Helpers** - `@require_auth`, login/logout functions
7. ✅ **Session Management** - Flask session integration
8. ✅ **CSRF Protection** - Auto-inject tokens, validate on POST
9. ✅ **Module Loader** - Auto-load `lib/*.py` files
10. ✅ **Basic CLI** - `scribe new`, `scribe dev`
11. ✅ **Migration System** - Apply SQL files from `migrations/`

**Success Criteria:**
- Can create new project: `scribe new myapp`
- Can run dev server: `scribe dev`
- Can define routes using `@route('/path')`
- Can execute Python in `{$ ... $}` blocks
- Can query SQLite database
- Can use `@require_auth` decorator
- Forms have automatic CSRF protection
- Session works across requests
- Can run the login example from `new-architecture/02_QUICK_START.md`

### Phase 2: Multi-Database & Production Ready (Next)
**Goal:** Support all databases, deploy to production

**Must Build:**
1. PostgreSQL adapter
2. MySQL adapter
3. MSSQL adapter
4. Query builder (fluent interface)
5. Enhanced auth system
6. Form validation helpers
7. Configuration system (`scribe.json` schema)
8. Error handling & logging
9. Production deployment docs

### Phase 3: Developer Experience
**Goal:** Make it pleasant to use

**Must Build:**
1. Hot reload (auto-restart on file changes)
2. Better error messages
3. Debug toolbar
4. Query logging
5. Project templates (`scribe new blog`)
6. CLI enhancements

### Phase 4: IDE & Build System
**Goal:** Integrated development environment

**Must Build:**
1. Web-based code editor (Monaco)
2. Live preview panel
3. Database browser
4. Migration manager
5. Build system (`scribe build` → standalone executable)

### Phase 5: Polish & Release
**Goal:** Public v1.0.0

**Tasks:**
1. Comprehensive testing
2. Performance optimization
3. Security audit
4. Documentation website
5. Example applications
6. PyPI package setup
7. GitHub repo setup
8. CI/CD pipeline

---

## Implementation Priority

### Immediate Next Steps (Phase 1)

Build in this order:

1. **Project Structure** - Create directory layout
2. **Dependencies** - Create `requirements.txt`, `setup.py`
3. **Template Lexer** - Tokenize `.stpl` files (see `05_TEMPLATE_SPECIFICATION.md`)
4. **Template Parser** - Build Route AST (see `03_ARCHITECTURE.md`)
5. **Database - SQLite** - Basic adapter (see `08_DATABASE_ABSTRACTION.md`)
6. **Execution Context** - Sandboxed Python execution (see `03_ARCHITECTURE.md`)
7. **Flask Integration** - Route generation (see `10_FLASK_INTEGRATION.md`)
8. **Session Management** - Flask session setup
9. **CSRF Protection** - Flask-WTF integration
10. **Auth Helpers** - `@require_auth`, login/logout
11. **Module Loader** - Auto-load `lib/*.py`
12. **Migration System** - Apply SQL files
13. **CLI** - `scribe new`, `scribe dev` commands
14. **Testing** - Test with login example from `02_QUICK_START.md`

---

## Key Design Decisions

### 1. Template Syntax
**Decision:** Use `@route()` decorator style (not Twine's `:: passage` style)

**Reason:** More familiar to Python developers, clearer intent

**Example:**
```python
@route('/posts/<int:post_id>')
@require_auth
{$
post = db.find('posts', post_id)
comments = db.table('comments').where(post_id=post_id).all()
$}

<article>
    <h1>{{ post['title'] }}</h1>
    <div>{{ post['content'] }}</div>
</article>
```

### 2. Database Abstraction
**Decision:** Unified API with parameter normalization across all databases

**Reason:** Write once, run on any database

**Example:**
```python
# Same code works on SQLite, PostgreSQL, MySQL, MSSQL
user = db.find('users', 123)
posts = db.table('posts').where(user_id=user['id']).all()
```

### 3. Security Model
**Decision:** Sandboxed Python execution with whitelisted operations

**Allowed:**
- Database queries via `db` object
- Session access via `session` object
- Request data via `request` object
- Standard Python (loops, conditionals, functions)

**Blocked:**
- File I/O (`open()`, `read()`, `write()`)
- Network operations (`socket`, `urllib`)
- System calls (`os.system()`, `subprocess`)
- Arbitrary imports

### 4. Flask Integration
**Decision:** Generate routes dynamically at startup, compile to standard Flask

**Reason:**
- WSGI compatible (Gunicorn, uWSGI, Waitress)
- Full Flask ecosystem available
- Standard deployment patterns

### 5. Module Loading
**Decision:** Auto-load all `.py` files from `lib/` directory

**Reason:** Zero boilerplate, convention over configuration

**Example:**
```python
# lib/helpers.py
def format_date(date):
    return date.strftime('%Y-%m-%d')

# Automatically available in templates:
{$ formatted = format_date(user['created_at']) $}
```

### 6. CSRF Protection
**Decision:** Enabled by default, automatic token injection

**Reason:** Security by default, prevent common vulnerabilities

**Example:**
```html
<form method="POST">
    {{ csrf() }}  <!-- Auto-injected token -->
    <input name="username">
    <button>Submit</button>
</form>
```

### 7. Session Management
**Decision:** Flask sessions with secure defaults

**Reason:** Standard, well-tested, compatible with Flask ecosystem

**Configuration:**
- HTTP-only cookies
- Secure flag (HTTPS)
- SameSite=Lax
- Configurable timeout

---

## API Design

### Template Parser API
```python
from scribe.parser import TemplateParser

parser = TemplateParser()
routes = parser.parse_file('app.stpl')

for route in routes:
    print(route.path)           # '/home'
    print(route.methods)        # ['GET']
    print(route.decorators)     # ['require_auth']
    print(route.python_code)    # 'user = db.find(...)'
    print(route.template)       # '<h1>Hello</h1>'
```

### Database Adapter API
```python
from scribe.database import create_adapter

db = create_adapter(config)

# Find by ID
user = db.find('users', 1)

# Simple where
users = db.where('users', active=True)

# Query builder
posts = db.table('posts') \
    .where(published=True) \
    .order_by('-created_at') \
    .limit(10) \
    .all()

# Raw SQL
results = db.query("SELECT * FROM users WHERE active = ?", (True,))

# Insert
user_id = db.insert('users', username='alice', email='alice@example.com')

# Update
db.update('users', {'active': False}, id=user_id)

# Delete
db.delete('users', id=user_id)
```

### Execution Context API
```python
from scribe.execution import ExecutionContext

context = ExecutionContext(
    db=db_adapter,
    session=flask.session,
    request=flask.request,
    helpers=loaded_helpers
)

# Execute Python code
result = context.execute(python_code)

# Get variables for template rendering
template_vars = context.get_variables()
```

### CLI API
```bash
# Create new project
scribe new myapp

# Run development server
scribe dev

# Run on different host/port
scribe dev --host 0.0.0.0 --port 8000

# Apply migrations
scribe db migrate

# Build executable (Phase 4)
scribe build
```

---

## Security Requirements

### Mandatory Security Features (Phase 1)

1. **CSRF Protection**
   - Auto-enabled on all POST/PUT/DELETE requests
   - Token injection via `{{ csrf() }}`
   - Validation before route handler execution

2. **SQL Injection Prevention**
   - All database methods use parameterized queries
   - Raw SQL requires explicit parameters
   - Never string interpolation for SQL

3. **XSS Prevention**
   - Jinja2 auto-escaping enabled by default
   - User must explicitly mark content as safe

4. **Session Security**
   - HTTP-only cookies
   - Secure flag when HTTPS detected
   - SameSite=Lax
   - Session timeout

5. **Password Hashing**
   - Werkzeug's `generate_password_hash()` (scrypt)
   - Never store plaintext passwords
   - Helper functions in default scaffold

6. **Sandboxed Execution**
   - Restricted builtins (no file I/O, network, system calls)
   - Whitelisted imports only
   - Cannot escape execution context

### Security Validation Checklist

Before considering Phase 1 complete:
- [ ] CSRF tokens required and validated
- [ ] All DB queries parameterized
- [ ] Jinja2 auto-escaping enabled
- [ ] Sessions use secure cookies
- [ ] Password hashing examples in docs
- [ ] Execution sandbox prevents file I/O
- [ ] Execution sandbox prevents network access
- [ ] Execution sandbox prevents system calls

---

## Testing Strategy

### Unit Tests (Phase 1)
- Template lexer tokenization
- Template parser AST generation
- Database adapter methods
- Query builder
- Execution context variable isolation
- CSRF token generation/validation
- Session management

### Integration Tests (Phase 1)
- Parse .stpl → Generate Flask routes → Handle request
- Database queries in execution context
- Form submission with CSRF
- Login/logout flow
- @require_auth decorator

### End-to-End Tests (Phase 2+)
- Complete login system
- Multi-route applications
- File uploads
- API endpoints

### Example Test Structure
```python
# tests/test_parser.py
def test_parse_simple_route():
    parser = TemplateParser()
    content = """
    @route('/')
    {$ message = "Hello" $}
    <h1>{{ message }}</h1>
    """
    routes = parser.parse(content, 'test.stpl')

    assert len(routes) == 1
    assert routes[0].path == '/'
    assert 'message = "Hello"' in routes[0].python_code
```

---

## Distribution Strategy

### Development Install
```bash
git clone https://github.com/yourusername/scribe-engine.git
cd scribe-engine
pip install -e .
```

### PyPI Install (v1.0+)
```bash
pip install scribe-engine
```

### Standalone Binary (Phase 4)
```bash
scribe build
# Creates: dist/scribe.exe (Windows) or dist/scribe (Linux/Mac)
```

**Binary includes:**
- Python runtime (embedded)
- All dependencies
- No installation required

---

## Common Patterns & Examples

### Pattern 1: Protected Route with Database Query
```python
@route('/dashboard')
@require_auth
{$
user = db.find('users', session['user_id'])
recent_posts = db.table('posts') \
    .where(user_id=user['id']) \
    .order_by('-created_at') \
    .limit(5) \
    .all()
$}

<h1>Welcome, {{ user['username'] }}</h1>
{% for post in recent_posts %}
    <article>{{ post['title'] }}</article>
{% endfor %}
```

### Pattern 2: Form with Validation
```python
@route('/posts/new', methods=['GET', 'POST'])
@require_auth
{$
errors = {}

if request.method == 'POST':
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()

    if not title:
        errors['title'] = "Title is required"
    if not content:
        errors['content'] = "Content is required"

    if not errors:
        db.insert('posts',
            title=title,
            content=content,
            user_id=session['user_id']
        )
        return redirect('/dashboard')
$}

<form method="POST">
    {{ csrf() }}

    <div>
        <label>Title</label>
        <input name="title" value="{{ request.form.get('title', '') }}">
        {% if errors.title %}
            <span class="error">{{ errors.title }}</span>
        {% endif %}
    </div>

    <button>Create Post</button>
</form>
```

### Pattern 3: API Endpoint
```python
@route('/api/posts', methods=['GET'])
{$
from flask import jsonify

posts = db.table('posts') \
    .where(published=True) \
    .all()

return jsonify({
    'posts': [dict(p) for p in posts]
})
$}
```

---

## Reference Implementation (Minimal)

See `new-architecture/README.md` for a 100-line proof of concept that demonstrates:
- Template parsing (regex-based)
- Flask route generation
- Python execution in templates
- Database queries
- Jinja2 rendering

This can serve as a reference for the full implementation.

---

## Success Criteria

### Phase 1 Complete When:
- [ ] Can run `scribe new myapp` and create project structure
- [ ] Can run `scribe dev` and start development server
- [ ] Can define routes using `@route('/path')`
- [ ] Can execute Python in `{$ ... $}` blocks
- [ ] Can access `db`, `session`, `request` in Python blocks
- [ ] Can query SQLite database
- [ ] Can use `@require_auth` decorator
- [ ] Forms automatically have CSRF protection via `{{ csrf() }}`
- [ ] Sessions persist across requests
- [ ] Can auto-load modules from `lib/` directory
- [ ] Can apply migrations from `migrations/` directory
- [ ] **Can run the complete login example from `02_QUICK_START.md`**

### v1.0 Release Ready When:
- [ ] All Phase 1-3 features implemented
- [ ] Supports SQLite, PostgreSQL, MySQL, MSSQL
- [ ] Has comprehensive test suite (>80% coverage)
- [ ] Has documentation website
- [ ] Has 5+ example applications
- [ ] Can build standalone executable
- [ ] Security audit passed
- [ ] Performance tested (handles 100+ req/sec)

---

## Working with Claude

### When I Ask Questions
- Reference the documentation in `new-architecture/` for detailed specs
- Check `03_ARCHITECTURE.md` for component design
- Check `05_TEMPLATE_SPECIFICATION.md` for syntax details
- Check `02_QUICK_START.md` for working examples

### When You Implement
- Follow the directory structure defined above
- Use type hints (Python 3.10+)
- Write docstrings for all public APIs
- Include inline comments for complex logic
- Write tests alongside implementation
- Follow PEP 8 style guide

### When You're Stuck
- Ask for clarification before making assumptions
- Propose multiple solutions with tradeoffs
- Reference similar patterns from Flask/Django/other frameworks

### When You Complete a Component
- Confirm it matches the specification
- Show example usage
- List what's next in the dependency chain

---

## Git Branch Strategy

- `main` - Stable releases only
- `develop` - Active development
- `feature/*` - Feature branches
- `docs/*` - Documentation updates

**Current branch:** `framework` (transitional, will merge to `develop`)

---

## Notes & Reminders

1. **This is a ground-up rewrite** - No legacy code to maintain
2. **Security first** - CSRF, sessions, auth are mandatory from day 1
3. **Documentation exists** - 28,000 words of specs in `new-architecture/`
4. **Target: v1.0** - Aim for PyPI distribution and standalone binary
5. **Open source** - Will be on GitHub with permissive license (TBD: MIT or Apache 2.0)

---

## Quick Reference Links

- **Vision & Philosophy:** `new-architecture/01_OVERVIEW.md`
- **Working Example:** `new-architecture/02_QUICK_START.md`
- **System Architecture:** `new-architecture/03_ARCHITECTURE.md`
- **Template Syntax:** `new-architecture/05_TEMPLATE_SPECIFICATION.md`
- **Database Layer:** `new-architecture/08_DATABASE_ABSTRACTION.md`
- **Flask Integration:** `new-architecture/10_FLASK_INTEGRATION.md`
- **Full Summary:** `new-architecture/IMPLEMENTATION_SUMMARY.md`

---

**Last Updated:** 2025-12-07
**Current Phase:** Phase 1 - COMPLETE ✅
**Next Milestone:** Phase 2 - Multi-Database Support

---

## Quick Links

- **PROGRESS.md** - Detailed progress tracking with metrics
- **new-architecture/** - Design documentation (28,000 words)
- **tests/loginapp/** - Working login example
- **build.py** - Build standalone binary
- **install.sh** - Smart installer script
