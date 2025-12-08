# Template Specification (.stpl files)

Complete syntax reference for ScribeEngine template files.

---

## File Format

**Extension:** `.stpl` (Scribe Template)
**Encoding:** UTF-8
**Line Endings:** LF (Unix) or CRLF (Windows)

---

## Basic Structure

A `.stpl` file contains one or more **routes**. Each route defines:
1. HTTP path and methods
2. Optional decorators (auth, rate limiting, etc.)
3. Python code to execute
4. HTML template to render

**Minimal example:**
```python
@route('/')
{$
message = "Hello, World!"
$}

<h1>{{ message }}</h1>
```

---

## Route Declaration

### **Syntax**

```python
@route('<path>', methods=[<methods>])
@decorator1
@decorator2
{$
# Python code
$}

<!-- HTML template -->
```

### **Components**

#### **1. Route Decorator**

```python
@route('/path')                     # GET only (default)
@route('/path', methods=['GET'])    # Explicit GET
@route('/path', methods=['POST'])   # POST only
@route('/path', methods=['GET', 'POST'])  # Multiple methods
```

**Path patterns:**
```python
@route('/')                         # Root
@route('/about')                    # Static path
@route('/posts/<int:post_id>')      # Integer parameter
@route('/users/<username>')         # String parameter
@route('/files/<path:filepath>')    # Path parameter (with slashes)
```

**Parameter types:**
- `<int:name>` - Integer
- `<float:name>` - Float
- `<string:name>` - String (default if no type specified)
- `<path:name>` - Path (allows slashes)
- `<uuid:name>` - UUID

**Parameters available in Python code:**
```python
@route('/posts/<int:post_id>')
{$
# post_id is automatically available
post = db.find('posts', post_id)
$}
```

#### **2. Decorators**

```python
@route('/dashboard')
@require_auth                       # Require login
{$ ... $}

@route('/admin')
@require_auth
@require_role('admin')              # Require specific role
{$ ... $}

@route('/api/data')
@rate_limit(100, per='hour')        # Rate limiting
{$ ... $}
```

**Built-in decorators:**
- `@require_auth` - Redirect to login if not authenticated
- `@require_auth('/custom_login')` - Custom login URL
- `@require_role('role_name')` - Require specific role
- `@rate_limit(count, per='minute|hour|day')` - Rate limiting

**Custom decorators** (defined in `lib/*.py`):
```python
# lib/decorators.py
def admin_only(func):
    def wrapper(*args, **kwargs):
        if not session.get('is_admin'):
            abort(403)
        return func(*args, **kwargs)
    return wrapper

# In template:
@route('/admin')
@admin_only
{$ ... $}
```

---

## Python Code Blocks

### **Syntax**

```python
{$
# Python code here
variable = "value"
result = some_function()
$}
```

**Multi-line:**
```python
{$
users = db.query("""
    SELECT *
    FROM users
    WHERE active = true
    ORDER BY name
""")

for user in users:
    print(user['name'])
$}
```

### **Execution Context**

**Available objects:**

| Object | Type | Description | Example |
|--------|------|-------------|---------|
| `db` | DatabaseAdapter | Database operations | `db.find('users', 1)` |
| `session` | Flask session | User session data | `session['user_id']` |
| `request` | Flask request | HTTP request data | `request.form.get('name')` |
| `auth` | AuthHelper | Authentication | `auth.login(user, pass)` |
| `g` | Flask g | Request-scoped storage | `g.current_user` |

**Request object properties:**
```python
{$
# Request method
if request.method == 'POST':
    # ...

# Form data
username = request.form.get('username')
password = request.form.get('password')

# Query parameters
page = request.args.get('page', 1)

# JSON body
data = request.json

# Headers
auth_header = request.headers.get('Authorization')

# Files
file = request.files.get('upload')

# Cookies
token = request.cookies.get('token')
$}
```

**Session operations:**
```python
{$
# Set session value
session['user_id'] = 123

# Get session value
user_id = session.get('user_id')

# Check if key exists
if 'user_id' in session:
    # ...

# Remove session value
session.pop('user_id', None)

# Clear all session data
session.clear()
$}
```

### **Return Statements**

**Redirect:**
```python
{$
if not session.get('user_id'):
    return redirect('/login')
$}
```

**Abort (error responses):**
```python
{$
post = db.find('posts', post_id)
if not post:
    abort(404)  # Not Found

if not session.get('is_admin'):
    abort(403)  # Forbidden
$}
```

**JSON response:**
```python
{$
from flask import jsonify

posts = db.table('posts').all()
return jsonify({
    'posts': [dict(p) for p in posts]
})
$}
```

**Custom response:**
```python
{$
from flask import make_response

response = make_response('<h1>Custom</h1>')
response.headers['X-Custom-Header'] = 'value'
return response
$}
```

### **Variables Scope**

**Variables persist to template:**
```python
{$
name = "Alice"
age = 30
$}

<p>Name: {{ name }}</p>
<p>Age: {{ age }}</p>
```

