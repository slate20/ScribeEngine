# Flask Integration

Complete specification for how ScribeEngine integrates with Flask to serve web applications.

---

## Overview

ScribeEngine **generates Flask routes dynamically** from parsed `.stpl` template files. This document explains:
1. How templates become Flask routes
2. Request handling flow
3. Response generation
4. Integration with Flask ecosystem

---

## Architecture

```
.stpl Template                Flask Application
──────────────                ──────────────────

@route('/users/<int:id>')
{$                            app = Flask(__name__)
user = db.find('users', id)
$}                            @app.route('/users/<int:id>', methods=['GET'])
                              def route_users_id(id):
<h1>{{ user.name }}</h1>          # 1. Create execution context
                                  context = create_context(db, session, request)

                                  # 2. Execute Python block
                                  context.execute("user = db.find('users', id)")

                                  # 3. Build template context
                                  template_vars = context.get_variables()
                                  template_vars['id'] = id  # Add route params

                                  # 4. Render Jinja2
                                  html = render_template_string(
                                      "<h1>{{ user.name }}</h1>",
                                      **template_vars
                                  )

                                  # 5. Return response
                                  return html
```

---

## Route Generation Process

### **Step 1: Parse Template Files**

```python
from scribe.parser import TemplateParser

def load_routes(project_path):
    """Load and parse all .stpl files"""
    parser = TemplateParser()
    routes = []

    # Find all template files
    template_files = find_template_files(project_path)

    for filepath in template_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse file into routes
        file_routes = parser.parse(content, filepath)
        routes.extend(file_routes)

    return routes
```

### **Step 2: Generate Flask Routes**

```python
def register_routes(app, routes, db):
    """Register all routes with Flask app"""

    for route in routes:
        # Create handler function
        handler = create_route_handler(route, db)

        # Apply decorators
        for decorator in route.decorators:
            handler = apply_decorator(handler, decorator)

        # Register with Flask
        app.add_url_rule(
            rule=route.path,
            endpoint=route.endpoint,
            view_func=handler,
            methods=route.methods
        )

        print(f"✓ Registered route: {route.methods} {route.path}")
```

### **Step 3: Create Route Handler**

```python
def create_route_handler(route, db):
    """
    Create Flask view function for a route.

    Args:
        route: ParsedRoute object
        db: DatabaseAdapter instance

    Returns:
        Callable: Flask view function
    """
    def handler(**url_params):
        from flask import request, session, g

        # 1. Create execution context
        context = ExecutionContext()
        context.add_variable('db', db)
        context.add_variable('session', session)
        context.add_variable('request', request)
        context.add_variable('g', g)

        # Add URL parameters
        for key, value in url_params.items():
            context.add_variable(key, value)

        # Load auto-loaded modules
        helpers = load_helper_modules(route.project_path)
        for name, obj in helpers.items():
            context.add_variable(name, obj)

        # Load helper functions
        context.add_variable('redirect', redirect_helper)
        context.add_variable('abort', abort_helper)
        context.add_variable('csrf', csrf_helper)
        context.add_variable('flash', flash_helper)
        context.add_variable('auth', AuthHelper(db, session))

        try:
            # 2. Execute Python code block
            result = context.execute(route.python_code)

            # Check if code returned early (redirect, abort, etc.)
            if result is not None:
                return result

            # 3. Build Jinja2 template context
            template_vars = context.get_variables()

            # Add Flask helpers
            template_vars['csrf'] = csrf_helper
            template_vars['url_for'] = url_for
            template_vars['get_flashed_messages'] = get_flashed_messages
            template_vars['flash_messages'] = flash_messages_helper

            # 4. Render Jinja2 template
            html = render_jinja2(route.template, template_vars)

            # 5. Return HTTP response
            return html

        except Exception as e:
            # Error handling
            if app.debug:
                return render_error_debug(e, route)
            else:
                return render_error_production(e)

    # Set function name for debugging
    handler.__name__ = route.endpoint

    return handler
```

