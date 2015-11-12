import graphene
from graphene import relay, resolve_only_args

from webapp.api.graphql.schemas.users import UserType

class Query(graphene.ObjectType):
    """A user."""
    node = relay.NodeField()
    me = graphene.Field(UserType)

    @classmethod
    def get_user(self, id):
        User.get_by_id(id)

    @resolve_only_args
    def resolve_me(self):
        return None
