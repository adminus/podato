import graphene
from graphene import relay, resolve_only_args
from graphql.core.execution import Executor

from webapp.api.graphql.schemas.users import User

from webapp.api.resources.debug_resources import dictify

class Query(graphene.ObjectType):
    """A user."""
    node = relay.NodeField()
    me = graphene.Field(User)

    @classmethod
    def resolve_me(cls, self, stuff, info):
        return User(username=str(dictify(info)), id="Foo")
