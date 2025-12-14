"""
Command-line interface for ScribeEngine.

Provides commands:
    scribe new <project>    - Create new project
    scribe dev              - Run development server
    scribe db migrate       - Run database migrations
"""

import click
import os
import shutil
from pathlib import Path


def create_docs(project_path, project_name):
    """Create documentation directory and files"""
    docs_path = os.path.join(project_path, 'docs')
    os.makedirs(docs_path, exist_ok=True)

    # docs/README.md
    docs_readme = f'''# ScribeEngine Documentation

Welcome to your {project_name} documentation! These guides will help you get the most out of ScribeEngine.

## 📚 Guides

1. **[Getting Started](01_GETTING_STARTED.md)** - Create your first routes and understand the basics
2. **[Template Syntax](02_TEMPLATE_SYNTAX.md)** - Complete reference for .stpl files
3. **[Database](03_DATABASE.md)** - Working with databases, queries, and migrations
4. **[Authentication](04_AUTHENTICATION.md)** - Understanding and customizing the auth system
5. **[Deployment](05_DEPLOYMENT.md)** - Deploying your app to production

## 🚀 Recommended Reading Order

**New to ScribeEngine?**
1. Start with Getting Started
2. Read Template Syntax
3. Explore Database guide
4. Dive into Authentication (if using auth)

**Ready for production?**
- Jump to Deployment guide

## 🔗 More Resources

- **Full Documentation:** See the `new-architecture/` directory for complete technical specs
- **Examples:** Check out the `/login`, `/dashboard` routes in your `app.stpl`
- **Community:** [GitHub Issues](https://github.com/yourusername/scribe-engine/issues)

## 💡 Quick Reference

**Define a route:**
```python
@route('/hello')
'''+'''{$
message = "Hello!"
$}
<h1>'''+'''{{ message }}</h1>
```

**Query database:**
```python
{$
users = db['default'].query("SELECT * FROM users")
$}
```

**Protect a route:**
```python
@route('/admin')
@require_auth
{$
... $}
```

Happy coding! 🎉
'''

    # Write docs/README.md
    with open(os.path.join(docs_path, 'README.md'), 'w') as f:
        f.write(docs_readme)

    # docs/01_GETTING_STARTED.md
    getting_started = '''# Getting Started with ScribeEngine

This guide will walk you through creating your first custom route and understanding how ScribeEngine works.

## Your Project Structure

After running `scribe new myapp`, you have:

```
myapp/
├── app.stpl              # Your routes (this is where you'll spend most time)
├── base.stpl             # HTML layout template
├── scribe.json           # Configuration (database, secret key)
├── lib/                  # Helper functions (auto-loaded)
│   └── auth_helpers.py   # Password hashing functions
├── migrations/           # Database schema changes
│   └── 001_users.sql     # Initial user table
├── static/               # CSS, JavaScript, images
│   ├── css/
│   │   └── style.css     # Your styles
│   └── js/
├── docs/                 # Documentation (you are here!)
└── app.db                # SQLite database (created automatically)
```

## Running Your App

```bash
cd myapp
scribe dev
```

Open http://localhost:5000 in your browser. You should see the welcome page!

## Understanding Routes

Routes are defined in `app.stpl` using the `@route()` decorator:

```python
@route('/hello')
'''+'''{$
message = "Hello, World!"
$}

<h1>'''+'''{{ message }}</h1>
```

**What's happening:**
1. `@route('/hello')` - Defines URL path
2. `'''+'''{$ ... $}` - Python code block (executed server-side)
3. `message = "Hello, World!"` - Creates a variable
4. `'''+'''{{ message }}` - Jinja2 template variable (renders in HTML)

## Your First Custom Route

Let's add a simple blog post route. Open `app.stpl` and add at the end:

```python
@route('/blog')
'''+'''{$
page_title = "Blog"
posts = [
    {"title": "First Post", "date": "2025-01-01"},
    {"title": "Second Post", "date": "2025-01-15"},
]
$}

<div class="container">
    <h1>Blog Posts</h1>

    '''+'''{'''+ '''% for post in posts %}
    <div class="card">
        <h2>'''+'''{{ post.title }}</h2>
        <p class="text-muted">Posted on '''+'''{{ post.date }}</p>
    </div>
    '''+'''{'''+ '''% endfor %}
</div>
```

**Save the file** and the server will automatically reload. Visit http://localhost:5000/blog

## Working with Route Parameters

You can capture parts of the URL:

```python
@route('/blog/<int:post_id>')
'''+'''{$
page_title = f"Post #'''+'''{post_id}"
# post_id is automatically available as an integer
posts = {
    1: {"title": "First Post", "content": "Hello world!"},
    2: {"title": "Second Post", "content": "Another post"},
}
post = posts.get(post_id, None)

if not post:
    return abort(404)
$}

<div class="container">
    <div class="card">
        <h1>'''+'''{{ post.title }}</h1>
        <p>'''+'''{{ post.content }}</p>
    </div>
</div>
```

**Parameter types:**
- `<int:id>` - Integer
- `<string:name>` - String (default)
- `<path:filepath>` - Path (with slashes)

## Using the Database

Your app comes with a SQLite database. Let's query it:

```python
@route('/users')
'''+'''{$
page_title = "Users"
# Query the database
users = db['default'].query("SELECT * FROM users")
$}

<div class="container">
    <h1>Users</h1>

    '''+'''{'''+ '''% if users %}
        '''+'''{'''+ '''% for user in users %}
        <div class="card">
            <h3>'''+'''{{ user.username }}</h3>
            <p>Joined: '''+'''{{ user.created_at }}</p>
        </div>
        '''+'''{'''+ '''% endfor %}
    '''+'''{'''+ '''% else %}
        <p>No users found.</p>
    '''+'''{'''+ '''% endif %}
</div>
```

**Important:** Always use parameterized queries to prevent SQL injection:

```python
# ✅ GOOD (parameterized)
users = db['default'].query(
    "SELECT * FROM users WHERE username = ?",
    (username,)
)

# ❌ BAD (vulnerable to SQL injection)
users = db['default'].query(
    f"SELECT * FROM users WHERE username = '''+'''{username}"
)
```

## Forms and POST Requests

Handle form submissions:

```python
@route('/contact', methods=['GET', 'POST'])
'''+'''{$
page_title = "Contact"
success = False

if request.method == 'POST':
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Process the form (e.g., save to database)
    # ... your logic here ...

    success = True
$}

<div class="container-narrow">
    <div class="card">
        <h1>Contact Us</h1>

        '''+'''{'''+ '''% if success %}
        <div class="alert alert-success">Message sent!</div>
        '''+'''{'''+ '''% endif %}

        <form method="POST">
            '''+'''{{ csrf() }}  '''+'''<!-- CSRF protection -->

            <div class="form-group">
                <label>Name</label>
                <input type="text" name="name" required>
            </div>

            <div class="form-group">
                <label>Email</label>
                <input type="email" name="email" required>
            </div>

            <div class="form-group">
                <label>Message</label>
                <textarea name="message" rows="5" required></textarea>
            </div>

            <button type="submit" class="btn btn-primary">Send</button>
        </form>
    </div>
</div>
```

**Key points:**
- `methods=['GET', 'POST']` - Accept both methods
- `'''+'''{{ csrf() }}` - Required for security (prevents CSRF attacks)
- `request.method` - Check which HTTP method was used
- `request.form.get('name')` - Access form data

## What's Next?

- **Customize the theme:** Edit `static/css/style.css` (change CSS variables)
- **Learn template syntax:** Read [Template Syntax](02_TEMPLATE_SYNTAX.md)
- **Work with databases:** Read [Database](03_DATABASE.md)
- **Understand authentication:** Read [Authentication](04_AUTHENTICATION.md)

Happy coding! 🚀
'''

    # Write docs/01_GETTING_STARTED.md
    with open(os.path.join(docs_path, '01_GETTING_STARTED.md'), 'w') as f:
        f.write(getting_started)

    # docs/02_TEMPLATE_SYNTAX.md
    template_syntax = '''# Template Syntax Reference

Complete guide to ScribeEngine `.stpl` file syntax.

## Route Declaration

### Basic Routes

```python
@route('/')              # GET request (default)
@route('/about')         # Static path
@route('/api/data')      # Nested path
```

### HTTP Methods

```python
@route('/login', methods=['GET', 'POST'])
@route('/api/users', methods=['GET', 'POST', 'PUT', 'DELETE'])
```

### Route Parameters

```python
@route('/posts/<int:post_id>')                # Integer
@route('/users/<username>')                   # String (default)
@route('/files/<path:filepath>')              # Path (includes slashes)
@route('/product/<uuid:product_id>')          # UUID
```

## Python Blocks

Execute Python code with `'''+'''{$ ... $}`:

```python
'''+'''{$
# Variables
title = "Hello"
items = [1, 2, 3]

# Loops
for item in items:
    process(item)

# Conditionals
if user_id:
    user = db['default'].find('users', user_id)

# Functions
def format_date(date):
    return date.strftime('%Y-%m-%d')
$}
```

### Available Objects

- `request` - Flask request object (form data, headers, method)
- `session` - Flask session (dict-like)
- `db` - Database connections
- `flash()` - Flash messages
- `redirect()` - Redirect to URL
- `abort()` - Return HTTP error
- `jsonify()` - Return JSON response

## Jinja2 Templates

### Variables

```html
<h1>'''+'''{{ page_title }}</h1>
<p>'''+'''{{ user.name }}</p>
<p>'''+'''{{ items[0] }}</p>
```

### Filters

```html
'''+'''{{ name | upper }}                    # UPPERCASE
'''+'''{{ long_text | truncate(100) }}       # Limit length
'''+'''{{ date | default('No date') }}       # Default value
```

### Conditionals

```html
'''+'''{'''+ '''% if user %}
    <p>Welcome, '''+'''{{ user.name }}!</p>
'''+'''{'''+ '''% else %}
    <p>Please log in.</p>
'''+'''{'''+ '''% endif %}
```

### Loops

```html
'''+'''{'''+ '''% for post in posts %}
    <h2>'''+'''{{ post.title }}</h2>
'''+'''{'''+ '''% endfor %}

'''+'''{'''+ '''% for key, value in dict.items() %}
    <p>'''+'''{{ key }}: '''+'''{{ value }}</p>
'''+'''{'''+ '''% endfor %}
```

## Decorators

### @require_auth

Require login:

```python
@route('/dashboard')
@require_auth
'''+'''{$ ... $}
```

Redirects to `/login` if not authenticated.

## Return Statements

### Redirect

```python
'''+'''{$
if not user:
    return redirect('/login')
$}
```

### JSON Response

```python
'''+'''{$
data = {"status": "success", "count": 42}
return jsonify(data)
$}
```

### Abort (HTTP Error)

```python
'''+'''{$
if not authorized:
    return abort(403)  # Forbidden
$}
```

## Layout Inheritance

Use `base.stpl` automatically:

```python
@route('/page')
'''+'''{$
page_title = "My Page"  # Sets <title>
$}

<!-- Content automatically wrapped in base.stpl -->
<h1>Hello!</h1>
```

See [Getting Started](01_GETTING_STARTED.md) for examples.
'''

    # Write docs/02_TEMPLATE_SYNTAX.md
    with open(os.path.join(docs_path, '02_TEMPLATE_SYNTAX.md'), 'w') as f:
        f.write(template_syntax)

    # docs/03_DATABASE.md
    database_guide = '''# Database Guide

Learn how to work with databases in ScribeEngine.

## Configuration

Edit `scribe.json`:

```json
{
  "databases": {
    "default": {
      "type": "sqlite",
      "database": "app.db"
    }
  }
}
```

### Multiple Databases

```json
{
  "databases": {
    "default": {
      "type": "sqlite",
      "database": "app.db"
    },
    "analytics": {
      "type": "postgresql",
      "host": "localhost",
      "port": 5432,
      "user": "dbuser",
      "password": "secret",
      "database": "analytics"
    }
  }
}
```

Access: `db['default']`, `db['analytics']`

## Query Methods

### Raw SQL

```python
'''+'''{$
users = db['default'].query("SELECT * FROM users")
user = db['default'].query(
    "SELECT * FROM users WHERE id = ?",
    (user_id,)
)
$}
```

### Find by ID

```python
'''+'''{$
user = db['default'].find('users', 123)
# Returns: {'id': 123, 'username': 'alice', ...}
$}
```

### Insert

```python
'''+'''{$
user_id = db['default'].insert('users',
    username='alice',
    email='alice@example.com',
    password_hash=hash_password('secret')
)
$}
```

### Update

```python
'''+'''{$
db['default'].update('users',
    {'email': 'newemail@example.com'},
    id=user_id
)
$}
```

### Delete

```python
'''+'''{$
db['default'].delete('users', id=user_id)
$}
```

## Migrations

Create `migrations/002_add_posts.sql`:

```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

Run: `scribe db migrate`

Migrations run in numerical order (001_, 002_, etc.).

## Best Practices

### Always Use Parameterized Queries

```python
# ✅ SAFE
users = db['default'].query(
    "SELECT * FROM users WHERE username = ?",
    (username,)
)

# ❌ DANGEROUS (SQL injection vulnerability)
users = db['default'].query(
    f"SELECT * FROM users WHERE username = '''+'''{username}"
)
```

### Check for Empty Results

```python
'''+'''{$
users = db['default'].query("SELECT * FROM users WHERE id = ?", (user_id,))

if users:
    user = users[0]
else:
    return abort(404)
$}
```

See [Template Syntax](02_TEMPLATE_SYNTAX.md) for more examples.
'''

    # Write docs/03_DATABASE.md
    with open(os.path.join(docs_path, '03_DATABASE.md'), 'w') as f:
        f.write(database_guide)

    # docs/04_AUTHENTICATION.md
    auth_guide = '''# Authentication Guide

Understanding the built-in authentication system.

## How It Works

Your app includes a complete login system:

1. **Login route** (`/login`) - Validates credentials, creates session
2. **Dashboard route** (`/dashboard`) - Protected with `@require_auth`
3. **Logout route** (`/logout`) - Clears session
4. **Session management** - Flask sessions (server-side)
5. **Password hashing** - Werkzeug (scrypt algorithm)

## The Login Flow

### 1. User submits login form

```python
@route('/login', methods=['GET', 'POST'])
'''+'''{$
if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')

    # Look up user
    users = db['default'].query(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )

    if users and verify_password(users[0]['password_hash'], password):
        session['user_id'] = users[0]['id']  # Create session
        return redirect('/dashboard')
$}
```

### 2. Session is stored

ScribeEngine uses Flask sessions (signed cookies by default).

### 3. Protected routes check session

```python
@route('/dashboard')
@require_auth
'''+'''{$
# @require_auth checks if 'user_id' in session
# Redirects to /login if not authenticated
user = db['default'].find('users', session['user_id'])
$}
```

## Password Hashing

**NEVER store plain text passwords!**

### Hash a password

```python
from lib.auth_helpers import hash_password

hashed = hash_password('user_password')
# Store `hashed` in database
```

### Verify a password

```python
from lib.auth_helpers import verify_password

if verify_password(stored_hash, user_input):
    # Password correct
```

## Adding User Registration

```python
@route('/register', methods=['GET', 'POST'])
'''+'''{$
page_title = "Register"
error = None

if request.method == 'POST':
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    # Validation
    if len(username) < 3:
        error = "Username must be at least 3 characters"
    elif len(password) < 8:
        error = "Password must be at least 8 characters"
    else:
        # Check if username exists
        existing = db['default'].query(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        )

        if existing:
            error = "Username already taken"
        else:
            # Create user
            user_id = db['default'].insert('users',
                username=username,
                password_hash=hash_password(password)
            )
            session['user_id'] = user_id
            return redirect('/dashboard')
$}

<form method="POST">
    '''+'''{{ csrf() }}
    <!-- form fields -->
</form>
```

## Removing Authentication

**Don't need auth?** Follow these steps:

1. **Delete auth routes** in `app.stpl`:
   - `/login`
   - `/dashboard`
   - `/logout`

2. **Update `base.stpl` navbar** - replace session check with static links

3. **Delete files:**
   - `lib/auth_helpers.py`
   - `migrations/001_users.sql`

4. **Remove decorators:**
   - Delete `@require_auth` from any custom routes

See [Getting Started](01_GETTING_STARTED.md) for more examples.
'''

    # Write docs/04_AUTHENTICATION.md
    with open(os.path.join(docs_path, '04_AUTHENTICATION.md'), 'w') as f:
        f.write(auth_guide)

    # docs/05_DEPLOYMENT.md
    deployment_guide = '''# Deployment Guide

Deploy your ScribeEngine app to production.

## Production Checklist

Before deploying:

- [ ] Change `secret_key` in `scribe.json` to a random value
- [ ] Use PostgreSQL or MySQL (not SQLite) for production
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Set `debug=False` in Flask
- [ ] Use environment variables for secrets
- [ ] Set up monitoring/logging
- [ ] Configure backups

## Using Production Server

ScribeEngine includes Waitress (production WSGI server):

```bash
scribe serve --host 0.0.0.0 --port 8000 --threads 8
```

**Options:**
- `--host`: IP address (0.0.0.0 = all interfaces)
- `--port`: Port number
- `--threads`: Worker threads

## PostgreSQL Configuration

Edit `scribe.json`:

```json
{
  "databases": {
    "default": {
      "type": "postgresql",
      "host": "localhost",
      "port": 5432,
      "user": "myapp_user",
      "password": "USE_ENV_VARIABLE",
      "database": "myapp_db"
    }
  },
  "secret_key": "USE_ENV_VARIABLE"
}
```

**Don't commit secrets!** Use environment variables.

## Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name myapp.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Systemd Service

Create `/etc/systemd/system/myapp.service`:

```ini
[Unit]
Description=MyApp ScribeEngine
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/myapp
ExecStart=/usr/local/bin/scribe serve --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable myapp
sudo systemctl start myapp
```

See other guides for development workflows.
'''

    # Write docs/05_DEPLOYMENT.md
    with open(os.path.join(docs_path, '05_DEPLOYMENT.md'), 'w') as f:
        f.write(deployment_guide)


