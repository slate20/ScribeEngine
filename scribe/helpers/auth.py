"""
Authentication helper functions and decorators for ScribeEngine.

Provides:
- @require_auth decorator
- Login/logout helpers
- Password hashing utilities
"""

from functools import wraps
from flask import session, redirect, request
from werkzeug.security import generate_password_hash, check_password_hash


def require_auth(f=None, login_url='/login'):
    """
    Decorator to require authentication for a route.

    Args:
        f: Function to decorate (optional, for parameterless @require_auth)
        login_url: URL to redirect to if not authenticated

    Usage in template:
        @route('/dashboard')
        @require_auth
        {$ ... $}

        or with custom login URL:

        @route('/admin')
        @require_auth('/admin/login')
        {$ ... $}
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                # Store the requested URL to redirect back after login
                session['next_url'] = request.url
                return redirect(login_url)
            return func(*args, **kwargs)
        return wrapper

    # Handle both @require_auth and @require_auth('/custom_url')
    if f is None:
        # Called with arguments: @require_auth('/custom_url')
        return decorator
    else:
        # Called without arguments: @require_auth
        return decorator(f)


def hash_password(password: str) -> str:
    """
    Hash a password using Werkzeug's secure hashing (scrypt).

    Args:
        password: Plain text password

    Returns:
        Hashed password string

    Example in template:
        {$
        password = request.form.get('password')
        hashed = hash_password(password)
        db.insert('users', username=username, password=hashed)
        $}
    """
    return generate_password_hash(password, method='scrypt')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        password: Plain text password
        password_hash: Hashed password from database

    Returns:
        True if password matches

    Example in template:
        {$
        user = db.table('users').where(username=username).first()
        if user and verify_password(password, user['password']):
            session['user_id'] = user['id']
            return redirect('/dashboard')
        else:
            errors['login'] = "Invalid username or password"
        $}
    """
    return check_password_hash(password_hash, password)


def login_user(user_id: int, remember: bool = False):
    """
    Log in a user by storing their ID in the session.

    Args:
        user_id: User ID to store in session
        remember: If True, make session permanent (30 days)

    Example in template:
        {$
        user = db.table('users').where(username=username).first()
        if user and verify_password(password, user['password']):
            login_user(user['id'], remember=True)
            return redirect('/dashboard')
        $}
    """
    session['user_id'] = user_id

    if remember:
        session.permanent = True


def logout_user():
    """
    Log out the current user by clearing the session.

    Example in template:
        @route('/logout')
        {$
        logout_user()
        flash('You have been logged out', 'info')
        return redirect('/')
        $}
    """
    session.clear()


def get_current_user_id():
    """
    Get the current user's ID from the session.

    Returns:
        User ID or None if not logged in

    Example in template:
        {$
        user_id = get_current_user_id()
        if user_id:
            user = db.find('users', user_id)
        $}
    """
    return session.get('user_id')


def is_authenticated() -> bool:
    """
    Check if a user is currently authenticated.

    Returns:
        True if user is logged in

    Example in template:
        {$
        if is_authenticated():
            user = db.find('users', session['user_id'])
        $}
    """
    return 'user_id' in session


class AuthHelper:
    """
    Authentication helper class that can be injected into templates.

    Provides convenient methods for authentication operations.

    Example usage in template:
        {$
        if auth.login(username, password):
            return redirect('/dashboard')
        else:
            errors['login'] = "Invalid credentials"
        $}
    """

    def __init__(self, db, session):
        """
        Initialize auth helper.

        Args:
            db: DatabaseAdapter instance
            session: Flask session object
        """
        self.db = db
        self.session = session

    def login(self, username: str, password: str, username_field: str = 'username') -> bool:
        """
        Attempt to log in with username and password.

        Args:
            username: Username or email
            password: Plain text password
            username_field: Field name to search by (default: 'username')

        Returns:
            True if login successful

        Example:
            {$
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')

                if auth.login(username, password):
                    flash('Login successful!', 'success')
                    return redirect('/dashboard')
                else:
                    errors['login'] = "Invalid username or password"
            $}
        """
        # Find user by username
        users = self.db.where('users', **{username_field: username})

        if not users:
            return False

        user = users[0]

        # Verify password
        if verify_password(password, user['password']):
            login_user(user['id'])
            return True

        return False

    def logout(self):
        """
        Log out the current user.

        Example:
            {$ auth.logout() $}
        """
        logout_user()

    def user_id(self):
        """Get current user ID or None"""
        return get_current_user_id()

    def is_authenticated(self) -> bool:
        """Check if user is logged in"""
        return is_authenticated()

    def get_user(self):
        """
        Get the current user object from database.

        Returns:
            User Row object or None
        """
        user_id = get_current_user_id()
        if user_id:
            return self.db.find('users', user_id)
        return None
