import logging
import sys
import cache
import flask
import flask_restful

from config import settings
from flask import request
from flask import redirect

app = flask.Flask(__name__)
app.config.from_object(settings)
logging.basicConfig(level=logging.DEBUG)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)
cache.init_cache(app)

with app.app_context():
    from users import users_blueprint
    from api import api_blueprint
    import db
    import async

    app.register_blueprint(users_blueprint)
    app.register_blueprint(api_blueprint)
    async.init_celery(app)

    @app.before_request
    def log_request():
        r = flask.request
        logging.info("received request %s %s" % (r.method, r.url))