@click.group()
@click.version_option(version="2.0.0-alpha")
def cli():
    """ScribeEngine - Write Python directly in templates"""
    pass


@cli.command()
@click.argument('project_name')
@click.option('--path', default='.', help='Parent directory for new project')
def new(project_name, path):
    """
    Create a new ScribeEngine project.

    Example:
        scribe new myapp
        scribe new myblog --path ~/projects
    """
    # Create project directory
    project_path = os.path.join(path, project_name)

    if os.path.exists(project_path):
        click.echo(f"Error: Directory '{project_path}' already exists")
        return

    click.echo(f"Creating new ScribeEngine project: {project_name}")

    # Create directory structure
    os.makedirs(project_path)
    os.makedirs(os.path.join(project_path, 'migrations'))
    os.makedirs(os.path.join(project_path, 'lib'))
    os.makedirs(os.path.join(project_path, 'static'))
    os.makedirs(os.path.join(project_path, 'static', 'css'))
    os.makedirs(os.path.join(project_path, 'static', 'js'))

    # Create scribe.json
    scribe_json = '''{
  "databases": {
    "default": {
      "type": "sqlite",
      "database": "app.db"
    }
  },
  "secret_key": "CHANGE_THIS_TO_A_RANDOM_SECRET_KEY_IN_PRODUCTION"
}
'''
    with open(os.path.join(project_path, 'scribe.json'), 'w') as f:
        f.write(scribe_json)

    # Create base.stpl layout template
    base_stpl = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title | default('My App') }} - ScribeEngine</title>
    <meta name="description" content="{{ page_description | default('Built with ScribeEngine') }}">
    <link rel="stylesheet" href="/static/css/style.css">
    {'''+ '''% block extra_head %}{'''+ '''% endblock %}
