from flask import current_app as podatoApp
from celery import *
from celery.result import ResultBase, AsyncResult
from celery.signals import before_task_publish

import logging

app = Celery()
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


class AsyncSuccess(object):
    """This class represents the result of an async operation."""

    def __init__(self, async_result=None, success=None):
        """Create a new result for an async operation. Only one of async_result and success should be given.
        async_result should be a celery AsyncResult. success should be a boolean. Passing in a value for success means that the operation has already been completed,
        so the success state is known.
        A task that failed or succeeded immediately may not have an id.
        """
        if async_result != None and success != None:
            raise ValueError("async_result and success shouldn't both be given.")

        if async_result == None and success == None:
            raise ValueError("Either async_result or success must be given.")

        self.id = async_result.id if async_result else None
        self.async_result = async_result
        self._success = success
        self._final_async_result_cache = None

    @property
    def _final_async_result(self):
        """Within Celery, one task may start another. This method traverses the chain of tasks to get to the last one, to get its state. For internal use only."""
        if self._final_async_result_cache:
            return self._final_async_result_cache

        self._final_async_result_cache = list(self._iter_async_results())[-1]
        return self._final_async_result_cache

    def _iter_async_results(self):
        """Iterate over the chain of async results."""
        if not self.async_result:
            return

        result = self.async_result
        lastResult = self.async_result
        while True:
            if isinstance(result, ResultBase):
                lastResult = result
                result = result.result
                yield lastResult
            else:
                return

    @property
    def success(self):
        """Whether this operation was successful"""
        if self._success != None:
            return self._success

        if self.state == "DOESNOTEXIST":
            return False

        return not isinstance(self._final_async_result.result, Exception)

    @property
    def state(self):
        """Gets the state of this operation. It can be DOESNOTEXIST if you'veasked
           for a task by id that does not exist, QUEUED if the task is in the queue,
           awaiting execution, SUCCESS if the task succeeded or FAILURE if the task failed."""

        if self._success != None:
            return {True: "SUCCESS", False: "FAILURE"}[self._success]
        if self.async_result.state == "PENDING":
            state = "DOESNOTEXIST"
        if self.async_result.state == "QUEUED":
            return "QUEUED"
        last = self._final_async_result
        if last.state in ["SUCCESS", "FAILURE", "STARTED"]:
            return last.state
        return "STARTED"


    @classmethod
    def get(cls, id):
        """Get a task by its id."""
        return cls(async_result=AsyncResult(id))

    def __repr__(self):
        return "<AsyncSuccess #%s success=%s state=%s>" % (self.id, self.success, self.state)