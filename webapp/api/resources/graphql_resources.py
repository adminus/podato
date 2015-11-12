from flask_restplus import Resource

from webapp.api.oauth import AuthorizationRequired
from webapp.api.blueprint import api
from webapp.api.oauth import oauth
from webapp.api.graphql.schemas import schema

ns = api.namespace("graphql")

graphql_parser = api.parser()
graphql_parser.add_argument(name="query", location="form", type=str)

@ns.route("/query")
class GraphqlResource(Resource):

    @api.doc(id="query", parser=graphql_parser)
    def post(self):
        valid, req = oauth.verify_request([])
        result = schema.execute(graphql_parser.parse_args()["query"])
        return {"data": result.data, "errors": [str(e) for e in result.errors] if result.errors else None}
