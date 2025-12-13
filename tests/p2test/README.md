# p2test

A ScribeEngine web application.

## Getting Started

1. Run development server:
   ```
   scribe dev
   ```

2. Open http://localhost:5000 in your browser

## Project Structure

```
p2test/
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
{$
greeting = f"Hello, {name}!"
$}

<h1>{{ greeting }}</h1>
```

## Database Operations

```python
@route('/users')
{$
users = db.query("SELECT * FROM users")
$}

{% for user in users %}
    <div>{{ user['name'] }}</div>
{% endfor %}
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
