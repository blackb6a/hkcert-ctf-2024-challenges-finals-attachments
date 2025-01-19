from http import HTTPStatus
from flask import make_response, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(get_remote_address, storage_uri='memory://')


def init_app(app):
    limiter.init_app(app)

    @app.errorhandler(429)
    def rate_limit_error_handler(e):
        return {'error': 'request too frequent'}, HTTPStatus.TOO_MANY_REQUESTS