</head>
<body>
    <header class="navbar">
        <div class="container">
            <div class="navbar-content">
                <div class="navbar-brand">
                    <a href="/">My App</a>
                </div>

                '''+'''<!-- Auth-aware navigation: Remove this entire block if you don't need auth -->
                <nav class="navbar-links">
                    {'''+ '''% if 'user_id' in session %}
                        '''+'''<!-- Logged in navigation -->
                        <a href="/dashboard">Dashboard</a>
                        <a href="/logout">Logout</a>
                    {'''+ '''% else %}
                        '''+'''<!-- Public navigation -->
                        <a href="/">Home</a>
                        <a href="/about">About</a>
                        <a href="/login">Login</a>
                    {'''+ '''% endif %}
                </nav>
                '''+'''<!-- End auth-aware navbar -->
            </div>
        </div>
    </header>

    <main class="main-content">
        '''+'''<!-- Flash messages -->
        {'''+ '''% with messages = get_flashed_messages(with_categories=true) %}
            {'''+ '''% if messages %}
                <div class="container">
                    {'''+ '''% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {'''+ '''% endfor %}
                </div>
            {'''+ '''% endif %}
        {'''+ '''% endwith %}

        {'''+ '''% block content %}
            '''+'''<!-- Route content goes here -->
        {'''+ '''% endblock %}
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2025 My ScribeEngine App. Built with <a href="https://github.com/yourusername/scribe-engine">ScribeEngine</a>.</p>
        </div>
    </footer>

    {'''+ '''% block extra_scripts %}{'''+ '''% endblock %}
</body>
</html>
'''
    with open(os.path.join(project_path, 'base.stpl'), 'w') as f:
        f.write(base_stpl)

    # Create example app.stpl (using layout system - no HTML boilerplate!)
    app_stpl = '''@route('/')
{$
page_title = "Welcome"
# Redirect to dashboard if already logged in
if 'user_id' in session:
    return redirect('/dashboard')
$}

<div class="hero">
    <div class="container">
        <h1>Welcome to Your ScribeEngine App! 🚀</h1>
        <p class="lead">You're all set up with authentication, database access, and a modern UI.
           Try logging in or start building your first feature.</p>
        <div class="hero-buttons">
            <a href="/login" class="btn btn-primary">Try Login Demo</a>
            <a href="/about" class="btn btn-secondary">Learn More</a>
        </div>
    </div>
</div>

<div class="container-narrow">
    <div class="card">
        <h2>🎯 Quick Start</h2>
        <ul class="checklist">
            <li><strong>Try it out:</strong> Login with <code>testuser</code> / <code>password123</code></li>
            <li><strong>Customize theme:</strong> Edit CSS variables in <code>static/css/style.css</code></li>
            <li><strong>Add routes:</strong> Open <code>app.stpl</code> and create your first route</li>
            <li><strong>Read docs:</strong> Check out the guides in <code>docs/</code> directory</li>
            <li><strong>Don't need auth?</strong> See README.md for removal instructions</li>
        </ul>
    </div>

    <div class="card">
        <h2>📚 Key Concepts</h2>
        <p>ScribeEngine makes web development simple. Here are the core concepts:</p>
        <ul>
            <li><strong>Routes:</strong> Define URL endpoints with <code>&#64;route('/path')</code> decorators</li>
            <li><strong>Python Blocks:</strong> Write server-side code in <code>&lcub;$ ... $&rcub;</code> blocks</li>
            <li><strong>Templates:</strong> Use Jinja2 syntax <code>&lcub;&lcub; variable &rcub;&rcub;</code> to display data</li>
            <li><strong>Database:</strong> Query any database with <code>db['default'].query()</code></li>
            <li><strong>Authentication:</strong> Protect routes with <code>&#64;require_auth</code> decorator</li>
            <li><strong>Forms:</strong> Automatic CSRF protection with <code>&lcub;&lcub; csrf() &rcub;&rcub;</code></li>
        </ul>
        <p>See the <code>docs/</code> directory for detailed examples and tutorials.</p>
    </div>

    <div class="card">
        <h2>🎁 What's Included</h2>
        <ul>
            <li><strong>Authentication:</strong> Login, logout, session management, protected routes</li>
            <li><strong>Database:</strong> SQLite ready to go (easy to upgrade to PostgreSQL/MySQL)</li>
            <li><strong>Modern UI:</strong> Responsive design with CSS variable theming</li>
            <li><strong>Security:</strong> CSRF tokens, password hashing, secure sessions</li>
            <li><strong>Documentation:</strong> Complete guides in the <code>docs/</code> folder</li>
        </ul>
    </div>

    <div class="card">
        <h2>🚀 Next Steps</h2>
        <ol>
            <li><a href="/login">Try the login demo</a> to see authentication in action</li>
            <li>Read <code>docs/01_GETTING_STARTED.md</code> for a tutorial</li>
            <li>Customize the theme by changing CSS variables</li>
            <li>Add your first custom route</li>
            <li>Build something amazing!</li>
        </ol>
    </div>
</div>


'''+'''# ================================================================
# AUTHENTICATION ROUTES
# To remove authentication:
#   1. Delete everything between these markers
#   2. Remove @require_auth decorators from your custom routes
#   3. Delete lib/auth_helpers.py
#   4. Delete migrations/001_users.sql
#   5. Update navbar in base.stpl (remove session check)
# ================================================================

'''+'''@route('/login', methods=['GET', 'POST'])
{$
page_title = "Login"
error = None

# Redirect if already logged in
if 'user_id' in session:
    return redirect('/dashboard')

if request.method == 'POST':
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    # Query database for user
    users = db['default'].query(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )

    if users:
        user = users[0]
        # Verify password using helper function (from lib/auth_helpers.py)
        if verify_password(user['password_hash'], password):
            session['user_id'] = user['id']
            flash('Login successful!', 'success')
            return redirect('/dashboard')
        else:
            error = "Invalid password"
    else:
        error = "User not found"
$}

<div class="container-narrow">
    <div class="card">
        <h2>Login</h2>

        {'''+ '''% if error %}
        <div class="alert alert-error">{{ error }}</div>
        {'''+ '''% endif %}

        <form method="POST">
            {'''+ '''{ csrf() }}

            <div class="form-group">
                <label for="username">Username</label>
                <input
                    type="text"
                    id="username"
                    name="username"
                    value="{'''+ '''{ request.form.get('username', '') }}"
                    required
                    autofocus
                >
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input
                    type="password"
                    id="password"
                    name="password"
                    required
                >
            </div>

            <button type="submit" class="btn btn-primary btn-block">Login</button>
        </form>

        <div class="help-text">
            <p><strong>Test credentials:</strong></p>
            <ul>
                <li>Username: <code>testuser</code></li>
                <li>Password: <code>password123</code></li>
            </ul>
        </div>

        <p class="text-center"><a href="/">← Back to Home</a></p>
    </div>
</div>


@route('/dashboard')
@require_auth
{$
page_title = "Dashboard"
# Load current user from database
user = db['default'].query(
    "SELECT * FROM users WHERE id = ?",
    (session['user_id'],)
)[0]
$}

<div class="container">
    <div class="card">
        <h1>Welcome, {'''+ '''{ user['username'] }}! 👋</h1>

        <div class="user-info">
            <p><strong>User ID:</strong> {'''+ '''{ user['id'] }}</p>
            <p><strong>Username:</strong> {'''+ '''{ user['username'] }}</p>
            <p><strong>Account created:</strong> {'''+ '''{ user['created_at'] }}</p>
        </div>

        <div class="info-box">
            <h3>🔐 About This Page</h3>
            <p>This route is protected by the <code>@require_auth</code> decorator.
               Only logged-in users can see this page.</p>
            <p>Your session contains: <code>session['user_id'] = {'''+ '''{ session['user_id'] }}</code></p>
        </div>

        <div class="actions">
            <a href="/logout" class="btn btn-secondary">Logout</a>
        </div>
    </div>

    <div class="card">
        <h2>What to Build Next?</h2>
        <ul>
            <li>Add a profile editing page</li>
            <li>Create a user registration flow</li>
            <li>Build a password reset feature</li>
            <li>Add role-based permissions</li>
            <li>Or remove auth entirely and build your own app!</li>
        </ul>
        <p>See <code>docs/04_AUTHENTICATION.md</code> for examples.</p>
    </div>
</div>


@route('/logout')
{$
session.pop('user_id', None)
flash('You have been logged out successfully', 'info')
return redirect('/login')
$}


'''+'''# ================================================================
# END AUTHENTICATION ROUTES
# ================================================================


'''+'''@route('/about')
{$
page_title = "About"
page_description = "Learn about this ScribeEngine application"
$}

<div class="container-narrow">
    <div class="card">
        <h1>About This Project</h1>

        <p>This is a ScribeEngine web application. ScribeEngine lets you write Python
           directly in templates, eliminating boilerplate and making web development fast.</p>

        <h2>Framework Features</h2>
        <ul>
            <li>Write Python in templates with <code>&lcub;$ ... $&rcub;</code> blocks</li>
            <li>Define routes using <code>&#64;route()</code> decorators</li>
            <li>Built-in authentication and security</li>
            <li>Unified database API (SQLite, PostgreSQL, MySQL, MSSQL)</li>
            <li>Automatic CSRF protection</li>
            <li>Session management included</li>
            <li>Hot-reload development server</li>
        </ul>

        <h2>Learn More</h2>
        <p>Explore the documentation in the <code>docs/</code> directory:</p>
        <ul>
            <li><code>01_GETTING_STARTED.md</code> - Tutorial for beginners</li>
            <li><code>02_TEMPLATE_SYNTAX.md</code> - Complete syntax reference</li>
            <li><code>03_DATABASE.md</code> - Working with databases</li>
            <li><code>04_AUTHENTICATION.md</code> - Auth system guide</li>
            <li><code>05_DEPLOYMENT.md</code> - Production deployment</li>
        </ul>

        <p class="text-center"><a href="/">← Back to Home</a></p>
    </div>
</div>
'''
    with open(os.path.join(project_path, 'app.stpl'), 'w') as f:
        f.write(app_stpl)

    # Create modern CSS file with CSS variables
    css = '''/* ================================================================
   SCRIBEENGINE - DEFAULT THEME

   CUSTOMIZE THIS:
   Change the CSS variables below to customize colors, spacing, etc.

   QUICK THEME CHANGES:
   - Blue theme (default): --primary-color: #2563eb
   - Green theme: --primary-color: #10b981
   - Purple theme: --primary-color: #8b5cf6
   - Red theme: --primary-color: #ef4444

   Change just ONE variable to transform the entire color scheme!
   ================================================================ */

:root {
    /* Primary Colors - Change these for instant theme updates */
    --primary-color: #2563eb;
    --primary-hover: #1d4ed8;
    --primary-light: #dbeafe;
    --primary-dark: #1e40af;

    /* Neutral Colors */
    --bg-color: #f8fafc;
    --surface-color: #ffffff;
    --text-color: #1e293b;
    --text-muted: #64748b;
    --border-color: #e2e8f0;

    /* Semantic Colors */
    --success-color: #10b981;
    --success-bg: #d1fae5;
    --error-color: #ef4444;
    --error-bg: #fee2e2;
    --warning-color: #f59e0b;
    --warning-bg: #fef3c7;
    --info-color: #3b82f6;
    --info-bg: #dbeafe;

    /* Spacing Scale (based on 4px grid) */
    --spacing-xs: 0.25rem;   /* 4px */
    --spacing-sm: 0.5rem;    /* 8px */
    --spacing-md: 1rem;      /* 16px */
    --spacing-lg: 1.5rem;    /* 24px */
    --spacing-xl: 2rem;      /* 32px */
    --spacing-2xl: 3rem;     /* 48px */

    /* Typography */
    --font-body: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
    --font-mono: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", monospace;
    --font-size-sm: 0.875rem;
    --font-size-base: 1rem;
    --font-size-lg: 1.125rem;
    --font-size-xl: 1.25rem;
    --font-size-2xl: 1.5rem;
    --font-size-3xl: 1.875rem;

    /* Borders & Shadows */
    --radius-sm: 0.25rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);

    /* Layout */
    --container-max-width: 1200px;
    --container-narrow-width: 600px;
}