---

## Execution Context

Manages Python code execution in templates.

```python
class ExecutionContext:
    """
    Manages execution environment for template Python code.

    Provides:
    - Variable storage
    - Safe execution environment
    - Access control
    """

    def __init__(self):
        self.variables = {}
        self._safe_builtins = self._create_safe_builtins()

    def add_variable(self, name, value):
        """Add variable to execution context"""
        self.variables[name] = value

    def get_variables(self):
        """Get all variables (for template rendering)"""
        return {k: v for k, v in self.variables.items()
                if not k.startswith('_') and not callable(v)}

    def execute(self, code):
        """
        Execute Python code in controlled environment.

        Args:
            code (str): Python code to execute

        Returns:
            Any: Return value if code uses 'return' statement
        """
        # Create safe globals
        safe_globals = {
            '__builtins__': self._safe_builtins,
            **self.variables
        }

        # Execute code
        exec_globals = safe_globals
        exec(code, exec_globals)

        # Update variables from execution
        for key, value in exec_globals.items():
            if not key.startswith('__'):
                self.variables[key] = value

        # Check for return value
        if 'return' in code:
            # Extract return value (complex - simplified here)
            return self.variables.get('_return_value')

        return None

    def _create_safe_builtins(self):
        """Create restricted set of builtins"""
        return {
            # Types
            'int': int,
            'float': float,
            'str': str,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,

            # Functions
            'len': len,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'sorted': sorted,
            'reversed': reversed,
            'min': min,
            'max': max,
            'sum': sum,
            'abs': abs,
            'round': round,
            'any': any,
            'all': all,

            # String
            'ord': ord,
            'chr': chr,

            # Type checking
            'isinstance': isinstance,
            'type': type,
            'hasattr': hasattr,
            'getattr': getattr,
            'setattr': setattr,

            # Debugging
            'print': print,

            # BLOCKED: open, __import__, eval, exec, compile
        }
```

---

## Helper Functions

### **Redirect Helper**

```python
from flask import redirect as flask_redirect, make_response

def redirect_helper(location, code=302):
    """
    Redirect to another URL.

    Args:
        location (str): URL to redirect to
        code (int): HTTP status code (default 302)

    Returns:
        Response: Flask redirect response

    Example:
        return redirect('/dashboard')
        return redirect('/login', 301)  # Permanent redirect
    """
    return flask_redirect(location, code=code)
```

### **Abort Helper**

```python
from flask import abort as flask_abort

def abort_helper(code, description=None):
    """
    Abort request with HTTP error.

    Args:
        code (int): HTTP status code
        description (str): Optional error description

    Example:
        abort(404)  # Not Found
        abort(403, "Access denied")
    """
    if description:
        flask_abort(code, description=description)
    else:
        flask_abort(code)
```

### **CSRF Helper**

```python
from flask_wtf.csrf import generate_csrf
from markupsafe import Markup

def csrf_helper():
    """
    Generate CSRF token field for forms.

    Returns:
        Markup: HTML hidden input with CSRF token

    Example:
        <form method="POST">
            {{ csrf() }}
            ...
        </form>
    """
    token = generate_csrf()
    return Markup(f'<input type="hidden" name="csrf_token" value="{token}">')
```

### **Flash Messages Helper**

```python
from flask import get_flashed_messages
from markupsafe import Markup

def flash_messages_helper():
    """
    Render flash messages as HTML.

    Returns:
        Markup: HTML for all flash messages

    Example:
        {{ flash_messages() }}
    """
    messages = get_flashed_messages(with_categories=True)

    if not messages:
        return Markup('')

    html = []
    for category, message in messages:
        html.append(
            f'<div class="flash flash-{category}">{message}</div>'
        )

    return Markup('\n'.join(html))
```

### **Auth Helper**