**Local variables don't persist:**
```python
{$
def calculate_total(items):
    total = 0  # Local to function
    for item in items:
        total += item['price']
    return total

items = db.table('items').all()
total = calculate_total(items)  # total persists
$}

<p>Total: {{ total }}</p>
```

---

## HTML Templates (Jinja2)

After Python code executes, the HTML portion renders using **Jinja2**.

### **Variable Substitution**

```html
<h1>{{ title }}</h1>
<p>{{ description }}</p>
<p>User ID: {{ user['id'] }}</p>
```

**With filters:**
```html
<p>{{ text | upper }}</p>
<p>{{ price | round(2) }}</p>
<p>{{ date | date_format('%Y-%m-%d') }}</p>
```

### **Control Flow**

**If statements:**
```html
{% if user %}
    <p>Welcome, {{ user['name'] }}</p>
{% else %}
    <p>Please log in</p>
{% endif %}

{% if user and user['is_admin'] %}
    <a href="/admin">Admin Panel</a>
{% endif %}
```

**For loops:**
```html
<ul>
{% for post in posts %}
    <li>{{ post['title'] }}</li>
{% endfor %}
</ul>

{% for post in posts %}
    <article>
        <h2>{{ post['title'] }}</h2>
        <p>{{ post['content'] }}</p>
    </article>
{% else %}
    <p>No posts found</p>
{% endfor %}
```

**Loop variables:**
```html
{% for item in items %}
    <p>{{ loop.index }}. {{ item }}</p>  <!-- 1-indexed -->
    <p>{{ loop.index0 }}. {{ item }}</p>  <!-- 0-indexed -->

    {% if loop.first %}
        <p>First item</p>
    {% endif %}

    {% if loop.last %}
        <p>Last item</p>
    {% endif %}
{% endfor %}
```

### **Comments**

```html
{# This is a Jinja2 comment (not rendered) #}

{#
Multi-line
comment
#}
```

### **Template Inheritance**

**Base template: `base.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Default Title{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```

**Child template:**
```python
@route('/')
{$ title = "Home" $}

{% extends "base.html" %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
    <h1>Welcome</h1>
    <p>This is the home page</p>
{% endblock %}
```

### **Includes**

```html
{% include 'partials/header.html' %}

<main>
    <!-- content -->
</main>

{% include 'partials/footer.html' %}
```

### **Macros (Reusable Components)**

```html
{% macro render_form_field(name, label, type='text') %}
<div class="form-group">
    <label>{{ label }}</label>
    <input type="{{ type }}" name="{{ name }}">
</div>
{% endmacro %}

{{ render_form_field('email', 'Email Address', 'email') }}
{{ render_form_field('password', 'Password', 'password') }}
```

---

## Helper Functions

Available in both Python blocks and templates.

### **CSRF Protection**

```html
<form method="POST">
    {{ csrf() }}  <!-- Injects hidden CSRF token -->
    <!-- form fields -->
</form>
```

### **Flash Messages**

**Set in Python:**
```python
{$
if success:
    flash('Operation successful!', 'success')
else:
    flash('Something went wrong', 'error')
$}
```

**Display in template:**
```html
{{ flash_messages() }}

<!-- Or manual: -->
{% for category, message in get_flashed_messages(with_categories=True) %}
    <div class="alert-{{ category }}">{{ message }}</div>
{% endfor %}
```

### **URL Generation**

```html
<a href="{{ url_for('route_name') }}">Link</a>
<a href="{{ url_for('post_detail', post_id=123) }}">Post #123</a>
```

### **Static Files**

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
<script src="{{ url_for('static', filename='js/app.js') }}"></script>
<img src="{{ url_for('static', filename='images/logo.png') }}">
```

---

## Complete Examples

### **Example 1: Simple Page**

```python
@route('/about')
{$
team_members = [
    {'name': 'Alice', 'role': 'CEO'},
    {'name': 'Bob', 'role': 'CTO'},
]
$}

<div class="container">
    <h1>About Us</h1>
    <p>Meet our team:</p>

    <div class="team">
        {% for member in team_members %}
        <div class="member">
            <h3>{{ member['name'] }}</h3>
            <p>{{ member['role'] }}</p>
        </div>
        {% endfor %}
    </div>
</div>
```

### **Example 2: Form Handling**

```python
@route('/contact', methods=['GET', 'POST'])
{$
success = False
errors = {}

if request.method == 'POST':
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    message = request.form.get('message', '').strip()

    # Validation
    if not name:
        errors['name'] = "Name is required"
    if not email or '@' not in email:
        errors['email'] = "Valid email is required"
    if not message:
        errors['message'] = "Message is required"

    if not errors:
        # Save to database
        db.insert('contacts',
            name=name,
            email=email,
            message=message
        )
        db.commit()
        success = True
$}

