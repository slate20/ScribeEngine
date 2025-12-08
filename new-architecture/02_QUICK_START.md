# Quick Start - Build Your First ScribeEngine App

This guide walks you through building a complete login system in 10 minutes.

---

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

---

## Step 1: Install ScribeEngine

```bash
pip install scribe-engine
```

---

## Step 2: Create a New Project

```bash
scribe new my-app
cd my-app
```

**This creates:**
```
my-app/
├── scribe.json          # Configuration
├── app.stpl             # Your routes (empty)
├── lib/                 # Python helpers
├── migrations/          # Database migrations
├── static/              # CSS, JS, images
└── data/                # SQLite database
```

---

## Step 3: Create the Database Schema

**File: `migrations/001_users.sql`**

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test user (password: password123)
INSERT INTO users (username, password_hash) VALUES
    ('testuser', 'scrypt:32768:8:1$...hash here...');
```

**Generate the password hash:**
```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('password123'))"
```

Copy the output and replace `'scrypt:32768:8:1$...hash here...'` with it.

---

## Step 4: Create Auth Helpers

**File: `lib/auth.py`**

```python
"""Authentication helpers - auto-loaded into all templates"""
from werkzeug.security import check_password_hash, generate_password_hash

def verify_password(password_hash, password):
    """Verify password against hash"""
    if password is None or password_hash is None:
        return False
    return check_password_hash(password_hash, password)

def hash_password(password):
    """Hash a password for storage"""
    return generate_password_hash(password)
```

---

## Step 5: Build the Login Page

**File: `app.stpl`**

```python
@route('/')
{$
# Redirect to dashboard if logged in, otherwise show login
if 'user_id' in session:
    return redirect('/dashboard')
$}

<h1>Welcome</h1>
<p><a href="/login">Login</a></p>


@route('/login', methods=['GET', 'POST'])
{$
error = None

if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')

    # Query database
    users = db.query("SELECT * FROM users WHERE username = ?", (username,))

    if users:
        user = users[0]
        if verify_password(user['password_hash'], password):
            session['user_id'] = user['id']
            return redirect('/dashboard')
        else:
            error = "Invalid password"
    else:
        error = "User not found"
$}

<div class="container-narrow">
    <div class="card">
        <h2>Login</h2>

        {% if error %}
        <div class="alert-error">{{ error }}</div>
        {% endif %}

        <form method="POST">
            {{ csrf() }}

            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" required>
            </div>

            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required>
            </div>

            <button type="submit" class="btn-primary">Login</button>
        </form>
    </div>
</div>


@route('/dashboard')
@require_auth
{$
user = db.query("SELECT * FROM users WHERE id = ?", (session['user_id'],))[0]
$}

<div class="container">
    <h1>Welcome, {{ user['username'] }}!</h1>
    <p>You successfully logged in.</p>
    <a href="/logout">Logout</a>
</div>


@route('/logout')
{$
session.pop('user_id', None)
return redirect('/login')
$}
```

---

## Step 6: Add Basic Styling

**File: `static/style.css`**

```css
body {
    font-family: system-ui, -apple-system, sans-serif;
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    background: #f5f5f5;
}

.container-narrow {
    max-width: 400px;
    margin: 2rem auto;
}

.card {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.form-group {
    margin-bottom: 1rem;
}

label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

input[type="text"],
input[type="password"] {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
}

.btn-primary {
    background: #2563eb;
    color: white;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
}

.btn-primary:hover {
    background: #1d4ed8;
}

.alert-error {
    background: #fee2e2;
    color: #991b1b;
    padding: 0.75rem;
    border-radius: 4px;
    margin-bottom: 1rem;
}
```

---

## Step 7: Configure the App

**File: `scribe.json`**

```json
{
  "name": "My App",
  "version": "1.0.0",

  "database": {
    "type": "sqlite",
    "path": "data/app.db"
  },

  "routes": {
    "files": ["app.stpl"],
    "login_url": "/login"
  },

  "auth": {
    "enabled": true,
    "login_url": "/login"
  },

  "session": {
    "timeout": 3600
  }
}
```

---

## Step 8: Run Your App

```bash
scribe dev
```

**Output:**
```
✓ Loaded routes from app.stpl (4 routes)
✓ Loaded helpers from lib/auth.py (2 functions)
✓ Applied migration: 001_users.sql
✓ Database connected (SQLite)

Running on http://127.0.0.1:5000
Press Ctrl+C to quit
```

---

## Step 9: Test It

1. **Open browser:** http://127.0.0.1:5000
2. **Click "Login"**
3. **Enter credentials:**
   - Username: `testuser`
   - Password: `password123`
4. **See dashboard:** "Welcome, testuser!"
5. **Click "Logout"**

---

## What Just Happened?

### **1. Template Parsing**
ScribeEngine parsed `app.stpl` and found:
- 4 routes (`/`, `/login`, `/dashboard`, `/logout`)
- Python code blocks in `{$ ... $}`
- Jinja2 templates in HTML

### **2. Flask Routes Generated**
Behind the scenes, ScribeEngine created Flask routes:

```python
@app.route('/')
def route_home():
    # Execute Python block
    # Render template
    # Return response

@app.route('/login', methods=['GET', 'POST'])
def route_login():
    # ...
```

### **3. Auto-Loading**
- `lib/auth.py` functions became available in templates
- `db` object configured automatically
- `session` from Flask exposed to templates
- CSRF protection enabled

### **4. Security**
- Passwords hashed with scrypt
- CSRF tokens in forms via `{{ csrf() }}`
- Session cookies HTTP-only
- SQL injection prevented (parameterized queries)

---

## Next Steps

### **Add User Registration**

```python
@route('/register', methods=['GET', 'POST'])
{$
error = None

if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')

    # Check if user exists
    existing = db.query("SELECT id FROM users WHERE username = ?", (username,))
    if existing:
        error = "Username already taken"
    else:
        # Create user
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hash_password(password))
        )
        db.commit()
        return redirect('/login')