/* ================================================================
   BASE STYLES
   ================================================================ */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html {
    font-size: 16px;
    height: 100%;
}

body {
    font-family: var(--font-body);
    font-size: var(--font-size-base);
    line-height: 1.6;
    color: var(--text-color);
    background: var(--bg-color);
    min-height: 100%;
    display: flex;
    flex-direction: column;
}

.main-content {
    flex: 1;
    padding: var(--spacing-xl) 0;
}

h1, h2, h3, h4, h5, h6 {
    margin-top: 0;
    margin-bottom: var(--spacing-md);
    color: var(--text-color);
    font-weight: 600;
}

h1 { font-size: var(--font-size-3xl); }
h2 { font-size: var(--font-size-2xl); }
h3 { font-size: var(--font-size-xl); }


/* ================================================================
   NAVIGATION
   ================================================================ */

.navbar {
    background: var(--surface-color);
    border-bottom: 1px solid var(--border-color);
    padding: var(--spacing-md) 0;
    box-shadow: var(--shadow-sm);
}

.navbar-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.navbar-brand a {
    font-size: var(--font-size-xl);
    font-weight: 700;
    color: var(--primary-color);
    text-decoration: none;
}

.navbar-links {
    display: flex;
    gap: var(--spacing-lg);
}

.navbar-links a {
    color: var(--text-color);
    text-decoration: none;
    font-weight: 500;
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius-md);
    transition: background-color 0.2s, color 0.2s;
}

