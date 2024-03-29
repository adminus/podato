from flask import g, Flask
from flask import _app_ctx_stack as stack

from flask import current_app

import rethinkdb as r

from datetime import datetime
import logging


def get_connection():
    host = current_app.config.get("RETHINKDB_HOST")
    port = current_app.config.get("RETHINKDB_PORT")
    db = current_app.config.get("RETHINKDB_DB")
    auth = current_app.config.get("RETHINKDB_AUTH")

    ctx = stack.top
    if ctx is None:
        return

    conn = getattr(ctx, "_db_conn", None)
    if not conn:
        conn = r.connect(host, port, db, auth)
        ctx._db_conn = conn
    return conn


@current_app.teardown_appcontext
def close_connection(exception):
    ctx = stack.top
    conn = getattr(ctx, '_db_conn', None)
    if conn is not None:
        conn.close()

# A dictionary that maps type names (as returned by Model._get_type()) to classes.
TYPE_REGISTRY = {}

class Model(object):
    """A superclass to be used for database models. It has utilities to get a
       database connection, and to turn the object into a dict. Set a table_name property on the class to use the
       'table' property, and get() and save() methods. If not set, the class name,
       converted to lower case with an 's' appended will be used.

       To specify which attributes should be savied add an 'attributes' class property
       containing a list of property names. The first property name should be the primary key."""

    def __init__(self, **kwargs):

        for name in kwargs:
            setattr(self, name, kwargs[name])

    @classmethod
    def get_connection(cls):
        """returns a database connection"""
        return get_connection()

    @classmethod
    def get_attributes(cls):
        attrs = []
        for sup in cls.__mro__:
            if hasattr(sup, "attributes"):
                attrs = attrs + sup.attributes

        unique = []
        for att in attrs:
            if att not in unique:
                unique.append(att)
        return unique

    @classmethod
    def register(cls):
        """Registers a model's type."""
        TYPE_REGISTRY[cls._get_type()] = cls

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

        d = {"__type": self._get_type()}
        for attr in self.get_attributes():
            if not hasattr(self, attr):
                continue
            d[attr] = getattr(self, attr)
        d = self.prepare_value(d)
        return d

    @classmethod
    def prepare_value(cls, value):
        """Ensures that a value can be written to the database."""
        if isinstance(value, datetime):
            return value.replace(tzinfo=r.make_timezone("+00:00"))
        if hasattr(value, "to_dict"):
            value = value.to_dict()
        if isinstance(value, dict):
            return cls._prepare_dict(value)
        if isinstance(value, (set, tuple, list)):
            return [cls.prepare_value(item) for item in value]
        elif not isinstance(value, (basestring, int, float, long, bool)) and value is not None:
            raise ValueError("Values must either implement to_dict, or be of"
                             "type dict, set, tuple, list, basestring, int, "
                             "float, long, datetime or None, got %s: %s" % (type(value), value))
        return value

    @classmethod
    def _prepare_dict(cls, d):
        """Given a dictionary, this method ensures that it is ready to be written to the database."""
        result = {}
        for key in d:
            result[key] = cls.prepare_value(d[key])
        return result

    @classmethod
    def from_dict(cls, d):
        """Converts a dictionary back to the class within the application"""
        if not d:
            return None
        type_ = d.get("__type")
        del d["__type"]

        if type_:
            clss = TYPE_REGISTRY[type_]
        else:
            clss = cls

        for key in d:
            if isinstance(d[key], datetime):
                d[key] = d[key].replace(tzinfo=None)
            if isinstance(d[key], dict) and "__type" in d[key]:
                d[key] = cls.from_dict(d[key])
            if isinstance(d[key], list):
                for i in xrange(len(d[key])):
                    if isinstance(d[key][i], dict) and "__type" in d[key][i]:
                        d[key][i] = cls.from_dict(d[key][i])

        return clss(**d)

    @classmethod
    def _get_type(cls):
        return cls.__name__.lower() + "s"

    @classmethod
    def get_table(cls):
        """Get the table object for this class."""
        default_name = cls._get_type()
        table_name = getattr(cls, "table_name", default_name)
        return r.table(table_name)

    @classmethod
    def run(cls, query):
        """Runs the given query"""
        return query.run(cls.get_connection())

    @classmethod
    def get(cls, id):
        """Get an object by its id."""
        return cls.from_dict(cls.run(cls.get_table().get(id)))

    @property
    def table(self):
        return self.get_table()

    def save(self):
        """Saves the current object"""
        d = self.to_dict()
        logging.debug("saving %s" % d)
        primary = self.get_attributes()[0]
        id = getattr(self, primary)
        res = self.run(self.table.get(id).replace(d))
        logging.debug("result: %s" % res)
        return res

    def delete(self):
        """Deletes the current object"""
        self.run(self.table.get(self.getattr(self.attributes[0])).delete())

    def __repr__(self):
        class_name = self.__class__.__name__
        primary_key = self.get_attributes()[0]
        key_value = getattr(self, primary_key)
        return "<%s %s=%s>" % (class_name, primary_key, key_value)

    def __str__(self):
        return repr(self)


class ValidationError(Exception):
    pass