$}

<div class="container-narrow">
    <div class="card">
        <h2>Register</h2>

        {% if error %}
        <div class="alert-error">{{ error }}</div>
        {% endif %}

        <form method="POST">
            {{ csrf() }}
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn-primary">Register</button>
        </form>

        <p><a href="/login">Already have an account?</a></p>
    </div>
</div>
```

### **Use PostgreSQL Instead of SQLite**

**Edit `scribe.json`:**
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

**Same code works!** ScribeEngine handles the differences.

### **Split Routes into Multiple Files**

**Create `routes/auth.stpl`:**
```python
@route('/login', methods=['GET', 'POST'])
{$ ... $}

@route('/register', methods=['GET', 'POST'])
{$ ... $}

@route('/logout')
{$ ... $}
```

**Create `routes/dashboard.stpl`:**
```python
@route('/dashboard')
@require_auth
{$ ... $}
```

**Update `scribe.json`:**
```json
{
  "routes": {
    "files": ["routes/*.stpl"]
  }
}
```

### **Use the IDE**

```bash
scribe ide
```

Opens at http://127.0.0.1:5001 with:
- File editor
- Live preview (auto-refresh on save)
- Database browser
- Migration manager

---

## Common Patterns

### **Query Patterns**

```python
{$
# Find by ID
user = db.find('users', 1)

# Simple where
users = db.where('users', active=True)

# Complex query builder
posts = db.table('posts') \
    .where(published=True) \
    .where_in('category', ['tech', 'news']) \
    .order_by('-created_at') \
    .limit(10) \
    .all()

# Raw SQL
results = db.query("""
    SELECT p.*, u.name as author
    FROM posts p
    JOIN users u ON p.user_id = u.id
    WHERE p.published = true
""")

# Insert
post_id = db.insert('posts', title='Hello', content='World')

# Update
db.update('posts', {'published': True}, id=post_id)

# Delete
db.delete('posts', id=post_id)
$}
```

### **Form Handling**

```python
@route('/posts/new', methods=['GET', 'POST'])
{$
errors = {}

if request.method == 'POST':
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()

    # Validation
    if not title:
        errors['title'] = "Title is required"
    if not content:
        errors['content'] = "Content is required"

    if not errors:
        db.insert('posts', title=title, content=content)
        return redirect('/posts')
$}

<form method="POST">
    {{ csrf() }}

    <div class="form-group">
        <label>Title</label>
        <input type="text" name="title" value="{{ request.form.get('title', '') }}">
        {% if errors.title %}
            <span class="error">{{ errors.title }}</span>
        {% endif %}
    </div>

    <div class="form-group">
        <label>Content</label>
        <textarea name="content">{{ request.form.get('content', '') }}</textarea>
        {% if errors.content %}
            <span class="error">{{ errors.content }}</span>
        {% endif %}
    </div>

    <button type="submit">Create Post</button>
</form>
```

### **API Endpoints**

```python
@route('/api/posts', methods=['GET'])
{$
from flask import jsonify

posts = db.table('posts').where(published=True).all()

# Return JSON instead of HTML
return jsonify({
    'posts': [dict(p) for p in posts]
})
$}
```

### **File Uploads**

```python
@route('/upload', methods=['POST'])
{$
from werkzeug.utils import secure_filename
import os

if 'file' in request.files:
    file = request.files['file']
    if file.filename:
        filename = secure_filename(file.filename)
        filepath = os.path.join('static/uploads', filename)
        file.save(filepath)

        # Save to database
        db.insert('uploads', filename=filename, path=filepath)
$}
```

---

## Debugging

### **Enable Debug Mode**

**In `scribe.json`:**
```json
{
  "debug": true
}
```

**Now errors show:**
- Full stack traces
- Variable values
- SQL queries executed
- Template context

### **Print Debug Info**

```python
{$
print(f"User ID: {session.get('user_id')}")
print(f"Form data: {dict(request.form)}")
$}
```

Output appears in terminal where `scribe dev` is running.

### **Database Queries**

```python
{$
# Log all queries
db.debug = True

# This will print to console:
users = db.where('users', active=True)
# SQL: SELECT * FROM users WHERE active = ?
# Params: (True,)
$}
```

---

## Next: Deep Dive into Architecture

Continue to [03_ARCHITECTURE.md](03_ARCHITECTURE.md) to understand how ScribeEngine works internally.
