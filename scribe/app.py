"""
Flask application creation and route registration for ScribeEngine.

This module handles:
- Creating Flask app instances
- Parsing .stpl template files
- Generating and registering Flask routes
- Integrating database, session, and helpers
"""

import os
import re
import glob
from pathlib import Path
from typing import Dict, Any, List, Optional
from flask import Flask, request, session, g, render_template_string
from jinja2 import Template

from scribe.parser import TemplateParser
from scribe.database import create_adapter, DatabaseManager
from scribe.execution import ExecutionContext
from scribe.loader import load_helper_modules
from scribe.helpers import response, forms, auth


def should_skip_layout(template: str) -> bool:
    """
    Check if template should bypass layout wrapping.

    Templates skip layout if they:
    - Start with <!DOCTYPE (case-insensitive)
    - Already use {% extends %}

    Args:
        template: Route template content

    Returns:
        True if layout should be skipped
    """
    if not template:
        return False

    template_stripped = template.strip()

    # Check for DOCTYPE at start (case-insensitive)
    if re.match(r'^\s*<!DOCTYPE', template_stripped, re.IGNORECASE):
        return True

    # Check for existing {% extends %}
    if re.search(r'{%\s*extends\s+', template_stripped):
        return True

    return False


def has_explicit_blocks(template: str) -> bool:
    """
    Check if template defines explicit Jinja2 blocks.

    Args:
        template: Route template content

    Returns:
        True if template contains {% block %} tags
    """
    return bool(re.search(r'{%\s*block\s+', template))


def wrap_template_with_layout(template: str, base_template_name: str = 'base.stpl') -> str:
    """
    Wrap route template with layout inheritance.

    Handles three modes:
    1. Bypass: Template has <!DOCTYPE> or {% extends %} - return as-is
    2. Explicit blocks: Template has {% block %} tags - add {% extends %}
    3. Auto-wrap: Plain content - wrap in {% block content %} and add {% extends %}

    Args:
        template: Route template content
        base_template_name: Name of base template file (default: 'base.stpl')

    Returns:
        Combined template string ready for render_template_string()
    """
    if not template:
        return template

    template_stripped = template.strip()

    # Mode 3: Skip wrapping for full HTML or already-extending templates
    if should_skip_layout(template_stripped):
        return template_stripped

    # Mode 2: Has explicit blocks - just add extends
    if has_explicit_blocks(template_stripped):
        return f"{{% extends '{base_template_name}' %}}\n{template_stripped}"

    # Mode 1: Plain HTML - wrap in content block
    return (
        f"{{% extends '{base_template_name}' %}}\n"
        f"{{% block content %}}\n"
        f"{template_stripped}\n"
        f"{{% endblock %}}"
    )


def create_app(project_path: str = '.', config: Optional[Dict[str, Any]] = None) -> Flask:
    """
    Create and configure a Flask application from ScribeEngine templates.

    Args:
        project_path: Path to the project directory containing .stpl files
        config: Optional configuration dict (overrides scribe.json)

    Returns:
        Configured Flask application

    Example:
        app = create_app('/path/to/project')
        app.run(debug=True)
    """
    # Create Flask app with project path as root
    # This allows Flask to find static/ and templates/ in the project directory
    # Convert to absolute path
    project_path = os.path.abspath(project_path)
    static_folder = os.path.join(project_path, 'static')

    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder=static_folder if os.path.exists(static_folder) else None,
        static_url_path='/static',
        template_folder=project_path  # Enable template loading for base.stpl
    )

    # Debug: print static folder location
    if os.path.exists(static_folder):
        print(f"  Static files: {static_folder}")
    else:
        print(f"  Warning: static folder not found at {static_folder}")

    # Load configuration
    app_config = load_config(project_path, config)
    app.config.update(app_config)

    # Ensure secret key is set (required for sessions)
    if not app.config.get('SECRET_KEY'):
        import secrets
        app.config['SECRET_KEY'] = secrets.token_hex(32)
        print("Warning: No SECRET_KEY configured, generated a random one. Set it in scribe.json for production.")

    # Create database manager (supports multiple named connections)
    # Handle both old 'database' key and new 'databases' key
    if 'databases' not in app_config and 'database' in app_config:
        # Old format: convert to new format
        app_config['databases'] = {'default': app_config['database']}
    elif 'databases' not in app_config:
        # No database config at all: use SQLite default
        app_config['databases'] = {'default': {'type': 'sqlite', 'database': 'app.db'}}

    db = DatabaseManager(app_config)

    # Store database manager in app config for access in routes and GUI
    app.config['DB'] = db

    # Load helper modules from lib/ directory
    helpers = load_helper_modules(project_path)
    app.config['HELPERS'] = helpers

    # Parse and register routes
    routes = parse_template_files(project_path)
    register_routes(app, routes, db, helpers, project_path)

    # Setup CSRF protection
    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect(app)
    app.config['CSRF'] = csrf

    # Add Jinja2 global functions
    setup_jinja_globals(app)

    # Register GUI IDE blueprint (optional, for development)
    # This is always registered but only accessible when explicitly requested
    register_gui_blueprint(app)

    print(f"\n✓ ScribeEngine app created with {len(routes)} route(s)")

    return app


