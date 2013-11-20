from flask import g, redirect, url_for, request
from functools import wraps

def requires_login(func):
    @wraps(func)
    def _login(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.path))
        return func(*args, **kwargs)
    return _login