import graphene
from webapp.api.graphql.schemas.query import Query

#TODO: as soon as rethinkdb support for gevent ships, switch to using the gevent executor.
schema = graphene.Schema(name="Podato schema")
schema.query = Query
