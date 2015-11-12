import graphene
from graphene import relay

from webapp.users import User as DBUser

class UserType(relay.Node):
    """A user."""
    username = graphene.StringField(description="The user's username.")

    @classmethod
    def get_node(self, id):
        User.get_by_id(id)
