# ScribeEngine 2.0 - Complete Implementation Guide

Welcome to the ScribeEngine 2.0 implementation documentation. This is a **ground-up rewrite** specification for building a modern Python web framework with inline templating.

---

## What is ScribeEngine?

**ScribeEngine** is a Python web framework that eliminates boilerplate by letting you write Python code directly in your templates. No separate route files, no separate controllers—just write what you need, where you need it.

### **Key Features**

✅ **Inline Python in templates** - Write logic where you use it
✅ **Auto-loading modules** - Drop `.py` files in `lib/` → automatically available
✅ **Multi-database support** - SQLite, PostgreSQL, MySQL, MSSQL
✅ **Integrated IDE** - Web-based editor with live preview
✅ **Executable builds** - Distribute as standalone .exe
✅ **Flask underneath** - Full Flask ecosystem available

---

## Documentation Structure

### **📚 Start Here**

| Document | Purpose | Read When |
|----------|---------|-----------|
| [00_INDEX.md](00_INDEX.md) | Navigation index | First time browsing |
| [01_OVERVIEW.md](01_OVERVIEW.md) | Vision & philosophy | Understanding the "why" |
| [02_QUICK_START.md](02_QUICK_START.md) | Build a login app in 10 min | Want to see it in action |

### **🏗️ Core Architecture**

| Document | Purpose | For |
|----------|---------|-----|
| [03_ARCHITECTURE.md](03_ARCHITECTURE.md) | System design & components | Architects & implementers |
| [04_PROJECT_STRUCTURE.md](04_PROJECT_STRUCTURE.md) | File organization | Project planning |

### **📝 Template System**

| Document | Purpose | For |
|----------|---------|-----|
| [05_TEMPLATE_SPECIFICATION.md](05_TEMPLATE_SPECIFICATION.md) | Complete `.stpl` syntax | Template developers |
| [06_TEMPLATE_PARSER.md](06_TEMPLATE_PARSER.md) | Parser implementation | Parser implementers |
| [07_EXECUTION_CONTEXT.md](07_EXECUTION_CONTEXT.md) | Python execution env | Security & runtime |

### **💾 Database Layer**

| Document | Purpose | For |
|----------|---------|-----|
| [08_DATABASE_ABSTRACTION.md](08_DATABASE_ABSTRACTION.md) | Multi-DB support | Database developers |
| [09_MIGRATION_SYSTEM.md](09_MIGRATION_SYSTEM.md) | Schema migrations | Database management |

### **🌐 Web Framework**

| Document | Purpose | For |
|----------|---------|-----|
| [10_FLASK_INTEGRATION.md](10_FLASK_INTEGRATION.md) | Flask route generation | Web framework integration |
| [11_HELPERS_API.md](11_HELPERS_API.md) | Built-in helpers | API documentation |
| [12_AUTHENTICATION.md](12_AUTHENTICATION.md) | Auth system | Security implementers |

### **⚙️ Configuration & CLI**

| Document | Purpose | For |
|----------|---------|-----|
| [13_CONFIGURATION.md](13_CONFIGURATION.md) | `scribe.json` schema | Configuration |
| [14_CLI_SPECIFICATION.md](14_CLI_SPECIFICATION.md) | Command-line interface | CLI developers |

### **🖥️ IDE & Tooling**

| Document | Purpose | For |
|----------|---------|-----|
| [15_IDE_SPECIFICATION.md](15_IDE_SPECIFICATION.md) | Web-based IDE | IDE developers |
| [16_BUILD_SYSTEM.md](16_BUILD_SYSTEM.md) | Executable packaging | Build engineers |

### **🔒 Security & Best Practices**

| Document | Purpose | For |
|----------|---------|-----|
| [17_SECURITY.md](17_SECURITY.md) | Security model | Security review |
| [18_BEST_PRACTICES.md](18_BEST_PRACTICES.md) | Recommended patterns | All developers |

### **📖 Reference**

| Document | Purpose | For |
|----------|---------|-----|
| [19_COMPLETE_EXAMPLES.md](19_COMPLETE_EXAMPLES.md) | Full app examples | Learning & reference |
| [20_API_REFERENCE.md](20_API_REFERENCE.md) | Complete API docs | API reference |

---

## Implementation Roadmap

### **Phase 1: Proof of Concept (Week 1-2)**

**Goal:** Get a basic login example working

**Components to build:**
1. ✅ Template lexer (tokenize `.stpl` files)
2. ✅ Template parser (extract routes and Python blocks)
3. ✅ Flask route generator
4. ✅ Execution context (safe Python execution)
5. ✅ SQLite database adapter
6. ✅ Basic CLI (`scribe dev`)

**Deliverable:** Run the login example from [02_QUICK_START.md](02_QUICK_START.md)

**Success criteria:**
- Parse `@route()` decorators
- Extract `{$ python $}` blocks
- Generate Flask routes
- Execute Python in templates
- Query SQLite database
- Render Jinja2 templates

---

