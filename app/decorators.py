from functools import wraps
from flask import abort
from flask_login import current_user


def super_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if (not current_user.is_anonymous) and current_user.is_super():
            return f(*args, **kwargs)
        else:
            abort(403)
    return decorated_function
