from app.views import api
from app.views import pages
from app.views import ticks


def init_app(app):
    app.register_blueprint(api.route, url_prefix='/api/')
    app.register_blueprint(pages.route, url_prefix='/')
    app.register_blueprint(ticks.route, url_prefix='/tick/')