.navbar-links a:hover {
    background: var(--primary-light);
    color: var(--primary-color);
}


/* ================================================================
   CONTAINERS
   ================================================================ */

.container {
    max-width: var(--container-max-width);
    margin: 0 auto;
    padding: 0 var(--spacing-lg);
}

.container-narrow {
    max-width: var(--container-narrow-width);
    margin: 0 auto;
    padding: 0 var(--spacing-lg);
}


/* ================================================================
   CARDS
   ================================================================ */

.card {
    background: var(--surface-color);
    border-radius: var(--radius-lg);
    padding: var(--spacing-xl);
    box-shadow: var(--shadow-md);
    margin-bottom: var(--spacing-xl);
}

.card h2 {
    color: var(--primary-color);
    margin-bottom: var(--spacing-md);
}


/* ================================================================
   FORMS
   ================================================================ */

.form-group {
    margin-bottom: var(--spacing-lg);
}

.form-group label {
    display: block;
    margin-bottom: var(--spacing-sm);
    font-weight: 600;
    color: var(--text-color);
}

.form-group input[type="text"],
.form-group input[type="email"],
.form-group input[type="password"],
.form-group input[type="number"],
.form-group textarea,
.form-group select {
    width: 100%;
    padding: var(--spacing-md);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    font-size: var(--font-size-base);
    font-family: var(--font-body);
    transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px var(--primary-light);
}


