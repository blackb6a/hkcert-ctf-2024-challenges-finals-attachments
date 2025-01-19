from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

def init_app(app):
    cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})
