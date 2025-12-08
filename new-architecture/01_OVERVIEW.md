# ScribeEngine - Overview

## What is ScribeEngine?

ScribeEngine is a **Python web framework** that lets you write Python code directly in your templates, eliminating the boilerplate of traditional MVC frameworks while maintaining clean separation of concerns.

### The Problem It Solves

Traditional web frameworks require:
- Separate route definitions
- Separate controller files
- Separate view templates
- API layers for simple data fetching
- Complex configuration

**ScribeEngine asks:** What if you could just write Python where you need it?

---

## Core Philosophy

### 1. **Write Python Where You Need It**

```python
@route('/dashboard')
@require_auth
{$
user = db.find('users', session['user_id'])
recent_posts = db.table('posts').where(user_id=user['id']).limit(5).all()
unread_count = db.table('notifications').where(user_id=user['id'], read=False).count()
$}

<div class="dashboard">
    <h1>Welcome, {{ user['name'] }}</h1>
    <p>You have {{ unread_count }} unread notifications</p>

    {% for post in recent_posts %}
        <article>{{ post['title'] }}</article>
    {% endfor %}
</div>
```

**No separate route file. No controller. No API endpoint. Just write what you need.**

### 2. **Sensible Defaults, Zero Configuration**

```bash
scribe new blog
cd blog
scribe dev
# Your app is running at http://localhost:5000
```

SQLite configured. Migrations ready. Session management enabled. CSRF protection active.

### 3. **Progressive Complexity**

**Simple apps:** Everything in one file
```
blog/
├── scribe.json
├── app.stpl       # All routes here
└── migrations/
```

**Growing apps:** Organize as needed
```
blog/
├── scribe.json
├── routes/
│   ├── auth.stpl
│   ├── posts.stpl
│   └── admin.stpl
├── lib/
│   ├── auth.py
│   └── models.py
└── migrations/
```

### 4. **Escape Hatches Everywhere**

Can't do something with ScribeEngine helpers? Drop to Flask:

```python
@route('/api/upload', methods=['POST'])
{$
from flask import current_app, send_file
# Full Flask API available
$}
```

Need complex SQL? Write it:

```python
{$
results = db.execute("""
    SELECT p.*, u.name as author
    FROM posts p
    JOIN users u ON p.user_id = u.id
    WHERE p.published = true
    ORDER BY p.created_at DESC
""")
$}
```

---

## What Makes ScribeEngine Different?

### vs. Flask

**Flask:**
```python
# app.py
from flask import Flask, render_template, session
app = Flask(__name__)

@app.route('/dashboard')
def dashboard():
    user = User.query.get(session['user_id'])
    posts = Post.query.filter_by(user_id=user.id).limit(5).all()
    return render_template('dashboard.html', user=user, posts=posts)

# templates/dashboard.html
<h1>Welcome, {{ user.name }}</h1>
```

**ScribeEngine:**
```python
# routes/dashboard.stpl
@route('/dashboard')
{$
user = db.find('users', session['user_id'])
posts = db.table('posts').where(user_id=user['id']).limit(5).all()
$}

<h1>Welcome, {{ user['name'] }}</h1>
```

**Difference:** No separate files. Logic lives with the template.

### vs. Django

