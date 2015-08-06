from flask import g
from flask import current_app

import rethinkdb as r

def get_connection():
    host = current_app.config.get("RETHINKDB_HOST")
    port = current_app.config.get("RETHINKDB_PORT")
    db = current_app.config.get("RETHINKDB_DB")
    auth = current_app.config.get("RETHINKDB_AUTH")

    conn = getattr(g, "_db_conn", None)
    if not conn:
        conn = r.connect(host, port, db, auth)
        g._db_conn = conn
    return conn


@current_app.teardown_appcontext
def close_connection(exception):
    conn = getattr(g, '_db_conn', None)
    if conn is not None:
        conn.close()