/* ================================================================
   BUTTONS
   ================================================================ */

.btn {
    display: inline-block;
    padding: var(--spacing-md) var(--spacing-xl);
    border: none;
    border-radius: var(--radius-md);
    font-size: var(--font-size-base);
    font-weight: 600;
    text-decoration: none;
    text-align: center;
    cursor: pointer;
    transition: background-color 0.2s, transform 0.1s;
}

.btn:active {
    transform: translateY(1px);
}

.btn-primary {
    background: var(--primary-color);
    color: white;
}

.btn-primary:hover {
    background: var(--primary-hover);
    text-decoration: none;
}

.btn-secondary {
    background: var(--text-muted);
    color: white;
}

.btn-secondary:hover {
    background: var(--text-color);
    text-decoration: none;
}

.btn-block {
    display: block;
    width: 100%;
}


/* ================================================================
   ALERTS
   ================================================================ */

.alert {
    padding: var(--spacing-md) var(--spacing-lg);
    border-radius: var(--radius-md);
    margin-bottom: var(--spacing-lg);
    border-left: 4px solid;
}

.alert-success {
    background: var(--success-bg);
    color: var(--success-color);
    border-color: var(--success-color);
}

.alert-error {
    background: var(--error-bg);
    color: var(--error-color);
    border-color: var(--error-color);
}

.alert-info {
    background: var(--info-bg);
    color: var(--info-color);
    border-color: var(--info-color);
}

.alert-warning {
    background: var(--warning-bg);
    color: var(--warning-color);
    border-color: var(--warning-color);
}


/* ================================================================
   HERO SECTION
   ================================================================ */

.hero {
    text-align: center;
    padding: var(--spacing-2xl) var(--spacing-lg);
    margin-bottom: var(--spacing-xl);
}

.hero h1 {
    font-size: var(--font-size-3xl);
    color: var(--primary-color);
    margin-bottom: var(--spacing-md);
}

.hero .lead {
    font-size: var(--font-size-lg);
    color: var(--text-muted);
    max-width: 600px;
    margin: 0 auto var(--spacing-xl);
}

.hero-buttons {
    display: flex;
    gap: var(--spacing-md);
    justify-content: center;
    flex-wrap: wrap;
}


/* ================================================================
   UTILITIES
   ================================================================ */

.text-center {
    text-align: center;
}

.text-muted {
    color: var(--text-muted);
}

code {
    background: var(--bg-color);
    padding: 0.2em 0.4em;
    border-radius: var(--radius-sm);
    font-family: var(--font-mono);
    font-size: 0.9em;
    color: var(--primary-dark);
}

pre {
    background: var(--bg-color);
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
    overflow-x: auto;
    margin: var(--spacing-md) 0;
}

pre code {
    background: none;
    padding: 0;
}

ul, ol {
    margin-left: var(--spacing-xl);
    margin-bottom: var(--spacing-md);
}

li {
    margin-bottom: var(--spacing-sm);
}

a {
    color: var(--primary-color);
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

.checklist {
    list-style: none;
    margin-left: 0;
}

.checklist li {
    margin-bottom: var(--spacing-md);
}

.concept-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-lg);
    margin-top: var(--spacing-md);
}

.concept {
    padding: var(--spacing-md);
    background: var(--bg-color);
    border-radius: var(--radius-md);
}

.concept h3 {
    font-size: var(--font-size-lg);
    margin-bottom: var(--spacing-sm);
}

.concept p {
    margin-bottom: var(--spacing-sm);
}

.user-info {
    margin: var(--spacing-lg) 0;
    padding: var(--spacing-md);
    background: var(--bg-color);
    border-radius: var(--radius-md);
}

.info-box {
    padding: var(--spacing-md);
    background: var(--info-bg);
    border-left: 4px solid var(--info-color);
    border-radius: var(--radius-md);
    margin: var(--spacing-lg) 0;
}

.actions {
    margin-top: var(--spacing-lg);
}

