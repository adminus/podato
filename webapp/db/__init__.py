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

class Model(object):
    """A superclass to be used for database models. It has utilities to get a
       database connection, and to turn the object into a dict."""

    @classmethod
    def get_connection(cls):
        """returns a database connection"""
        return get_connection()

    def to_dict(self):
        """Turn this object into a dicionary. To determine which attributes to
           include, this method looks for an "attributes" object. For example

           class User(Model):
               attributes = ["username", "email", "password_hash", "salt"]
               ...

        When callign to_dict on a user object, this method will look for a "username", "email" etc attribute.
        It'll use the attribute name for the key in tHe dict. If the attribute's value has a to_dict method, it will be called.
        Names in the list that don't correspond to an attribute on the object will be ignored.
        """

        d = {}
        for attr in self.attributes:
            if hasattr(self, attr):
                continue
                
            value = getattr(self, attr)
            if hasattr(value, "to_dict")
                value = value.to_dict()
            if isinstance(value, set, tuple, list):
                value = [item.to_dict() if hasattr(item, "to_dict") else item for item in value]

            d[attr] = value

        return d
