"""
Project template generator for Scribe Framework

Provides templates for creating new projects with different configurations.
"""

import os
import json


def create_webapp_project(project_name: str, project_root_dir: str):
    """
    Creates a new web application project with SQLite database support.

    Args:
        project_name: Name of the project
        project_root_dir: Directory where project will be created

    Returns:
        project_path: Full path to created project
    """
    project_path = os.path.join(project_root_dir, project_name)

    if os.path.exists(project_path):
        raise FileExistsError(f"Project '{project_name}' already exists at {project_path}")

    print(f"Creating new web application: {project_name}")

    # Create directory structure
    os.makedirs(project_path)
    os.makedirs(os.path.join(project_path, 'data'))
    os.makedirs(os.path.join(project_path, 'migrations'))
    os.makedirs(os.path.join(project_path, 'models'))
    os.makedirs(os.path.join(project_path, 'static'))
    os.makedirs(os.path.join(project_path, 'saves'))

    # Create project.json
    project_config = {
        "title": project_name.replace('_', ' ').replace('-', ' ').title(),
        "author": "Anonymous",
        "starting_passage": "index",
        "project_type": "webapp",

        "database": {
            "enabled": True,
            "type": "sqlite",
            "path": "data/app.db"
        },

        "server": {
            "host": "127.0.0.1",
            "port": 5000,
            "environment": "development"
        },

        "features": {
            "use_default_player": False,
            "save_system": "server",
            "hot_reload": True
        },

        "nav": {
            "enabled": False,
            "position": "horizontal"
        },

        "debug_mode": True,

        "theme": {
            "enabled": True,
            "use_engine_defaults": False,  # Disable game engine defaults for webapp projects
            "colors": {
                "primary_color": "#2563eb",
                "background_color": "#ffffff",
                "text_color": "#1f2937",
                "link_color": "#2563eb",
                "border_color": "#e5e7eb"
            },
            "fonts": {
                "body_font": "'Inter', -apple-system, sans-serif",
                "heading_font": "'Inter', -apple-system, sans-serif"
            }
        }
    }

    with open(os.path.join(project_path, 'project.json'), 'w') as f:
        json.dump(project_config, f, indent=2)

    # Create initial migration
    initial_migration = """-- Initial database schema

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO users (name, email) VALUES
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com');
"""

    with open(os.path.join(project_path, 'migrations', '001_initial.sql'), 'w') as f:
        f.write(initial_migration)

    # Create index.stpl
    index_template = """:: index
{$
# Example: Query database
users = db.query("SELECT * FROM users ORDER BY name")
user_count = len(users)
$}

<div class="app-container">
    <!-- Header -->
    <header class="app-header">
        <div class="app-header-content">
            <h1 class="app-title">{{title}}</h1>
            <nav class="app-nav">
                <a href="/">Home</a>
                <a href="#about">About</a>
                <a href="#docs">Docs</a>
            </nav>
        </div>
    </header>

    <!-- Main Content -->
    <main class="app-main">
        <!-- Welcome Section -->
        <div class="mb-8">
            <h1>Welcome to Scribe Framework</h1>
            <p class="text-lg text-muted">Build with Scribe Framework</p>
        </div>

        <!-- Getting Started Card -->
        <div class="card mb-6">
            <div class="card-header">
                <h2 class="card-title">Getting Started</h2>
            </div>
            <div class="card-body">
                <p class="mb-4">
                    This is your new Scribe Framework web application!
                    Edit <code>index.stpl</code> to customize this page.
                </p>

                <h3 class="mb-4">Database Example</h3>
                <p class="mb-4">Found <span class="badge badge-primary">{{user_count}} users</span> in database:</p>

                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Email</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for user in users %}
                            <tr>
                                <td>{{user.name}}</td>
                                <td>{{user.email}}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Features Grid -->
        <div class="grid grid-cols-2 mb-6">
            <div class="card">
                <div class="card-body">
                    <h3 class="mb-4">What's Included?</h3>
                    <ul class="list-disc">
                        <li>✅ SQLite database with automatic migrations</li>
                        <li>✅ Python logic in templates</li>
                        <li>✅ Hot reload for instant changes</li>
                        <li>✅ Production deployment ready</li>
                    </ul>
                </div>
            </div>

            <div class="card">
                <div class="card-body">
                    <h3 class="mb-4">Quick Tips</h3>
                    <pre><code># Query database
users = db.query("SELECT * FROM users")

# Use query builder
users = db.table('users').order_by('name').all()

# Insert data
db.execute(
    "INSERT INTO users (name, email) VALUES (?, ?)",
    ("Charlie", "charlie@example.com")
)</code></pre>
                </div>
            </div>
        </div>

        <!-- Call to Action -->
        <div class="card">
            <div class="card-body">
                <div class="flex items-center justify-between">
                    <div>
                        <h3>Ready to build?</h3>
                        <p class="text-muted">Start editing your templates and models</p>
                    </div>
                    <div class="flex gap-2">
                        <a href="#" class="btn btn-secondary">View Docs</a>
                        <a href="#" class="btn btn-primary">Get Started</a>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="app-footer">
        <p>Built with Scribe Framework</p>
    </footer>
</div>
"""

    with open(os.path.join(project_path, 'index.stpl'), 'w') as f:
        f.write(index_template)

    # Create example model
    example_model = """\"\"\"
Example User model

This file demonstrates how to organize Python code in separate modules.
All .py files in your project are automatically loaded by the engine.
\"\"\"


class User:
    \"\"\"User model with database operations\"\"\"

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def save(self):
        \"\"\"Insert or update user in database\"\"\"
        existing = db.query("SELECT id FROM users WHERE email = ?", (self.email,))

        if existing:
            db.execute("UPDATE users SET name = ? WHERE email = ?",
                      (self.name, self.email))
            return existing[0]['id']
        else:
            return db.execute("INSERT INTO users (name, email) VALUES (?, ?)",
                            (self.name, self.email))

    @staticmethod
    def all():
        \"\"\"Get all users\"\"\"
        return db.query("SELECT * FROM users ORDER BY name")

    @staticmethod
    def find_by_email(email):
        \"\"\"Find user by email\"\"\"
        result = db.query("SELECT * FROM users WHERE email = ?", (email,))
        return result[0] if result else None
"""

    with open(os.path.join(project_path, 'models', 'user.py'), 'w') as f:
        f.write(example_model)

    # Create style.css (modern, clean design)
    style_css = get_webapp_css()

    with open(os.path.join(project_path, 'static', 'style.css'), 'w') as f:
        f.write(style_css)

    # Create README
    readme = f"""# {project_config['title']}

A Scribe Framework web application with SQLite database support.

## Project Structure

```
{project_name}/
├── project.json          # Configuration
├── index.stpl           # Main page template
├── models/              # Python business logic
│   └── user.py
├── migrations/          # Database migrations
│   └── 001_initial.sql
├── static/              # CSS, JS, images
│   └── style.css
└── data/                # SQLite database
    └── app.db           (created on first run)
```

## Getting Started

1. Run the development server:
   ```bash
   python main_engine.py --project-root /path/to/{project_name}
   ```

2. Open http://127.0.0.1:5000 in your browser

3. Edit `index.stpl` to start building your app

## Database Usage

Query from templates:
```python
{{$ users = db.query("SELECT * FROM users") $}}
```

Use query builder:
```python
{{$ users = db.table('users').where(active=True).all() $}}
```

## Adding Migrations

Create new file in `migrations/` directory:
```sql
-- migrations/002_add_posts.sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

Migrations run automatically on startup.
"""

    with open(os.path.join(project_path, 'README.md'), 'w') as f:
        f.write(readme)

    print(f"✓ Project created at: {project_path}")
    print(f"✓ Database configured: SQLite")
    print(f"✓ Initial migration ready")
    print(f"✓ Example model included")

    return project_path


