web: uwsgi uwsgi.ini
worker: celery worker -A webapp.async.app -P eventlet -c 2