```python
from werkzeug.security import check_password_hash

class AuthHelper:
    """Authentication helper functions"""

    def __init__(self, db, session):
        self.db = db
        self.session = session

    def login(self, username, password):
        """
        Attempt to log in user.

        Args:
            username (str): Username or email
            password (str): Plain text password

        Returns:
            bool: True if login successful
        """
        # Find user
        user = self.db.table('users').where(username=username).first()

        if not user:
            return False

        # Verify password
        if not check_password_hash(user['password_hash'], password):
            return False

        # Set session
        self.session['user_id'] = user['id']

        return True

    def logout(self):
        """Log out current user"""
        self.session.pop('user_id', None)

    def user(self):
        """
        Get current logged-in user.

        Returns:
            Row or None: Current user or None if not logged in
        """
        user_id = self.session.get('user_id')
        if not user_id:
            return None

        return self.db.find('users', user_id)

    def check(self):
        """Check if user is logged in"""
        return 'user_id' in self.session
```

---

## Decorator Implementation

### **@require_auth**

```python
from functools import wraps
from flask import session, redirect

def require_auth(login_url='/login'):
    """
    Decorator to require authentication.

    Args:
        login_url (str): URL to redirect to if not authenticated

    Example:
        @route('/dashboard')
        @require_auth
        {$ ... $}

        @route('/admin')
        @require_auth('/admin/login')
        {$ ... $}
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(login_url)
            return func(*args, **kwargs)
        return wrapper
    return decorator if callable(login_url) else decorator
```

### **@require_role**

```python
def require_role(role_name):
    """
    Decorator to require specific user role.

    Args:
        role_name (str): Required role name

    Example:
        @route('/admin')
        @require_auth
        @require_role('admin')
        {$ ... $}
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = session.get('user_id')
            if not user_id:
                abort(401)

            # Get user from database
            db = current_app.config['DATABASE']
            user = db.find('users', user_id)

            if not user or user.get('role') != role_name:
                abort(403)

            return func(*args, **kwargs)
        return wrapper
    return decorator
```

---

## Application Setup

### **Complete Flask Application**

```python
from flask import Flask
from flask_wtf.csrf import CSRFProtect

def create_app(project_path):
    """
    Create Flask application for ScribeEngine project.

    Args:
        project_path (str): Path to project directory

    Returns:
        Flask: Configured Flask app
    """
    app = Flask(__name__)

    # Load configuration
    config = load_config(project_path)

    # Configure Flask
    app.config['SECRET_KEY'] = config.get('secret_key', 'dev-key-change-in-production')
    app.config['DEBUG'] = config.get('debug', False)

    # Initialize CSRF protection
    csrf = CSRFProtect(app)

    # Create database adapter
    db = create_database_adapter(config['database'])
    app.config['DATABASE'] = db

    # Apply migrations
    apply_migrations(db, os.path.join(project_path, 'migrations'))

    # Load and register routes
    routes = load_routes(project_path)
    register_routes(app, routes, db)

    # Register error handlers
    register_error_handlers(app)

    # Register teardown handler
    @app.teardown_appcontext
    def close_db(error):
        db = app.config.get('DATABASE')
        if db:
            db.commit()  # Auto-commit on success

    return app
```

### **Error Handlers**

```python
def register_error_handlers(app):
    """Register error handlers for common HTTP errors"""

    @app.errorhandler(404)
    def not_found(error):
        if app.debug:
            return f"<h1>404 Not Found</h1><p>{error}</p>", 404
        return "<h1>404 Not Found</h1><p>The page you're looking for doesn't exist.</p>", 404

    @app.errorhandler(403)
    def forbidden(error):
        if app.debug:
            return f"<h1>403 Forbidden</h1><p>{error}</p>", 403
        return "<h1>403 Forbidden</h1><p>You don't have permission to access this resource.</p>", 403

    @app.errorhandler(500)
    def internal_error(error):
        if app.debug:
            import traceback
            tb = traceback.format_exc()
            return f"<h1>500 Internal Server Error</h1><pre>{tb}</pre>", 500
        return "<h1>500 Internal Server Error</h1><p>Something went wrong.</p>", 500
```