def load_config(project_path: str, config_override: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Load configuration from scribe.json and apply defaults.

    Args:
        project_path: Project directory path
        config_override: Optional config dict to override file config

    Returns:
        Configuration dictionary
    """
    import json

    config_path = os.path.join(project_path, 'scribe.json')
    config = {}

    # Load from file if exists
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

    # Apply overrides
    if config_override:
        config.update(config_override)

    # Apply defaults
    defaults = {
        'database': {
            'type': 'sqlite',
            'database': os.path.join(project_path, 'app.db')
        },
        'session': {
            'cookie_httponly': True,
            'cookie_secure': False,  # Set to True in production with HTTPS
            'cookie_samesite': 'Lax',
            'permanent_session_lifetime': 3600 * 24 * 30  # 30 days
        }
    }

    for key, value in defaults.items():
        if key not in config:
            config[key] = value

    return config


def parse_template_files(project_path: str) -> List:
    """
    Find and parse all .stpl template files in the project.

    Args:
        project_path: Project directory path

    Returns:
        List of Route objects
    """
    from scribe.parser.ast_nodes import Route

    parser = TemplateParser()
    all_routes = []

    # Find all .stpl files (excluding base.stpl which is a layout template)
    stpl_pattern = os.path.join(project_path, '**', '*.stpl')
    all_template_files = glob.glob(stpl_pattern, recursive=True)
    template_files = [f for f in all_template_files if os.path.basename(f) != 'base.stpl']

    if not template_files:
        print(f"Warning: No .stpl template files found in {project_path}")
        return []

    for filepath in template_files:
        try:
            routes = parser.parse_file(filepath)
            all_routes.extend(routes)
            print(f"  Parsed {len(routes)} route(s) from {os.path.basename(filepath)}")
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            raise

    return all_routes


def register_routes(
    app: Flask,
    routes: List,
    db,
    helpers: Dict[str, Any],
    project_path: str
):
    """
    Register all routes with the Flask application.

    Args:
        app: Flask application
        routes: List of Route objects
        db: DatabaseAdapter instance
        helpers: Dict of loaded helper functions
        project_path: Project directory path
    """
    for route in routes:
        # Create the route handler
        handler = create_route_handler(route, db, helpers, app, project_path)

        # Apply decorators (like @require_auth)
        handler = apply_decorators(handler, route.decorators, helpers)

        # Generate unique endpoint name
        endpoint = route.get_function_name()

        # Register with Flask
        app.add_url_rule(
            rule=route.path,
            endpoint=endpoint,
            view_func=handler,
            methods=route.methods
        )

        methods_str = ', '.join(route.methods)
        print(f"  ✓ {route.path} [{methods_str}]")


def create_route_handler(route, db, helpers: Dict[str, Any], app: Flask, project_path: str):
    """
    Create a Flask view function for a route.

    Args:
        route: Route object
        db: DatabaseAdapter instance
        helpers: Dict of helper functions
        app: Flask application
        project_path: Project directory path

    Returns:
        Flask view function
    """
    def handler(**url_params):
        # Create execution context
        context = ExecutionContext(
            db=db,
            session=session,
            request=request,
            g=g,
            helpers=helpers,
            route_params=url_params
        )

        # Add helper functions
        context.set_variable('redirect', response.redirect)
        context.set_variable('abort', response.abort)
        context.set_variable('url_for', response.url_for)
        context.set_variable('jsonify', response.jsonify)
        context.set_variable('csrf', forms.csrf_token)
        context.set_variable('flash', forms.flash)

        try:
            # Execute Python code block if present
            if route.python_code:
                # Check if code returns a value (redirect, jsonify, etc.)
                exec_result = context.execute(route.python_code)

                # If the code set a return value, return it
                if context.has_return_value():
                    return context.get_variable('__return__')

            # Build template context (all user variables + framework objects)
            template_vars = context.get_variables()

            # Add URL parameters to template context
            template_vars.update(url_params)

            # Also make framework objects available in template
            template_vars['session'] = session
            template_vars['request'] = request
            template_vars['g'] = g

            # Add helper functions to template
            template_vars['csrf'] = forms.csrf_token
            template_vars['url_for'] = response.url_for

            # Render template with layout wrapping
            if route.template:
                base_template_path = os.path.join(project_path, 'base.stpl')
                if os.path.exists(base_template_path):
                    # Wrap template with layout
                    wrapped_template = wrap_template_with_layout(route.template)
                    html = render_template_string(wrapped_template, **template_vars)
                else:
                    # No base.stpl - render as-is (backward compatibility)
                    html = render_template_string(route.template, **template_vars)
                return html
            else:
                # No template, just return empty response
                return ''

        except Exception as e:
            # In development, show detailed error
            if app.debug:
                raise
            else:
                # In production, log error and show generic message
                import traceback
                print(f"Error in route {route.path}:")
                traceback.print_exc()
                return f"Internal Server Error", 500

    return handler


def apply_decorators(handler, decorator_names: List[str], helpers: Dict[str, Any]):
    """
    Apply decorators to a route handler.

    Args:
        handler: Flask view function
        decorator_names: List of decorator expressions
        helpers: Dict of helper functions (may contain custom decorators)

    Returns:
        Decorated handler function
    """
    from scribe.helpers.auth import require_auth

    # Built-in decorators
    builtin_decorators = {
        'require_auth': require_auth,
        # Add more built-in decorators here
    }

    for decorator_expr in decorator_names:
        # Parse decorator expression (e.g., "require_auth" or "require_role('admin')")
        decorator_name = decorator_expr.split('(')[0].strip()

        # Find the decorator
        if decorator_name in builtin_decorators:
            decorator = builtin_decorators[decorator_name]
        elif decorator_name in helpers:
            decorator = helpers[decorator_name]
        else:
            raise ValueError(f"Unknown decorator: {decorator_name}")

        # Apply decorator
        # If decorator has arguments (e.g., require_role('admin')), we need to eval them
        if '(' in decorator_expr:
            # For now, just call the decorator directly
            # TODO: Properly parse and apply arguments
            handler = decorator(handler)
        else:
            handler = decorator(handler)

    return handler


def register_gui_blueprint(app: Flask):
    """
    Register the GUI IDE blueprint.

    Args:
        app: Flask application
    """
    try:
        from scribe.gui import gui_bp
        app.register_blueprint(gui_bp)
    except Exception as e:
        print(f"Warning: Could not register GUI blueprint: {e}")


def setup_jinja_globals(app: Flask):
    """
    Add global functions to Jinja2 templates.

    Args:
        app: Flask application
    """
    app.jinja_env.globals['csrf'] = forms.csrf_token
    app.jinja_env.globals['url_for'] = response.url_for