.help-text {
    margin-top: var(--spacing-lg);
    padding: var(--spacing-md);
    background: var(--bg-color);
    border-radius: var(--radius-md);
}


/* ================================================================
   FOOTER
   ================================================================ */

.footer {
    background: var(--surface-color);
    border-top: 1px solid var(--border-color);
    padding: var(--spacing-xl) 0;
    margin-top: var(--spacing-2xl);
    text-align: center;
    color: var(--text-muted);
}

.footer p {
    margin: 0;
}

.footer a {
    color: var(--text-muted);
}

.footer a:hover {
    color: var(--primary-color);
}


/* ================================================================
   RESPONSIVE
   ================================================================ */

@media (max-width: 768px) {
    .navbar-content {
        flex-direction: column;
        gap: var(--spacing-md);
    }

    .navbar-links {
        flex-wrap: wrap;
        justify-content: center;
    }

    .hero h1 {
        font-size: var(--font-size-2xl);
    }

    .hero-buttons {
        flex-direction: column;
    }

    .concept-grid {
        grid-template-columns: 1fr;
    }
}
'''
    with open(os.path.join(project_path, 'static', 'css', 'style.css'), 'w') as f:
        f.write(css)

    # Create auth helpers
    auth_helpers = '''"""Authentication helpers - auto-loaded into all templates"""
from werkzeug.security import check_password_hash, generate_password_hash


def verify_password(password_hash, password):
    """Verify password against hash"""
    if password is None or password_hash is None:
        return False
    return check_password_hash(password_hash, password)


def hash_password(password):
    """Hash a password for storage"""
    return generate_password_hash(password)
'''
    with open(os.path.join(project_path, 'lib', 'auth_helpers.py'), 'w') as f:
        f.write(auth_helpers)

    # Create users migration
    users_sql = '''-- Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test user (username: testuser, password: password123)
-- Hash generated with: python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('password123'))"
INSERT INTO users (username, password_hash) VALUES
    ('testuser', 'scrypt:32768:8:1$OhTY8rE77QY4MtSc$77cb268086ae09558d05ce5d3e7aec2ce5446e2b4c7170ba2e556fa0b371023eebdd540cc8317e17790bb7420f6c93e9553f7dd8b11a88454ab56f0952fa4134');
'''
    with open(os.path.join(project_path, 'migrations', '001_users.sql'), 'w') as f:
        f.write(users_sql)

    # Create README
    readme = f'''# {project_name}

A ScribeEngine web application with authentication, database, and modern UI.

## Quick Start

```bash
scribe dev
```

Then open http://localhost:5000

**Test login:**
- Username: `testuser`
- Password: `password123`

## Project Structure

```
{project_name}/
├── app.stpl              # Routes and templates
├── base.stpl             # HTML layout
├── scribe.json           # Configuration
├── lib/                  # Helper functions
│   └── auth_helpers.py   # Password utilities
├── migrations/           # Database schema
│   └── 001_users.sql     # Users table
├── static/               # CSS, JS, images
│   └── css/style.css     # Styles (with CSS variables)
├── docs/                 # Documentation
└── app.db                # SQLite database (auto-created)
```

## Customizing the Theme

Edit `static/css/style.css` and change CSS variables:

```css
:root '''+'''{
  --primary-color: #10b981;  /* Change to green */
  --primary-hover: #059669;
}
```

One variable change updates the entire theme!

## Removing Authentication

**Don't need login/logout?**

1. Delete auth routes in `app.stpl` (marked with comments)
2. Update navbar in `base.stpl` (remove session check)
3. Delete `lib/auth_helpers.py`
4. Delete `migrations/001_users.sql`

See `docs/04_AUTHENTICATION.md` for details.

## Documentation

- `docs/01_GETTING_STARTED.md` - Tutorial for beginners
- `docs/02_TEMPLATE_SYNTAX.md` - Complete syntax reference
- `docs/03_DATABASE.md` - Database guide
- `docs/04_AUTHENTICATION.md` - Auth system guide
- `docs/05_DEPLOYMENT.md` - Production deployment

## Adding Routes

Edit `app.stpl` and add routes using the `@route()` decorator:

```python
@route('/hello/<name>')
'''+'''{$
greeting = f"Hello, '''+'''{name}!"
$}

<h1>'''+'''{{ greeting }}</h1>
```

## Database Operations

```python
@route('/users')
{$
users = db['default'].query("SELECT * FROM users")
$}

{'''+ '''% for user in users %}
    <div>'''+'''{{ user['username'] }}</div>
{'''+ '''% endfor %}
```

## Learn More

- Full documentation: `new-architecture/` directory
- GitHub: https://github.com/yourusername/scribe-engine
'''
    with open(os.path.join(project_path, 'README.md'), 'w') as f:
        f.write(readme)

    # Create .gitignore
    gitignore = '''# Database
