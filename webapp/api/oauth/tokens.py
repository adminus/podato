import datetime
import cPickle

from webapp.db import Model
from webapp.users import User
from webapp import cache
from clients import Client

from webapp import utils


class BaseToken(Model):
    @property
    def user(self):
        return User.get_by_id(self.user_id)

    @property
    def client(self):
        return Client.get_by_id(self.client_id)


class GrantToken(BaseToken):
    """Grant token, to be exchanged for a BearerToken."""

    attributes = ["id", "client_id", "code", "user_id", "redirect_uri", "scopes", "expires"]

    def __init__(self, id, client_id, code, user_id, redirect_uri, scopes, expires=None):
        self.client_id = client_id
        self.user_id = user_id
        self.code = code
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self.expires = expires or datetime.datetime.utcnow() + datetime.timedelta(seconds=120)

    @classmethod
    def create(cls, client_id, code, user, redirect_uri, scopes):
        """Creates a new GrantToken

        client_id: The id of the client to which this grant token was issued.
        code: The code associated with this token, used for lookup.
        user: The user who is asked to grant access.
        redirect_uri: the uri to be redirected to after access is granted
        scopes: the requested oauth scopes.
        """
        instance = cls(
            client_id=client_id,
            user_id=user.id,
            redirect_uri=redirect_uri,
            scopes=scopes,
            expires=expires,
            code=code,
            id=cls.make_id(client_id, code)
        )
        return instance

    @classmethod
    def make_id(cls, client_id, code):
        """A consistent way to make an id for a grant_token."""
        return "%s-%s" % (client_id, code)

    @classmethod
    def lookup(cls, client_id, code):
        """Looks up a grant token for the given client and code."""
        return cache.get("GRANT_TOKEN_"+cls.make_id(client_id, code))

    def save(self):
        """Override save(), because we want to store granttokens in the cache."""
        s = cPickle.dumps(self)
        cache.set("GRANT_TOKEN_"+self.id, s)


class BearerToken(BaseToken):
    """Token that clients can use to access resources."""

    attributes = ["access_token", "refresh_token", "client_id", "user_id", "scopes",
                  "expires", "token_type"]

    def __init__(self, access_token, refresh_token, client_id, user_id, scopes=None, expires=None, token_type=None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.user_id = user_id
        self.scopes = scopes
        self.expires = expires
        self.token_typ = token_type

    @classmethod
    def create(cls, access_token, refresh_token, client, user, expires_in,
               token_type, scopes):
        """Create a new bearer token.

        arguments:
         - access_token: the access token
         - refresh_token: the refresh token
         - client: the Client object that can use this token
         - user: the User object, who has granted access to the client
         - expires_in: the number of seconds until this token expires
         - token_type: the token type.
         - scopes: a list of scopes.
         """
        expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
        return cls(access_token=access_token,
                   refresh_token=refresh_token,
                   client_id=client.client_id,
                   user_id=user.id,
                   token_type=token_type,
                   scopes=scopes,
                   expires=expires)

    @classmethod
    def get_by_access_token(cls, access_token):
        """Get a Bearer token by access token."""
        result = cls.run(cls.get_table().get_all(access_token, index="access_token"))
        if result:
            return cls.from_dict(result[0])
        return None

    @classmethod
    def get_by_refresh_token(cls, refresh_token):
        """Get a Bearer token by its refresh token."""
        result = cls.run(cls.get_table().get_all(refresh_token, index="refresh_token"))
        if result:
            return cls.from_dict(result[0])
        return None