def get_webapp_css():
    """Returns the modern CSS template for web applications"""
    return """/* Scribe Framework - Modern Web App Styles */

:root {
    /* Primary Colors */
    --primary-50: #eff6ff;
    --primary-100: #dbeafe;
    --primary-500: #3b82f6;
    --primary-600: #2563eb;
    --primary-700: #1d4ed8;

    /* Neutral Colors */
    --gray-50: #f9fafb;
    --gray-100: #f3f4f6;
    --gray-200: #e5e7eb;
    --gray-300: #d1d5db;
    --gray-400: #9ca3af;
    --gray-500: #6b7280;
    --gray-600: #4b5563;
    --gray-700: #374151;
    --gray-800: #1f2937;
    --gray-900: #111827;

    /* Semantic Colors */
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --info: #3b82f6;

    /* Shadows */
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);

    /* Spacing */
    --radius-sm: 0.375rem;
    --radius: 0.5rem;
    --radius-lg: 0.75rem;
}

/* Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html {
    font-size: 16px;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
    line-height: 1.6;
    color: var(--gray-900);
    background-color: var(--gray-50);
    min-height: 100vh;
}

/* Layout */
.app-container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.app-header {
    background: white;
    border-bottom: 1px solid var(--gray-200);
    box-shadow: var(--shadow-sm);
    position: sticky;
    top: 0;
    z-index: 100;
}

.app-header-content {
    max-width: 1400px;
    margin: 0 auto;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.app-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--gray-900);
}

.app-nav {
    display: flex;
    gap: 1.5rem;
}

.app-nav a {
    color: var(--gray-600);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s;
}

.app-nav a:hover {
    color: var(--primary-600);
}

.app-main {
    flex: 1;
    max-width: 1400px;
    width: 100%;
    margin: 0 auto;
    padding: 2rem;
}

.app-footer {
    background: white;
    border-top: 1px solid var(--gray-200);
    padding: 1.5rem 2rem;
    text-align: center;
    color: var(--gray-500);
    font-size: 0.875rem;
}

/* Container Variants */
.container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

.container-fluid {
    width: 100%;
    padding: 0 1rem;
}

.container-narrow {
    max-width: 800px;
    margin: 0 auto;
    padding: 0 1rem;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    font-weight: 600;
    line-height: 1.2;
    color: var(--gray-900);
    margin-bottom: 0.75rem;
}

h1 { font-size: 2.25rem; }
h2 { font-size: 1.875rem; }
h3 { font-size: 1.5rem; }
h4 { font-size: 1.25rem; }
h5 { font-size: 1.125rem; }
h6 { font-size: 1rem; }

p {
    margin-bottom: 1rem;
    color: var(--gray-700);
}

.text-sm { font-size: 0.875rem; }
.text-lg { font-size: 1.125rem; }
.text-xl { font-size: 1.25rem; }

.text-muted { color: var(--gray-500); }
.text-primary { color: var(--primary-600); }
.text-success { color: var(--success); }
.text-warning { color: var(--warning); }
.text-danger { color: var(--danger); }

/* Cards */
.card {
    background: white;
    border-radius: var(--radius-lg);
    border: 1px solid var(--gray-200);
    box-shadow: var(--shadow-sm);
    overflow: hidden;
}

.card-header {
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid var(--gray-200);
    background: var(--gray-50);
}

.card-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--gray-900);
    margin: 0;
}

.card-body {
    padding: 1.5rem;
}

.card-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid var(--gray-200);
    background: var(--gray-50);
}

/* Buttons */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.625rem 1.25rem;
    font-size: 0.875rem;
    font-weight: 500;
    line-height: 1;
    border-radius: var(--radius);
    border: 1px solid transparent;
    cursor: pointer;
    transition: all 0.15s;
    text-decoration: none;
}

.btn-primary {
    background: var(--primary-600);
    color: white;
}

.btn-primary:hover {
    background: var(--primary-700);
}

.btn-secondary {
    background: var(--gray-100);
    color: var(--gray-700);
    border-color: var(--gray-300);
}

.btn-secondary:hover {
    background: var(--gray-200);
}

.btn-success {
    background: var(--success);
    color: white;
}

.btn-danger {
    background: var(--danger);
    color: white;
}

/* Tables */
.table-container {
    overflow-x: auto;
    border-radius: var(--radius-lg);
    border: 1px solid var(--gray-200);
}

table {
    width: 100%;
    border-collapse: collapse;
    background: white;
}

thead {
    background: var(--gray-50);
    border-bottom: 1px solid var(--gray-200);
}

th {
    padding: 0.75rem 1rem;
    text-align: left;
    font-weight: 600;
    font-size: 0.875rem;
    color: var(--gray-700);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

td {
    padding: 0.875rem 1rem;
    border-bottom: 1px solid var(--gray-200);
    color: var(--gray-900);
}

tr:last-child td {
    border-bottom: none;
}

tbody tr:hover {
    background: var(--gray-50);
}

/* Forms */
.form-group {
    margin-bottom: 1.25rem;
}

label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    font-size: 0.875rem;
    color: var(--gray-700);
}

input[type="text"],
input[type="email"],
input[type="password"],
input[type="number"],
textarea,
select {
    width: 100%;
    padding: 0.625rem 0.875rem;
    border: 1px solid var(--gray-300);
    border-radius: var(--radius);
    font-size: 0.9375rem;
    color: var(--gray-900);
    background: white;
    transition: border-color 0.15s, box-shadow 0.15s;
}

input:focus,
textarea:focus,
select:focus {
    outline: none;
    border-color: var(--primary-500);
    box-shadow: 0 0 0 3px var(--primary-100);
}

/* Lists */
.list-none {
    list-style: none;
    padding: 0;
}

.list-disc {
    padding-left: 1.5rem;
}

.list-item {
    padding: 0.5rem 0;
}

/* Utilities */
.flex { display: flex; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.gap-1 { gap: 0.25rem; }
.gap-2 { gap: 0.5rem; }
.gap-4 { gap: 1rem; }
.gap-6 { gap: 1.5rem; }

.mb-2 { margin-bottom: 0.5rem; }
.mb-4 { margin-bottom: 1rem; }
.mb-6 { margin-bottom: 1.5rem; }
.mb-8 { margin-bottom: 2rem; }

.mt-2 { margin-top: 0.5rem; }
.mt-4 { margin-top: 1rem; }
.mt-6 { margin-top: 1.5rem; }
.mt-8 { margin-top: 2rem; }

.p-4 { padding: 1rem; }
.p-6 { padding: 1.5rem; }
.p-8 { padding: 2rem; }

/* Grid System */
.grid {
    display: grid;
    gap: 1.5rem;
}

.grid-cols-1 { grid-template-columns: repeat(1, 1fr); }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
.grid-cols-4 { grid-template-columns: repeat(4, 1fr); }

/* Links */
a {
    color: var(--primary-600);
    text-decoration: none;
    transition: color 0.15s;
}

a:hover {
    color: var(--primary-700);
    text-decoration: underline;
}

/* Code */
code {
    background: var(--gray-100);
    padding: 0.125rem 0.375rem;
    border-radius: var(--radius-sm);
    font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
    font-size: 0.875em;
    color: var(--gray-800);
}

pre {
    background: var(--gray-800);
    color: var(--gray-100);
    padding: 1.25rem;
    border-radius: var(--radius);
    overflow-x: auto;
    margin: 1.5rem 0;
}

pre code {
    background: none;
    padding: 0;
    color: inherit;
}

/* Badges */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.625rem;
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: 9999px;
}

.badge-primary {
    background: var(--primary-100);
    color: var(--primary-700);
}

.badge-success {
    background: #d1fae5;
    color: #065f46;
}

.badge-warning {
    background: #fef3c7;
    color: #92400e;
}

.badge-danger {
    background: #fee2e2;
    color: #991b1b;
}

/* Responsive */
@media (max-width: 768px) {
    .app-main {
        padding: 1rem;
    }

    .app-header-content {
        padding: 1rem;
        flex-direction: column;
        gap: 1rem;
        align-items: flex-start;
    }

    .app-nav {
        flex-direction: column;
        gap: 0.5rem;
        width: 100%;
    }

    .grid-cols-2,
    .grid-cols-3,
    .grid-cols-4 {
        grid-template-columns: 1fr;
    }

    h1 { font-size: 1.875rem; }
    h2 { font-size: 1.5rem; }
    h3 { font-size: 1.25rem; }

    .card-body {
        padding: 1rem;
    }
}

@media (min-width: 769px) and (max-width: 1024px) {
    .grid-cols-3,
    .grid-cols-4 {
        grid-template-columns: repeat(2, 1fr);
    }
}
"""


# For backward compatibility - alias to new function
create_new_project = create_webapp_project