### **Phase 2: Core Features (Week 3-6)**

**Goal:** Production-ready web framework

**Components to build:**
1. ✅ Complete template syntax support
2. ✅ PostgreSQL adapter
3. ✅ MySQL adapter
4. ✅ MSSQL adapter
5. ✅ Migration system
6. ✅ Auth helpers (`@require_auth`, `auth.login()`)
7. ✅ Form helpers (`csrf()`, `flash()`)
8. ✅ Auto-loading Python modules
9. ✅ Configuration system (`scribe.json`)
10. ✅ Error handling

**Deliverable:** Build a complete blog application

**Success criteria:**
- Switch databases via config
- Migrations run automatically
- Authentication works
- Forms handle CSRF
- Multiple `.stpl` files work
- Production deployment ready

---

### **Phase 3: Developer Experience (Week 7-10)**

**Goal:** Make it pleasant to use

**Components to build:**
1. ✅ Enhanced CLI commands
2. ✅ Project templates (`scribe new blog`)
3. ✅ Hot reload (auto-restart on file changes)
4. ✅ Better error messages
5. ✅ Debug toolbar
6. ✅ Query logging
7. ✅ Performance profiling

**Deliverable:** Polished developer experience

**Success criteria:**
- Create new project in 30 seconds
- See helpful error messages
- Auto-reload on file save
- Profile slow queries
- Debug easily

---

### **Phase 4: IDE & Tooling (Week 11-14)**

**Goal:** Integrated development environment

**Components to build:**
1. ✅ Web-based code editor (Monaco)
2. ✅ File manager
3. ✅ Live preview panel
4. ✅ Database browser
5. ✅ Migration manager
6. ✅ Build system (PyInstaller)
7. ✅ Deployment tools

**Deliverable:** Complete IDE

**Success criteria:**
- Edit code in browser
- See live preview
- Browse database
- Create migrations
- Build executables
- Deploy to server

---

### **Phase 5: Polish & Release (Week 15+)**

**Goal:** Public release

**Tasks:**
1. ✅ Comprehensive testing
2. ✅ Performance optimization
3. ✅ Security audit
4. ✅ Documentation website
5. ✅ Tutorial videos
6. ✅ Example applications
7. ✅ PyPI package
8. ✅ Community setup (GitHub, Discord)

**Deliverable:** v1.0.0 release

---

## Quick Implementation Guide

### **Step 1: Set Up Project Structure**

```bash
scribe-engine/
├── scribe/                  # Main package
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   ├── app.py              # Flask app creation
│   ├── parser/             # Template parsing
│   │   ├── __init__.py
│   │   ├── lexer.py
│   │   └── parser.py
│   ├── database/           # Database adapters
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── sqlite.py
│   │   ├── postgresql.py
│   │   └── mysql.py
│   ├── helpers/            # Helper functions
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── forms.py
│   └── templates/          # Project templates
├── setup.py
├── requirements.txt
└── README.md
```

### **Step 2: Implement Template Parser**

**See:** [06_TEMPLATE_PARSER.md](06_TEMPLATE_PARSER.md)

```python
# scribe/parser/parser.py
class TemplateParser:
    def parse(self, content, filename):
        """Parse .stpl file into routes"""
        lexer = Lexer(content)
        tokens = lexer.tokenize()

        routes = []
        current_route = None

        for token in tokens:
            if token.type == 'ROUTE_DECORATOR':
                current_route = Route(
                    path=token.args[0],
                    methods=token.kwargs.get('methods', ['GET'])
                )
            elif token.type == 'PYTHON_BLOCK':
                current_route.python_code = token.value
            elif token.type == 'HTML':
                current_route.template = token.value
                routes.append(current_route)

        return routes
```

### **Step 3: Implement Database Adapter**

**See:** [08_DATABASE_ABSTRACTION.md](08_DATABASE_ABSTRACTION.md)

```python
# scribe/database/sqlite.py
class SQLiteAdapter:
    def query(self, sql, params=None):
        """Execute SELECT query"""
        cursor = self.connection.cursor()
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        return [Row(dict(row)) for row in rows]
```

### **Step 4: Implement Flask Integration**

**See:** [10_FLASK_INTEGRATION.md](10_FLASK_INTEGRATION.md)

```python
# scribe/app.py
def create_app(project_path):
    """Create Flask app from ScribeEngine project"""
    app = Flask(__name__)

    # Load config
    config = load_config(project_path)

    # Create database
    db = create_database_adapter(config['database'])

    # Load routes
    routes = load_routes(project_path)

    # Register routes
    for route in routes:
        handler = create_route_handler(route, db)
        app.add_url_rule(
            route.path,
            endpoint=route.endpoint,
            view_func=handler,
            methods=route.methods
        )

    return app
```

### **Step 5: Implement CLI**

**See:** [14_CLI_SPECIFICATION.md](14_CLI_SPECIFICATION.md)

