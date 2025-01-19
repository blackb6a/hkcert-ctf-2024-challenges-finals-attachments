from flask import Flask
import json
import os
from flask_caching import Cache

from app import views
from app import db
from app import cache
from app import limiter


def create_app():
    app = Flask(__name__, static_url_path='/', static_folder='static')
    app.config.from_file('config.json', load=json.load)

    views.init_app(app)
    db.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    return app
