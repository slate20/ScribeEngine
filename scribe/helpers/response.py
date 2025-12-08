"""
Response helper functions for ScribeEngine templates.

Provides convenient wrappers around Flask response functions.
"""

from flask import redirect as flask_redirect
from flask import abort as flask_abort
from flask import url_for as flask_url_for
from flask import jsonify as flask_jsonify
from flask import make_response


def redirect(location: str, code: int = 302):
    """
    Redirect to another URL.

    Args:
        location: URL to redirect to
        code: HTTP status code (default: 302 temporary redirect)

    Returns:
        Flask redirect response

    Example in template:
        {$
        if not session.get('user_id'):
            return redirect('/login')
        $}
    """
    return flask_redirect(location, code=code)


def abort(code: int, message: str = None):
    """
    Abort request with HTTP error code.

    Args:
        code: HTTP status code (404, 403, 500, etc.)
        message: Optional error message

    Raises:
        HTTPException

    Example in template:
        {$
        post = db.find('posts', post_id)
        if not post:
            abort(404, "Post not found")
        $}
    """
    if message:
        flask_abort(code, description=message)
    else:
        flask_abort(code)


def url_for(endpoint: str, **values):
    """
    Generate URL for endpoint.

    Args:
        endpoint: Route endpoint name
        **values: URL parameters

    Returns:
        URL string

    Example in template:
        <a href="{{ url_for('route_posts_post_id', post_id=123) }}">View Post</a>
    """
    return flask_url_for(endpoint, **values)


def jsonify(*args, **kwargs):
    """
    Create JSON response.

    Returns:
        Flask JSON response

    Example in template:
        {$
        from flask import jsonify
        posts = db.table('posts').all()
        return jsonify({'posts': [dict(p) for p in posts]})
        $}
    """
    return flask_jsonify(*args, **kwargs)


def set_cookie(response, key: str, value: str = '', max_age=None, **kwargs):
    """
    Set a cookie on the response.

    Args:
        response: Flask response object
        key: Cookie name
        value: Cookie value
        max_age: Cookie lifetime in seconds
        **kwargs: Additional cookie parameters

    Returns:
        Modified response

    Example:
        {$
        from flask import make_response
        resp = make_response(redirect('/'))
        set_cookie(resp, 'theme', 'dark', max_age=86400*30)
        return resp
        $}
    """
    response.set_cookie(key, value, max_age=max_age, **kwargs)
    return response
