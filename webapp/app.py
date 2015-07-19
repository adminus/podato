import logging
import sys

import db
import cache
import flask
import flask_restful


from config import settings
from flask import request
from flask import redirect

app = flask.Flask(__name__)
app.config.from_object(settings)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
db.init_db(app)
cache.init_cache(app)

with app.app_context():
    from users import users_blueprint
    from api import api_blueprint

    import async

    app.register_blueprint(users_blueprint)
    app.register_blueprint(api_blueprint)
    async.init_celery(app)
