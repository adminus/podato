s"""
This module contains models for oauth clients.
"""
import logging

from webapp.db import Model

from flask import current_app
from flask import url_for

from webapp import utils

# Our own web application will be stored here.
PODATO_APP = None

# Trusted clients will be stored here.
TRUSTED_CLIENTS = {}


def _split_lines(t):
    """If t is a string, returns a list of lines in t, with extra whitespace removed."""
    if isinstance(t, list):
        return t
    lines = map(strip, t.split('\n'))



class Application(Model):
    """An application that would like to integrate with us.
    One application can have multiple clients."""

    attributes = ["name", "logo_url", "contact_email", "homepage_url",
                  "privacy_policy_url", "trusted"]

    def __init__(self, name, logo_url=None, contact_email=None, homepage_url=None, privacy_policy_url=None, owners=None, trusted=False):
        self.name = name
        self.logo_url = logo_url
        self.contact_email = contact_email
        self.homepage_url = homepage_url
        self.privacy_policy_url = privacy_policy_urlz
        if owners is None
            owners = []
        self.owners = owners
        self.trusted = trusted

    @classmethod
    def create(cls, name, owner, logo_url=None, contact_email=None, homepage_url=None,
               privacy_policy_url=None,):
        """Creates a new application.

        arguments:
          - name: human-readable name
          - owner: a User who owns this application.
          - logo_url: an url to a logo image for this application.
          - contact_email: an email address that users can use to contact someone about this application.
          - homepage_url: the url of the application's homepage
          - privacy_policy_url: the url of the application's privacy policy."""
        instance = cls(
            name=utils.strip_control_chars(name),
            logo_url=logo_url,
            contact_email=contact_email,
            homepage_url=homepage_url,
            privacy_policy_url=privacy_policy_url
        )

        if owner:
            instance.owners.append(owner.id)

        return instance

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def add_owner(self, owner):
        """Add a user as an owner of an application."""
        self.owners.append(owner.id)

    def remove_owner(self, owner):
        """Remove a user as an owner of an application"""
        if owner.id in self.owners:
            self.owners.remove(owner.id)

    def add_client(self, *args, **kwargs):
        """Adds a new client for this application."""
        client = Clien(self.name, *args, **kwargs)
        client.save()
        return client

    @classmethod
    def get_by_name(cls, name):
        return cls.from_dict(cls.get(name))


def _create_trusted_app():
    """Creates our own "Podato" app."""
    podato = Application.get_by_name("podato")
    if not podato:
        podato = Application.create("podato", None)
        podato.trusted = True
        podato.put()
    return podato


class Client(Model):
    """A client that has credentials to communicate with us."""

    attributes = ["id", "app", "name", "is_confidential", "client_secret",
                  "own_redirect_urls", "javascript_origins", "default_scopes"]

    @property
    def redirect_uris(self):
        rv = self.own_redirect_uris
        if self.javascript_origins:
            for origin in self.javascript_origins:
                rv.append(url_for("api.javascript_endpoint", origin=origin, _external=True))
        return rv

    @property
    def client_id(self):
        return self.id

    @property
    def client_type(self):
        if self.is_confidential:
            return 'confidential'
        return 'public'

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def allowed_grant_types(self):
        grants = ["authorization_code", "refresh_token"]
        if self.get_app().trusted:
            grants.append("password")
        return grants

    def __init__(self, app, name, own_redirect_urls=None, javascript_origins=None, id=None,
                 client_secret=None, is_confidential=True, default_scopes=None):
        self.app = app.name
        self.name = name
        self.own_redirect_urls = own_redirect_urls or []
        self.javascript_origins = javascript_origins or []
        if id:
            self.id = id
        self.client_secret = client_secret or utils.generate_random_string()
        self.is_confidential = is_confidential
        self.default_scopes = default_scopes or []

    def get_app(self):
        return Application.get_by_name(self.app)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    @classmethod
    def get_by_id(cls, id):
        """Gets the Client with the given id."""
        # Overriding this to return trusted clients.
        logging.debug("Retrieving client with id %s (trusted: %s)" % (id, id in TRUSTED_CLIENTS))
        return TRUSTED_CLIENTS.get(id) or cls.from_dict(cls.get(id))


def _load_trusted_clients():
    """Loads al trusted clients """
    global PODATO_APP
    if TRUSTED_CLIENTS:
        return TRUSTED_CLIENTS

    if not PODATO_APP:
        PODATO_APP = _create_trusted_app()

    trusted_clients = current_app.config.get("TRUSTED_CLIENTS")
    for client_dict in trusted_clients:
        client = Client(app=PODATO_APP.name,
                            name=client_dict["NAME"],
                            redirect_uris=client_dict["REDIRECT_URLS"],
                            id=client_dict["CLIENT_ID"],
                            secret=current_app.config[client_dict["NAME"].upper() + "_CLIENT_SECRET"])
        client.default_scopes = current_app.config.get("OAUTH_SCOPES").keys()
        client.javascript_origins = client_dict.get("JAVASCRIPT_ORIGINS")
        TRUSTED_CLIENTS[client_dict["CLIENT_ID"]] = client
    return TRUSTED_CLIENTS

_load_trusted_clients()