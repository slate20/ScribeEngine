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
    <title>{{ page_title | default('My App') }}</title>
    <meta name="description" content="{{ page_description | default('') }}">
    <link rel="stylesheet" href="/static/css/style.css">
    {% block extra_head %}{% endblock %}
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand"><a href="/">My App</a></div>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/about">About</a>
        </div>
    </nav>

    <main class="container">
        {% block content %}{% endblock %}
    </main>

    <footer>
        <p>&copy; 2025 My ScribeEngine App</p>
    </footer>

    {% block extra_scripts %}{% endblock %}
</body>
</html>
'''
    with open(os.path.join(project_path, 'base.stpl'), 'w') as f:
        f.write(base_stpl)

    # Create example app.stpl (using layout system - no HTML boilerplate!)
    app_stpl = '''@route('/')
{$
page_title = "Home"
message = "Hello, ScribeEngine!"
$}

<h1>{{ message }}</h1>
<p>Your ScribeEngine app is running!</p>

<h2>Getting Started</h2>
<ul>
    <li>Edit <code>app.stpl</code> to add routes</li>
    <li>Modify <code>base.stpl</code> to customize your layout</li>
    <li>Add helper functions in <code>lib/</code> directory</li>
    <li>Create database migrations in <code>migrations/</code> directory</li>
    <li>Run <code>scribe dev</code> to start development server</li>
</ul>

<h2>Example Routes</h2>
<ul>
    <li><a href="/">Home</a> (this page)</li>
    <li><a href="/about">About</a></li>
</ul>


@route('/about')
{$
page_title = "About"
page_description = "Learn about this ScribeEngine application"
$}

<h1>About This Project</h1>
<p>Built with ScribeEngine - no HTML boilerplate needed!</p>
<p>All routes automatically use the layout defined in <code>base.stpl</code>.</p>

<h2>Layout Features</h2>
<ul>
    <li>Shared navigation and footer across all pages</li>
    <li>Set page title with <code>page_title</code> variable</li>
    <li>Set meta description with <code>page_description</code> variable</li>
    <li>Use explicit blocks for advanced layouts</li>
</ul>

<p><a href="/">← Back to Home</a></p>
'''
    with open(os.path.join(project_path, 'app.stpl'), 'w') as f:
        f.write(app_stpl)

    # Create basic CSS file
    css = '''body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    max-width: 800px;
    margin: 50px auto;
    padding: 0 20px;
    line-height: 1.6;
}

h1 {
    color: #333;
    border-bottom: 2px solid #007bff;
    padding-bottom: 10px;
}

code {
    background: #f4f4f4;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: "Courier New", monospace;
}

a {
    color: #007bff;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}
'''
    with open(os.path.join(project_path, 'static', 'css', 'style.css'), 'w') as f:
        f.write(css)

    # Create README
    readme = f'''# {project_name}

A ScribeEngine web application.

## Getting Started

1. Run development server:
   ```
   scribe dev
   ```

2. Open http://localhost:5000 in your browser

## Project Structure

```
{project_name}/
├── app.stpl           # Your routes and templates
├── scribe.json        # Configuration
├── lib/               # Helper functions
├── migrations/        # Database migrations
├── static/            # CSS, JS, images
│   ├── css/
│   └── js/
└── app.db             # SQLite database (created automatically)
```

## Adding Routes

Edit `app.stpl` and add routes using the `@route()` decorator:

```python
@route('/hello/<name>')
'''+ '''{$
greeting = f"Hello, {name}!"
$}

<h1>{{ greeting }}</h1>
```

## Database Operations

```python
@route('/users')
{$
users = db['default'].query("SELECT * FROM users")
$}

{'''+ '''% for user in users %}
    <div>{{ user['name'] }}</div>
{'''+ '''% endfor %}
```

## Authentication

```python
@route('/dashboard')
@require_auth
{$
user = db.find('users', session['user_id'])
$}

<h1>Welcome, {{ user['username'] }}!</h1>
```

## Learn More

- Documentation: https://scribe-engine.readthedocs.io
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

    click.echo(f"\n✓ Created project: {project_name}")
    click.echo(f"\nNext steps:")
    click.echo(f"  cd {project_name}")
    click.echo(f"  scribe dev")
    click.echo(f"\nThen open http://localhost:5000 in your browser")


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