*.db
*.sqlite
*.sqlite3

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# ScribeEngine
scribe.json  # May contain secrets
'''
    with open(os.path.join(project_path, '.gitignore'), 'w') as f:
        f.write(gitignore)

    # Create documentation
    create_docs(project_path, project_name)

    click.echo(f"\n✓ Created project: {project_name}")
    click.echo(f"\nNext steps:")
    click.echo(f"  cd {project_name}")
    click.echo(f"  scribe dev")
    click.echo(f"\nThen:")
    click.echo(f"  1. Open http://localhost:5000")
    click.echo(f"  2. Login with: testuser / password123")
    click.echo(f"  3. Read docs/ directory for guides")
    click.echo(f"\nTo remove authentication, see README.md")


@cli.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=5000, type=int, help='Port to bind to')
@click.option('--debug/--no-debug', default=True, help='Enable debug mode')
@click.option('--path', default='.', help='Project directory')
def dev(host, port, debug, path):
    """
    Run development server.

    Example:
        scribe dev
        scribe dev --port 8000
        scribe dev --host 0.0.0.0 --no-debug
    """
    from scribe.app import create_app
    from scribe.migrations import run_migrations

    click.echo(f"Starting ScribeEngine development server...")
    click.echo(f"Project: {os.path.abspath(path)}")

    # Create Flask app
    app = create_app(path)

    # Run migrations
    click.echo("\nApplying database migrations...")
    db = app.config['DB']
    run_migrations(db, path)

    # Start server
    click.echo(f"\n✓ Server running at http://{host}:{port}")
    click.echo(f"  Press CTRL+C to quit\n")

    app.run(host=host, port=port, debug=debug)


@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8000, type=int, help='Port to bind to')
@click.option('--threads', default=4, type=int, help='Number of threads')
@click.option('--path', default='.', help='Project directory')
def serve(host, port, threads, path):
    """
    Run production server using Waitress.

    Uses the Waitress WSGI server - production-ready, multi-threaded,
    and fully self-contained. No external dependencies required.

    Example:
        scribe serve
        scribe serve --host 0.0.0.0 --port 8000
        scribe serve --threads 8
    """
    from scribe.app import create_app
    from scribe.migrations import run_migrations
    from waitress import serve as waitress_serve

    click.echo(f"Starting ScribeEngine production server...")
    click.echo(f"Project: {os.path.abspath(path)}")

    # Create Flask app
    app = create_app(path)

    # Run migrations
    click.echo("\nApplying database migrations...")
    db = app.config['DB']
    run_migrations(db, path)

    # Start server
    click.echo(f"\n✓ Production server running at http://{host}:{port}")
    click.echo(f"  Server: Waitress (production WSGI)")
    click.echo(f"  Threads: {threads}")
    click.echo(f"  Press CTRL+C to quit\n")

    # Run with Waitress - production-ready WSGI server
    waitress_serve(app, host=host, port=port, threads=threads)


@cli.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to (default: localhost only)')
@click.option('--port', default=5001, type=int, help='Port to bind to')
@click.option('--path', default='.', help='Project directory')
@click.option('--no-reload', is_flag=True, help='Disable auto-reload on file changes')
def gui(host, port, path, no_reload):
    """
    Launch the ScribeEngine IDE (web-based code editor).

    Opens a browser-based development environment with:
    - Code editor with .stpl syntax highlighting
    - Live preview panel
    - Database browser
    - File management
    - Auto-reload on file changes

    By default, only accessible on localhost (127.0.0.1) for security.

    Example:
        scribe gui
        scribe gui --port 5001
        scribe gui --host 0.0.0.0  # Allow remote access (use with caution)
        scribe gui --no-reload     # Disable auto-reload
    """
    from scribe.app import create_app
    from scribe.migrations import run_migrations
    import webbrowser
    import threading

    click.echo(f"Starting ScribeEngine IDE...")
    click.echo(f"Project: {os.path.abspath(path)}")

    # Security warning if not localhost
    if host != '127.0.0.1' and host != 'localhost':
        click.echo("\n⚠️  WARNING: IDE is accessible from other machines!")
        click.echo("   Only use --host 0.0.0.0 on trusted networks.")
        click.echo("   Consider adding authentication for remote access.\n")

    # Create Flask app
    app = create_app(path)

    # Run migrations
    click.echo("\nApplying database migrations...")
    db = app.config['DB']
    run_migrations(db, path)

    # Open browser after a short delay
    ide_url = f"http://{host}:{port}/__scribe_gui"

    def open_browser():
        import time
        import os
        # Only open browser in main process, not reloader process
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            time.sleep(1.5)  # Wait for server to start
            click.echo(f"\nOpening IDE in browser: {ide_url}")
            webbrowser.open(ide_url)

    threading.Thread(target=open_browser, daemon=True).start()

    # Configure auto-reload to watch project files
    extra_files = []
    if not no_reload:
        import glob
        # Watch .stpl template files
        extra_files.extend(glob.glob(os.path.join(path, '**/*.stpl'), recursive=True))
        # Watch lib/ Python files
        extra_files.extend(glob.glob(os.path.join(path, 'lib/**/*.py'), recursive=True))
        # Watch migrations
        extra_files.extend(glob.glob(os.path.join(path, 'migrations/**/*.sql'), recursive=True))
        # Watch config
        config_file = os.path.join(path, 'scribe.json')
        if os.path.exists(config_file):
            extra_files.append(config_file)

        click.echo(f"  Watching {len(extra_files)} project files for changes")

    # Start server
    click.echo(f"\n✓ IDE server running at {ide_url}")
    if not no_reload:
        click.echo(f"  Auto-reload: ENABLED (server will restart on file changes)")
    else:
        click.echo(f"  Auto-reload: DISABLED")
    click.echo(f"  Press CTRL+C to quit\n")

    app.run(
        host=host,
        port=port,
        debug=True,
        use_reloader=not no_reload,
        extra_files=extra_files if not no_reload else None
    )


@cli.group(name='db')
def db_commands():
    """Database management commands"""
    pass


@db_commands.command()
@click.option('--path', default='.', help='Project directory')
def migrate(path):
    """
    Run database migrations.

    Example:
        scribe db migrate
    """
    from scribe.app import load_config
    from scribe.database import create_adapter
    from scribe.migrations import run_migrations

    click.echo("Running database migrations...")

    # Load config
    config = load_config(path)

    # Create database adapter
    db = create_adapter(config.get('database', {'type': 'sqlite', 'database': 'app.db'}))

    # Run migrations
    run_migrations(db, path)

    db.close()


@db_commands.command()
@click.argument('name')
@click.option('--path', default='.', help='Project directory')
def new_migration(name, path):
    """
    Create a new migration file.

    Example:
        scribe db new-migration create_users
    """
    from scribe.migrations import create_migration

    filepath = create_migration(path, name)
    click.echo(f"\n✓ Created migration: {filepath}")
    click.echo(f"\nEdit the file to add your SQL statements, then run:")
    click.echo(f"  scribe db migrate")


@cli.command()
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation prompt')
def uninstall(yes):
    """
    Uninstall ScribeEngine from your system.

    This removes the scribe executable from your PATH.

    Example:
        scribe uninstall
        scribe uninstall -y
    """
    import shutil

    # Find where this executable is located
    executable_path = shutil.which('scribe')

    if not executable_path:
        click.echo("ScribeEngine is not installed (scribe command not found in PATH)")
        return

    click.echo(f"ScribeEngine is installed at: {executable_path}")

    if not yes:
        if not click.confirm("\nAre you sure you want to uninstall ScribeEngine?"):
            click.echo("Uninstall cancelled")
            return

    try:
        # Remove the executable
        os.remove(executable_path)
        click.echo(f"\n✓ Successfully uninstalled ScribeEngine")
        click.echo(f"  Removed: {executable_path}")
        click.echo("\nThank you for using ScribeEngine!")

    except PermissionError:
        click.echo(f"\n✗ Permission denied. The executable is in a system directory.")
        click.echo(f"  Try running with sudo:")
        click.echo(f"  sudo scribe uninstall")

    except Exception as e:
        click.echo(f"\n✗ Error during uninstall: {e}")
        click.echo(f"  You may need to manually remove: {executable_path}")


if __name__ == '__main__':
    cli()
