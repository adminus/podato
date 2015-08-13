from flask import current_app as podatoApp
from celery import *
from celery.app.log import Logging
from celery.result import GroupResult
from celery.result import ResultBase, AsyncResult
from celery.signals import before_task_publish
import logging

app = Celery()
Logging(app).setup(loglevel=logging.DEBUG, redirect_level=logging.DEBUG)


def init_celery(podatoApp):
    task_base = app.Task

    app.conf.CELERY_RESULT_BACKEND = podatoApp.config["REDIS_URL"]
    app.conf.BROKER_URL = podatoApp.config["REDIS_URL"]
    app.conf.CELERY_TRACK_STARTED = True
    app.conf.BROKER_POOL_LIMIT = 3

    class TaskWithAppContext(task_base):
        """A celery task that has access to the Flask application context."""
        abstract = True

        def __call__(self, *args, **kwargs):
            with podatoApp.app_context():
                return task_base.__call__(self, *args, **kwargs)

    app.Task = TaskWithAppContext