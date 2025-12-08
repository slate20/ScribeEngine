"""
Form helper functions for ScribeEngine templates.

Provides CSRF protection and flash messaging.
"""

from flask import session as flask_session, request
from markupsafe import Markup


def csrf_token():
    """
    Generate CSRF token input field.

    Returns:
        HTML input field with CSRF token

    Example in template:
        <form method="POST">
            {{ csrf() }}
            <input name="username">
            <button>Submit</button>
        </form>
    """
    from flask_wtf.csrf import generate_csrf

    token = generate_csrf()
    return Markup(f'<input type="hidden" name="csrf_token" value="{token}">')


# Alias for convenience
csrf = csrf_token


def flash(message: str, category: str = 'info'):
    """
    Flash a message to be displayed on the next request.

    Args:
        message: Message text
        category: Message category (info, success, warning, error)

    Example in template:
        {$
        flash('Login successful!', 'success')
        return redirect('/dashboard')
        $}

    Display flashed messages:
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
        {% endwith %}
    """
    from flask import flash as flask_flash
    flask_flash(message, category)


def get_flashed_messages(with_categories=False, category_filter=None):
    """
    Get flashed messages.

    Args:
        with_categories: If True, return (category, message) tuples
        category_filter: List of categories to filter by

    Returns:
        List of messages or (category, message) tuples

    Example in template:
        {% for message in get_flashed_messages() %}
            <div class="alert">{{ message }}</div>
        {% endfor %}
    """
    from flask import get_flashed_messages as flask_get_messages
    return flask_get_messages(with_categories=with_categories, category_filter=category_filter)


def validate_required(form_data: dict, *fields):
    """
    Validate that required fields are present and not empty.

    Args:
        form_data: Form data dict (usually request.form)
        *fields: Field names to validate

    Returns:
        Dict of field -> error message (empty if all valid)

    Example in template:
        {$
        errors = {}
        if request.method == 'POST':
            errors = validate_required(request.form, 'username', 'email', 'password')
            if not errors:
                # Process form
                pass
        $}
    """
    errors = {}
    for field in fields:
        value = form_data.get(field, '').strip()
        if not value:
            errors[field] = f"{field.replace('_', ' ').title()} is required"
    return errors


def validate_email(email: str) -> bool:
    """
    Simple email validation.

    Args:
        email: Email address to validate

    Returns:
        True if email looks valid

    Example:
        {$
        email = request.form.get('email', '')
        if not validate_email(email):
            errors['email'] = "Invalid email address"
        $}
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_length(value: str, min_length: int = None, max_length: int = None) -> bool:
    """
    Validate string length.

    Args:
        value: String to validate
        min_length: Minimum length (optional)
        max_length: Maximum length (optional)

    Returns:
        True if length is valid

    Example:
        {$
        password = request.form.get('password', '')
        if not validate_length(password, min_length=8):
            errors['password'] = "Password must be at least 8 characters"
        $}
    """
    length = len(value)

    if min_length is not None and length < min_length:
        return False

    if max_length is not None and length > max_length:
        return False

    return True
