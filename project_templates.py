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
            "use_engine_defaults": True,
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

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Welcome to {{title}}</h1>
            <p class="subtitle">Built with Scribe Framework</p>
        </header>

        <main>
            <section class="content-section">
                <h2>Getting Started</h2>
                <p>
                    This is your new Scribe Framework web application!
                    Edit <code>index.stpl</code> to customize this page.
                </p>

                <h3>Database Example</h3>
                <p>Found <strong>{{user_count}}</strong> users in database:</p>
                <ul>
                {% for user in users %}
                    <li>{{user.name}} ({{user.email}})</li>
                {% endfor %}
                </ul>
            </section>

            <section class="info-section">
                <h3>What's Included?</h3>
                <ul>
                    <li>✅ SQLite database with automatic migrations</li>
                    <li>✅ Python logic in templates</li>
                    <li>✅ Hot reload for instant changes</li>
                    <li>✅ Production deployment ready</li>
                </ul>
            </section>

            <section class="info-section">
                <h3>Quick Tips</h3>
                <div class="code-block">
                    <code># Query database<br>
users = db.query("SELECT * FROM users")<br>
<br>
# Use query builder<br>
users = db.table('users').order_by('name').all()<br>
<br>
# Insert data<br>
db.execute("INSERT INTO users (name, email) VALUES (?, ?)",<br>
&nbsp;&nbsp;&nbsp;&nbsp;("Charlie", "charlie@example.com"))
                    </code>
                </div>
            </section>
        </main>

        <footer>
            <p>Built with Scribe Framework</p>
        </footer>
    </div>
</body>
</html>
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
    --primary-color: #2563eb;
    --primary-hover: #1d4ed8;
    --background: #ffffff;
    --surface: #f9fafb;
    --text-primary: #1f2937;
    --text-secondary: #6b7280;
    --border: #e5e7eb;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    line-height: 1.6;
    color: var(--text-primary);
    background-color: var(--surface);
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

/* Header */
header {
    text-align: center;
    padding: 40px 0;
    border-bottom: 2px solid var(--border);
    margin-bottom: 30px;
}

header h1 {
    font-size: 2.5rem;
    color: var(--text-primary);
    margin-bottom: 10px;
}

.subtitle {
    font-size: 1.1rem;
    color: var(--text-secondary);
}

/* Content Sections */
.content-section, .info-section {
    background: var(--background);
    padding: 30px;
    border-radius: 8px;
    box-shadow: var(--shadow);
    margin-bottom: 30px;
}

.content-section h2, .info-section h3 {
    margin-bottom: 20px;
    color: var(--text-primary);
    border-bottom: 2px solid var(--border);
    padding-bottom: 10px;
}

.content-section h3 {
    margin-top: 20px;
    margin-bottom: 10px;
    color: var(--text-primary);
}

/* Lists */
ul {
    margin: 15px 0;
    padding-left: 20px;
}

li {
    padding: 5px 0;
    color: var(--text-primary);
}

/* Code Blocks */
.code-block {
    background: #1f2937;
    color: #e5e7eb;
    padding: 20px;
    border-radius: 6px;
    overflow-x: auto;
    margin: 20px 0;
}

.code-block code {
    font-family: 'Fira Code', 'Courier New', monospace;
    font-size: 0.9rem;
    line-height: 1.6;
}

code {
    background: var(--surface);
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
}

/* Links */
a {
    color: var(--primary-color);
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

/* Footer */
footer {
    text-align: center;
    padding: 40px 0 20px 0;
    color: var(--text-secondary);
    border-top: 1px solid var(--border);
    margin-top: 40px;
}

/* Responsive */
@media (max-width: 768px) {
    header h1 {
        font-size: 2rem;
    }

    .container {
        padding: 10px;
    }

    .content-section, .info-section {
        padding: 20px;
    }
}
"""


# For backward compatibility - alias to new function
create_new_project = create_webapp_project
