# app/utils/helpers.py – Utility functions and decorators.

from functools import wraps
from flask import abort
from flask_login import current_user

def login_required_admin(f):
    """
    Custom decorator that ensures the user is authenticated.
    Can be extended for role-based access. Currently same as @login_required.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)  # Unauthorized
        return f(*args, **kwargs)
    return decorated_function

def generate_share_token():
    """Generate a unique token for sharing (UUID4)."""
    import uuid
    return str(uuid.uuid4())