```python
# scribe/cli.py
import click

@click.group()
def cli():
    """ScribeEngine CLI"""
    pass

@cli.command()
@click.argument('name')
def new(name):
    """Create new project"""
    create_project(name)

@cli.command()
@click.option('--host', default='127.0.0.1')
@click.option('--port', default=5000)
def dev(host, port):
    """Run development server"""
    app = create_app('.')
    app.run(host=host, port=port, debug=True)
```

---

## Testing Your Implementation

### **Test 1: Parse Template**

```python
from scribe.parser import TemplateParser

template = """
@route('/')
{$ message = "Hello" $}
<h1>{{ message }}</h1>
"""

parser = TemplateParser()
routes = parser.parse(template, 'test.stpl')

assert len(routes) == 1
assert routes[0].path == '/'
assert 'message = "Hello"' in routes[0].python_code
```

### **Test 2: Database Query**

```python
from scribe.database import create_database_adapter

config = {'type': 'sqlite', 'path': ':memory:'}
db = create_database_adapter(config)

db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
user_id = db.insert('users', name='Alice')
user = db.find('users', user_id)

assert user['name'] == 'Alice'
```

### **Test 3: Full Request**

```python
from scribe import create_app

app = create_app('test_project')
client = app.test_client()

response = client.get('/')
assert response.status_code == 200
assert b'Hello' in response.data
```

---

## Dependencies

### **Core Dependencies**

```
Flask>=3.0.0           # Web framework
Jinja2>=3.1.0          # Template engine
Click>=8.1.0           # CLI framework
Flask-WTF>=1.2.0       # CSRF protection
Werkzeug>=3.0.0        # Utilities
```

### **Database Drivers**

```
# SQLite - built into Python

# PostgreSQL
psycopg2-binary>=2.9.0
SQLAlchemy>=2.0.0

# MySQL
pymysql>=1.1.0
SQLAlchemy>=2.0.0

# MSSQL
pymssql>=2.2.0
SQLAlchemy>=2.0.0
```

### **Development Tools**

```
pytest>=7.4.0          # Testing
black>=23.0.0          # Code formatting
flake8>=6.0.0          # Linting
mypy>=1.5.0            # Type checking
```

### **IDE Dependencies**

```
pywebview>=4.0.0       # Native window
Pygments>=2.16.0       # Syntax highlighting
```

### **Build Dependencies**

```
PyInstaller>=6.0.0     # Executable builds
```

---

## Example: Minimal Implementation

**File: `minimal.py`** (100-line proof of concept)

```python
import re
from flask import Flask, request, session
from flask_wtf.csrf import CSRFProtect
import sqlite3

# === Template Parser ===
def parse_template(content):
    """Minimal .stpl parser"""
    route_pattern = r'@route\([\'"](.+?)[\'"]\)'
    python_pattern = r'\{\$(.*?)\$\}'

    match = re.search(route_pattern, content)
    path = match.group(1) if match else '/'

    match = re.search(python_pattern, content, re.DOTALL)
    python_code = match.group(1).strip() if match else ''

    template = re.sub(route_pattern, '', content)
    template = re.sub(python_pattern, '', template, flags=re.DOTALL)

    return {'path': path, 'python_code': python_code, 'template': template}

# === Database ===
class DB:
    def __init__(self):
        self.conn = sqlite3.connect(':memory:', check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def query(self, sql, params=()):
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def execute(self, sql, params=()):
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        self.conn.commit()
        return cursor.lastrowid

# === Flask App ===
app = Flask(__name__)
app.secret_key = 'dev'
csrf = CSRFProtect(app)
db = DB()

# Parse template
template_content = """
@route('/')
{$
message = "Hello, ScribeEngine!"
$}
<h1>{{ message }}</h1>
"""

route = parse_template(template_content)

# Create route handler
@app.route(route['path'], methods=['GET', 'POST'])
def index():
    # Execute Python code
    context = {'db': db, 'session': session, 'request': request}
    exec(route['python_code'], context)

    # Render template
    from jinja2 import Template
    template = Template(route['template'])
    return template.render(**context)

if __name__ == '__main__':
    app.run(debug=True)
```

**Run it:**
```bash
python minimal.py
# Visit http://127.0.0.1:5000
# See: "Hello, ScribeEngine!"
```

---

## Next Steps

1. **Read** [01_OVERVIEW.md](01_OVERVIEW.md) to understand the vision
2. **Try** [02_QUICK_START.md](02_QUICK_START.md) to see it in action
3. **Study** [03_ARCHITECTURE.md](03_ARCHITECTURE.md) for system design
4. **Build** the proof of concept (Phase 1)
5. **Test** with the login example
6. **Expand** to full feature set (Phase 2-5)

---

## Support & Community

- **GitHub:** (TBD - create repository)
- **Discord:** (TBD - create server)
- **Documentation:** (TBD - create website)
- **PyPI:** (TBD - publish package)

---

## License

(TBD - choose license: MIT, Apache 2.0, etc.)

---

**Ready to build ScribeEngine?** Start with [01_OVERVIEW.md](01_OVERVIEW.md)!