**Django:**
- Must learn ORM (can't use raw SQL easily)
- Heavy configuration
- Opinionated project structure
- Steep learning curve

**ScribeEngine:**
- Use raw SQL or query builder (your choice)
- Minimal configuration
- Flexible structure
- Gentle learning curve

### vs. PHP

**PHP:**
```php
<?php
$user = db->query("SELECT * FROM users WHERE id = ?", [$_SESSION['user_id']]);
?>
<h1>Welcome, <?= $user['name'] ?></h1>
```

**ScribeEngine:**
```python
{$ user = db.find('users', session['user_id']) $}
<h1>Welcome, {{ user['name'] }}</h1>
```

**Similarity:** Inline logic in templates
**Difference:** Python's rich ecosystem, type safety, better tooling

---

## Key Features

### 1. **Inline Python Execution**

Write Python in templates using `{$ ... $}` blocks:

```python
{$
# Any Python code
user = db.find('users', 1)
posts = [p for p in db.all('posts') if p['user_id'] == user['id']]
import datetime
today = datetime.date.today()
$}
```

### 2. **Route Decorators**

Define routes with decorator syntax:

```python
@route('/posts/<int:post_id>')
{$
post = db.find('posts', post_id)
comments = db.table('comments').where(post_id=post_id).all()
$}
```

### 3. **Auto-Loading Modules**

Drop Python files in `lib/` directory:

```python
# lib/auth.py
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# Automatically available in all templates:
{$ hashed = hash_password('secret') $}
```

### 4. **Multi-Database Support**

**SQLite (default):**
```json
{
  "database": {
    "type": "sqlite",
    "path": "data/app.db"
  }
}
```

**PostgreSQL:**
```json
{
  "database": {
    "type": "postgresql",
    "host": "localhost",
    "database": "myapp",
    "user": "postgres",
    "password": "secret"
  }
}
```

**MySQL, MSSQL, Oracle** - all supported via SQLAlchemy.

### 5. **Migration System**

Drop SQL files in `migrations/`:

```sql
-- migrations/001_create_users.sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Run automatically on startup or via CLI:
```bash
scribe db migrate
```

### 6. **Built-in Authentication**

```python
@route('/login', methods=['GET', 'POST'])
{$
if request.method == 'POST':
    if auth.login(request.form['email'], request.form['password']):
        return redirect('/dashboard')
    else:
        error = "Invalid credentials"
$}

<form method="POST">
    {{ csrf() }}
    <input name="email" type="email">
    <input name="password" type="password">
    <button>Login</button>
</form>
```

Protected routes:
```python
@route('/dashboard')
@require_auth
{$ ... $}
```

### 7. **Integrated IDE**

```bash
scribe ide
```

Opens web-based IDE with:
- Code editor (Monaco/VS Code editor)
- Live preview
- Database browser
- Migration manager
- File manager
- Build tools

### 8. **Executable Builds**

```bash
scribe build
```

Creates standalone executable (PyInstaller) with embedded Python runtime. Distribute without "install Python".

---

## When to Use ScribeEngine

### ✅ **Great For:**

- **Internal tools** - CRUD apps, admin panels, dashboards
- **Prototypes** - Get working app in minutes
- **Small to medium apps** - Blogs, portfolios, simple SaaS
- **Data-driven apps** - Reports, analytics, visualizations
- **Learning web development** - Gentle introduction to Python web apps
- **Teams that know SQL** - No ORM to learn

### ⚠️ **Maybe Not For:**

- **Large teams** - Might prefer stricter separation of concerns
- **Complex SPAs** - Consider React/Vue + API backend instead
- **High-performance needs** - Though Flask underneath is quite fast
- **Strict MVC requirements** - This breaks traditional MVC pattern

---

## Design Principles

### 1. **Convention over Configuration**

Sensible defaults for:
- Project structure
- Database location
- Session management
- CSRF protection
- Template locations

Override anything via `scribe.json`.

### 2. **Explicit is Better Than Implicit**

```python
# Explicit route declaration
@route('/posts/<int:post_id>')

# Explicit database queries
user = db.find('users', 1)  # Clear what's happening

# Explicit redirects
return redirect('/dashboard')
```

No hidden magic. Clear what each line does.

### 3. **Python All The Way**

- Write Python in templates
- Write Python in helper modules
- Configure with JSON (not XML, YAML, or DSLs)
- Migrations are SQL (not Python DSL)

### 4. **Web Standards**

- HTTP methods (GET, POST, PUT, DELETE)
- HTTP status codes (200, 302, 404, 500)
- HTTP headers (Content-Type, Location, etc.)
- Standard form encoding
- Standard cookie/session handling

### 5. **Security by Default**

- CSRF protection automatic
- SQL injection prevention (parameterized queries)
- Password hashing helpers
- Session security
- XSS prevention (Jinja2 auto-escaping)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    ScribeEngine                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐      ┌──────────────┐              │
│  │   .stpl      │──┬──▶│   Template   │              │
│  │   Files      │  │   │   Parser     │              │
│  └──────────────┘  │   └──────────────┘              │
│                    │          │                        │
│  ┌──────────────┐  │          ▼                        │
│  │   lib/*.py   │──┤   ┌──────────────┐              │
│  │   Files      │  │   │   Flask      │              │
│  └──────────────┘  │   │   Routes     │              │
│                    │   └──────────────┘              │
│  ┌──────────────┐  │          │                        │
│  │ scribe.json  │──┘          ▼                        │
│  └──────────────┘      ┌──────────────┐              │
│                        │   Database   │              │
│                        │   Layer      │              │
│                        └──────────────┘              │
│                               │                        │
│                        ┌──────┴────────┐              │
│                        ▼               ▼              │
│                   ┌────────┐      ┌────────┐         │
│                   │ SQLite │      │ PostgreSQL       │
│                   └────────┘      │ MySQL  │         │
│                                   │ MSSQL  │         │
│                                   └────────┘         │
└─────────────────────────────────────────────────────────┘
```

**Flow:**
1. Parse `.stpl` files → Extract routes, Python blocks, templates
2. Generate Flask routes dynamically
3. On request → Execute Python block → Render Jinja2 template
4. Auto-load `lib/*.py` modules into execution context
5. Database abstraction layer supports multiple backends

---

## Technology Stack

- **Core:** Python 3.10+
- **Web Framework:** Flask 3.x
- **Template Engine:** Jinja2 3.x
- **Database:**
  - SQLite (built-in)
  - SQLAlchemy 2.x (for PostgreSQL, MySQL, MSSQL)
- **IDE:**
  - Monaco Editor (VS Code editor component)
  - Flask backend for file operations
- **Build:** PyInstaller 6.x
- **Security:** Flask-WTF (CSRF), Werkzeug (password hashing)

---

## Example: Complete Blog Application

**File: `blog.stpl`** (single-file app)

```python
@route('/')
{$
posts = db.table('posts').where(published=True).order_by('-created_at').limit(10).all()
$}

<h1>My Blog</h1>
{% for post in posts %}
    <article>
        <h2><a href="/posts/{{ post['id'] }}">{{ post['title'] }}</a></h2>
        <p>{{ post['excerpt'] }}</p>
    </article>
{% endfor %}


@route('/posts/<int:post_id>')
{$
post = db.find('posts', post_id)
if not post:
    abort(404)
comments = db.table('comments').where(post_id=post_id).all()
$}

<article>
    <h1>{{ post['title'] }}</h1>
    <div>{{ post['content'] | safe }}</div>

    <h3>Comments</h3>
    {% for comment in comments %}
        <div>{{ comment['text'] }}</div>
    {% endfor %}
</article>


@route('/admin/posts/new', methods=['GET', 'POST'])
@require_auth
{$
if request.method == 'POST':
    db.insert('posts',
        title=request.form['title'],
        content=request.form['content'],
        published=True,
        user_id=session['user_id']
    )
    return redirect('/')
$}

<form method="POST">
    {{ csrf() }}
    <input name="title" placeholder="Title">
    <textarea name="content"></textarea>
    <button>Publish</button>
</form>
```

**Migration: `migrations/001_schema.sql`**

```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    content TEXT,
    published BOOLEAN DEFAULT false,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id),
    text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Config: `scribe.json`**

```json
{
  "name": "My Blog",
  "database": {
    "type": "sqlite",
    "path": "data/blog.db"
  },
  "auth": {
    "enabled": true
  }
}
```

**Run it:**
```bash
scribe new blog
cd blog
# Copy files above
scribe dev
```

**That's it.** Full blog with auth, database, migrations, CSRF protection.

---

## Next Steps

Continue to [02_QUICK_START.md](02_QUICK_START.md) for a hands-on tutorial, or jump to [03_ARCHITECTURE.md](03_ARCHITECTURE.md) for implementation details.
