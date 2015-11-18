import graphene
from graphene import relay, resolve_only_args

from webapp.users import User as DBUser

class User(relay.Node):
    """A user."""
    username = graphene.StringField(description="The user's username.")

    @classmethod
    def get_node(cls, id):
        cls.from_db_user(DBUser.get_by_id(id))

    @classmethod
    def from_db_user(cls, user):
        return cls(username=user.username)