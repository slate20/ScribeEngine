# Scribe Engine - The Simplest Full-Stack Web Framework

<img width="1921" height="1080" alt="Screenshot from 2025-09-11 01-33-33" src="https://github.com/user-attachments/assets/db2c82bc-33c4-48e6-9bb1-fcd6f27dba3b" />

> **Note**: This branch (expand-scope) pivots Scribe Engine to a full-stack web framework. For the text-based game engine, see the main branch.

Scribe Engine is a Python-based full-stack web framework that makes building web applications incredibly simple. With an integrated IDE featuring syntax highlighting, live preview, SQLite database support, and lightning-fast builds, you can create powerful web applications without wrestling with complex configurations or deployment setups.

Built on Python for backend logic, Jinja2 for templating, SQLite for data persistence, and modern web technologies for the frontend, Scribe Engine gives you professional development tools and the flexibility to create everything from simple data-driven sites to sophisticated web applications.

## Why Scribe Engine?

- **Inline Python in HTML**: Write Python code directly in your templates - no separate route files needed
- **Auto-loading modules**: Drop `.py` files in your project and they're instantly available
- **Built-in database**: SQLite integration with automatic migrations and query builder
- **Integrated IDE**: Syntax highlighting, live preview, and debugging in one place
- **Production ready**: WSGI support for Gunicorn, uWSGI, and Waitress
- **Fast builds**: Package standalone executables in 5-15 seconds

## Quick Start

### Option 1: Download the IDE (Recommended)
Download the `scribe-engine` executable from [Releases](https://github.com/slate20/scribeengine/releases) and you're ready to go - no installation needed.

1. Launch the engine and choose your project directory
2. Click "Create New Project" and name your application
3. Write your web app in the integrated editor with live preview
4. Deploy to production or click "Build" for standalone executable

### Option 2: Use from Source
```bash
# Clone and install dependencies
git clone https://github.com/slate20/ScribeEngine.git
cd ScribeEngine
pip install -r requirements.txt

# Create a new project
python main_engine.py --create my-app --project-root ./projects

# Run development server
python main_engine.py --project-path ./projects/my-app --watch
```

## Example: Your First Web App

**Create `index.stpl`:**
```html
:: index
{$
# Python code runs before HTML rendering
users = db.query("SELECT * FROM users ORDER BY name")
user_count = len(users)
$}

<!DOCTYPE html>
<html>
<head>
    <title>{{title}}</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <h1>Welcome to My App</h1>
    <p>We have {{user_count}} users:</p>

    <ul>
    {% for user in users %}
        <li>{{user.name}} ({{user.email}})</li>
    {% endfor %}
    </ul>

    [[Add User->add_user]]
</body>
</html>
```

**Create `migrations/001_initial.sql`:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (name, email) VALUES
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com');
```

**Create `models/user.py`:**
```python
class User:
    @staticmethod
    def all():
        return db.query("SELECT * FROM users ORDER BY name")

    @staticmethod
    def create(name, email):
        return db.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email)
        )
```

That's it! The database, migrations, and models all work automatically.

## Development Experience

The Scribe Engine comes as a single executable that includes everything you need to create web applications. Most users will want the **GUI version** with the integrated development environment, though a **CLI version** is also available for developers who prefer working with external editors.

### Integrated Development Environment

The built-in IDE provides a complete development experience:
- **Syntax highlighting** for `.stpl` template files and Python
- **Live preview** panel showing your app in real-time as you write
- **Debug terminal** displaying current application state and variables
- **Visual project management** with intuitive file organization
- **Database browser** for inspecting your SQLite data
- **One-click builds** that package your application in seconds

### Database Features

SQLite integration is seamless and automatic:
- **Automatic migrations**: Drop SQL files in `migrations/` and they run on startup
- **Raw SQL**: Full power with parameterized queries
- **Query builder**: Fluent interface for common operations
- **Thread-safe**: Built-in connection pooling and locking
- **Migration tracking**: Never applies the same migration twice

### Production Deployment

Deploy your Scribe Engine app to any Python hosting:

```bash
# Set environment variables
export SCRIBE_ENV=production
export SCRIBE_PROJECT_PATH=/var/www/myapp
export SCRIBE_SECRET_KEY=your-secret-key

# Use Gunicorn (recommended)
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:application

# Or use any WSGI server
uwsgi --http :8000 --wsgi-file wsgi.py --callable application
waitress-serve --port=8000 wsgi:application
```

Or build a standalone executable:

Hit the "Build" button and your application is packaged into a standalone distribution in under 15 seconds. Users can run your app immediately without installing Python or any dependencies.

## Key Features

### Template Format (.stpl files)
- `:: PageName` - Define pages/routes
- `{$ python_code $}` - Inline Python execution
- `{{variable}}` - Jinja2 templating
- `[[Link->Page]]` - Easy navigation
- Full access to `db`, `player`, `game_state`, and custom modules

### Database API
```python
# Raw SQL with parameters
users = db.query("SELECT * FROM users WHERE active = ?", (True,))

# Query builder
users = db.table('users').where(active=True).order_by('name').all()
first = db.table('users').where(id=1).first()

# Insert/Update/Delete
id = db.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
db.execute("UPDATE users SET active = ? WHERE id = ?", (True, id))
db.commit()
```

### Auto-Loading Python Modules
Any `.py` file in your project is automatically loaded and available:
```python
# models/user.py
class User:
    @staticmethod
    def all():
        return db.query("SELECT * FROM users")

# Available immediately in templates:
{$ users = User.all() $}
```

## Project Structure

```
MyApp/
├── project.json          # Configuration
├── index.stpl           # Main page
├── *.stpl               # Additional pages
├── data/                # SQLite database
│   └── app.db
├── migrations/          # SQL migrations
│   ├── 001_initial.sql
│   └── 002_add_table.sql
├── models/              # Python models
│   └── user.py
├── static/              # CSS, JS, images
│   └── style.css
└── *.py                 # Custom modules
```

## Documentation

For detailed instructions on building web applications, database usage, deployment, and advanced features, please refer to the comprehensive [User Documentation](https://github.com/slate20/ScribeEngine/wiki) and [CLAUDE.md](CLAUDE.md) for technical details.