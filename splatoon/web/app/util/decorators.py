from functools import wraps
from http import HTTPStatus
from flask import g, session

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')

        if user_id is None:
            return {'error': 'user is not signed in'}, HTTPStatus.UNAUTHORIZED
        return f(current_user_id=user_id, *args, **kwargs)

    return decorated_function