<div class="container">
    <h1>Contact Us</h1>

    {% if success %}
        <div class="alert-success">Thank you! We'll be in touch.</div>
    {% endif %}

    <form method="POST">
        {{ csrf() }}

        <div class="form-group">
            <label>Name</label>
            <input type="text" name="name" value="{{ request.form.get('name', '') }}">
            {% if errors.name %}
                <span class="error">{{ errors.name }}</span>
            {% endif %}
        </div>

        <div class="form-group">
            <label>Email</label>
            <input type="email" name="email" value="{{ request.form.get('email', '') }}">
            {% if errors.email %}
                <span class="error">{{ errors.email }}</span>
            {% endif %}
        </div>

        <div class="form-group">
            <label>Message</label>
            <textarea name="message">{{ request.form.get('message', '') }}</textarea>
            {% if errors.message %}
                <span class="error">{{ errors.message }}</span>
            {% endif %}
        </div>

        <button type="submit">Send</button>
    </form>
</div>
```

### **Example 3: Authentication**

```python
@route('/login', methods=['GET', 'POST'])
{$
error = None

if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')

    user = db.table('users').where(username=username).first()

    if user and auth.verify_password(user['password_hash'], password):
        session['user_id'] = user['id']
        return redirect('/dashboard')
    else:
        error = "Invalid credentials"
$}

<div class="login-form">
    <h2>Login</h2>

    {% if error %}
        <div class="alert-error">{{ error }}</div>
    {% endif %}

    <form method="POST">
        {{ csrf() }}

        <div class="form-group">
            <input type="text" name="username" placeholder="Username" required>
        </div>

        <div class="form-group">
            <input type="password" name="password" placeholder="Password" required>
        </div>

        <button type="submit">Login</button>
    </form>
</div>


@route('/dashboard')
@require_auth
{$
user = db.find('users', session['user_id'])
recent_activity = db.table('activity').where(user_id=user['id']).limit(10).all()
$}

<div class="dashboard">
    <h1>Welcome, {{ user['username'] }}!</h1>

    <h2>Recent Activity</h2>
    <ul>
    {% for activity in recent_activity %}
        <li>{{ activity['description'] }} - {{ activity['created_at'] }}</li>
    {% endfor %}
    </ul>

    <a href="/logout">Logout</a>
</div>


@route('/logout')
{$
session.pop('user_id', None)
return redirect('/login')
$}
```

### **Example 4: API Endpoint**

```python
@route('/api/posts', methods=['GET'])
{$
from flask import jsonify

posts = db.table('posts') \
    .where(published=True) \
    .order_by('-created_at') \
    .limit(20) \
    .all()

return jsonify({
    'posts': [dict(p) for p in posts],
    'count': len(posts)
})
$}
```

### **Example 5: File Upload**

```python
@route('/upload', methods=['GET', 'POST'])
@require_auth
{$
import os
from werkzeug.utils import secure_filename

uploaded_file = None

if request.method == 'POST':
    if 'file' in request.files:
        file = request.files['file']
        if file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join('static/uploads', filename)
            file.save(filepath)

            # Save to database
            db.insert('uploads',
                user_id=session['user_id'],
                filename=filename,
                path=filepath
            )
            db.commit()

            uploaded_file = filename
$}

<div class="container">
    <h1>Upload File</h1>

    {% if uploaded_file %}
        <div class="alert-success">
            File uploaded: {{ uploaded_file }}
        </div>
    {% endif %}

    <form method="POST" enctype="multipart/form-data">
        {{ csrf() }}

        <div class="form-group">
            <input type="file" name="file" required>
        </div>

        <button type="submit">Upload</button>
    </form>
</div>
```

---

## Syntax Rules

### **Whitespace**

- Python blocks: Indentation matters (standard Python)
- HTML: Whitespace generally ignored by browsers
- Jinja2: Whitespace preserved in output

### **Comments**

```python
{$
# Python comment
variable = "value"  # Inline comment
$}

<!-- HTML comment -->

{# Jinja2 comment #}
```

### **Escaping**

**To output literal `{{` or `{%`:**
```html
{{ '{{' }}  <!-- Renders as {{ -->
{{ '{%' }}  <!-- Renders as {% -->
```

**To output literal `{$` or `$}`:**
```html
Use HTML entities: &#123;$ or $&#125;
```

---

## File Organization

### **Single File (Simple Apps)**

```python
# app.stpl

@route('/')
{$ ... $}
<!-- template -->

@route('/about')
{$ ... $}
<!-- template -->

@route('/contact')
{$ ... $}
<!-- template -->
```

### **Multiple Files (Complex Apps)**

```
routes/
├── auth.stpl       # Login, register, logout
├── posts.stpl      # Blog post routes
├── admin.stpl      # Admin panel routes
└── api.stpl        # API endpoints
```

**Each file contains related routes.**

---

## Next: Parser Implementation

See [06_TEMPLATE_PARSER.md](06_TEMPLATE_PARSER.md) for how to parse this syntax.
