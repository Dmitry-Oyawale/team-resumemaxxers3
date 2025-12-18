from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def role_required(required_role):
    def decorator(view_function):
        @wraps(view_function)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('You must be logged in to access this page.', 'error')
                return redirect(url_for("auth.login"))

            if current_user.role != required_role:
                flash('You do not have permission to access this page.', 'error')

                if current_user.role == 'viewer':
                    return redirect(url_for('main.index'))
                else:
                    return redirect(url_for('main.index'))

            return view_function(*args, **kwargs)

        return wrapper
    return decorator