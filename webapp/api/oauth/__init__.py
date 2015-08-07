from flask import current_app
from flask_oauthlib.provider import OAuth2Provider

from webapp.api.oauth import clients
from webapp.api.oauth import tokens
from webapp.api.oauth.oauth import oauth

from webapp.users import User
from webapp.users.auth import session


class AuthorizationRequired(Exception):
    pass


@oauth.clientgetter
def load_client(client_id):
    return clients.Client.get_by_id(client_id)


@oauth.grantgetter
def load_grant(client_id, code):
    return tokens.GrantToken.lookup(client_id, code)


@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    grant = tokens.GrantToken.create(client_id, code["code"], session.get_user(),
                                     request.redirect_uri, request.scopes)
    grant.save()
    return grant


@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return tokens.BearerToken.get_by_access_token(access_token=access_token)
    else:
        return tokens.BearerToken.get_by_refresh_token(refresh_token=refresh_token)


@oauth.tokensetter
def save_token(token, request):
    tokens.BearerToken.create(
        client=request.client,
        user=session.get_user(),
        access_token=token["access_token"],
        refresh_token=token.get("refresh_token"),
        expires_in=token["expires_in"],
        scopes=token["scope"].split(),
        token_type=token["token_type"]
    ).save()


@oauth.invalid_response
def handle_invalid_response(request):
    raise AuthorizationRequired()

import routes





