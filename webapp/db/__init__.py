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

# A dictionary that maps type names (as returned by Model._get_type()) to classes.
TYPE_RERISTRY = {}

class Model(object):
    """A superclass to be used for database models. It has utilities to get a
       database connection, and to turn the object into a dict. Set a table_name property on the class to use the
       'table' property, and get() and save() methods. If not set, the class name,
       converted to lower case with an 's' appended will be used.

       To specify which attributes should be savied add an 'attributes' class property
       containing a list of property names. The first property name should be the primary key."""


    @classmethod
    def get_connection(cls):
        """returns a database connection"""
        return get_connection()

    @classmethod
    def get_attributes(cls):
        attrs = set()
        for sup in cls.__mro__:
            if hasattr(sup, "attributes"):
                attrs = attrs.union(sup.attributes)

        return attrs

    @classmethod
    def __new__(cls, *args, **kwargs):
        """Registers a model's type when it is instantiated."""
        TYPE_RERISTRY[cls._get_type()] = cls
        return super(Model, cls).__new__(cls, *args, **kwargs)

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
            if hasattr(self, attr):
                continue

            value = getattr(self, attr)
            if hasattr(value, "to_dict"):
                value = value.to_dict()
            if isinstance(value, set, tuple, list):
                value = [item.to_dict() if hasattr(item, "to_dict") else item for item in value]

            d[attr] = value

        return d

    @classmethod
    def from_dict(cls, d):
        """Converts a dictionary back to the class within the application"""
        if not d:
            return None
        type_ = d.get("__type", None)
        if type_:
            clss = TYPE_RERISTRY[type_]
        else:
            clss = cls

        for key in d:
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
        query.run(cls.get_connection())

    @classmethod
    def get(cls, id):
        """Get an object by its id."""
        return cls.run(cls.get_table().get(id))

    @property
    def table(self):
        return self.get_table()

    def save(self):
        """Saves the current object"""
        d = self.to_dict()
        return self.run(self.table.replace(d))

    def delete(self):
        """Deletes the current object"""
        self.run(self.table.get(self.getattr(self.attributes[0])).delete())


class ValidationError(Exception):
    pass