---

## CLI Integration

### **Development Server**

```python
def run_dev_server(project_path, host='127.0.0.1', port=5000):
    """
    Run development server with auto-reload.

    Args:
        project_path (str): Path to project
        host (str): Host address
        port (int): Port number
    """
    app = create_app(project_path)

    print(f"✓ ScribeEngine development server")
    print(f"✓ Running on http://{host}:{port}")
    print(f"✓ Press Ctrl+C to quit")

    app.run(
        host=host,
        port=port,
        debug=True,
        use_reloader=True
    )
```

### **Production Server (WSGI)**

```python
# wsgi.py
import os
from scribe import create_app

# Get project path from environment
project_path = os.environ.get('SCRIBE_PROJECT_PATH', '/var/www/myapp')

# Create application
application = create_app(project_path)

if __name__ == '__main__':
    application.run()
```

**Run with Gunicorn:**
```bash
SCRIBE_PROJECT_PATH=/var/www/myapp gunicorn -w 4 -b 0.0.0.0:8000 wsgi:application
```

---

## Static Files

### **Serving Static Files**

Flask automatically serves files from `static/` directory.

**URL generation in templates:**
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
<script src="{{ url_for('static', filename='js/app.js') }}"></script>
<img src="{{ url_for('static', filename='images/logo.png') }}">
```

### **Custom Static Folder**

```python
app = Flask(__name__, static_folder='assets')
```

---

## Session Management

### **Configuration**

```python
app.config['SESSION_COOKIE_NAME'] = 'scribe_session'
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # No JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
```

### **Usage in Templates**

```python
{$
# Set session data
session['user_id'] = 123
session['preferences'] = {'theme': 'dark'}

# Get session data
user_id = session.get('user_id')
theme = session.get('preferences', {}).get('theme', 'light')

# Delete session data
session.pop('user_id', None)

# Clear all session data
session.clear()
$}
```

---

## Request Context

### **Request Object Properties**

```python
{$
# HTTP method
method = request.method  # 'GET', 'POST', etc.

# URL information
path = request.path  # '/users/123'
full_path = request.full_path  # '/users/123?page=2'
url = request.url  # 'http://example.com/users/123?page=2'
base_url = request.base_url  # 'http://example.com/users/123'

# Query parameters
page = request.args.get('page', 1)
search = request.args.get('q', '')

# Form data
username = request.form.get('username')
password = request.form.get('password')

# JSON body
data = request.json  # For Content-Type: application/json

# Headers
auth = request.headers.get('Authorization')
content_type = request.headers.get('Content-Type')

# Files
file = request.files.get('upload')

# Cookies
token = request.cookies.get('token')

# Client IP
ip = request.remote_addr
$}
```

---

## Response Objects

### **HTML Response (Default)**

```python
{$
message = "Hello, World!"
$}

<h1>{{ message }}</h1>
```

### **JSON Response**

```python
{$
from flask import jsonify

data = {'users': [{'id': 1, 'name': 'Alice'}]}
return jsonify(data)
$}
```

### **Custom Response**

```python
{$
from flask import make_response

response = make_response('<h1>Custom</h1>', 200)
response.headers['X-Custom-Header'] = 'value'
response.set_cookie('session', 'abc123')
return response
$}
```

### **File Download**

```python
{$
from flask import send_file

return send_file('/path/to/file.pdf', as_attachment=True)
$}
```

---

## Next Steps

- **[11_HELPERS_API.md](11_HELPERS_API.md)** - Complete helper function reference
- **[12_AUTHENTICATION.md](12_AUTHENTICATION.md)** - Authentication system details
- **[13_CONFIGURATION.md](13_CONFIGURATION.md)** - Configuration options
