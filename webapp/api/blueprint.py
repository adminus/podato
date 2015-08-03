from flask import Blueprint
from flask import current_app

from flask_restplus import Api

api_blueprint = Blueprint("api", __name__, url_prefix="/api")

errors = {
    "AuthorizationRequired": {
        "message": "This operation requires authorization",
        "status": "401"
    }
}

authorize_url ="%s://%s/api/oauth/authorize" % (current_app.config.get("DEFAULT_PROTOCOL"), current_app.config.get("SERVER_NAME"))
token_url = "%s://%s/api/oauth/token" % (current_app.config.get("DEFAULT_PROTOCOL"), current_app.config.get("SERVER_NAME"))
api = Api(api_blueprint,
          ui=True,
          title="Podato API",
          version=0.1,
          authorizations={
            "javascript":{
              "type":"oauth2",
              "flow":"implicit",
              "authorizationUrl": authorize_url,
              "scopes": current_app.config.get("OAUTH_SCOPES")
            },
            "server":{
              "type":"oauth2",
              "flow":"accessCode",
              "scopes":current_app.config.get("OAUTH_SCOPES"),
              "authorizationUrl": authorize_url,
              "tokenUrl": token_url
            }
          }
          )
