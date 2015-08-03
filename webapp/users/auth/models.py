import logging

from flask import abort
from webapp.db import db

from webapp.users.auth import facebook_api
from webapp.users.auth.providers import TwitterProvider

class ProvidedIdentity(db.EmbeddedDocument):
    """Model that represents a user identity as provided by a 3rd party identity provider."""
    provider = db.StringField(required=True)
    user_id = db.StringField(required=True)
    access_token = db.StringField(required=True)


class ProviderTokenHolder(object):
    """This is a mixin for User, which stores the auth tokens of 3rd party providers like Facebook or Google"""

    provided_identities = db.EmbeddedDocumentListField(ProvidedIdentity)

    def add_provided_identity(self, provider, user_id, access_token):
        # If the user already has an identity from the given platform with the given id,
        # update its access_token
        logging.debug("Adding provided identity to user. %r" % {
            "provider": provider,
            "user_id": user_id,
            "app_user": self.id
                                                               })
        for identity in self.provided_identities:
            if identity.provider == provider and identity.user_id == user_id:
                identity.access_token = access_token
                self.put()
                logging.debug("identity already found on user. Updating access token.")
                return

        prid = ProvidedIdentity(
            provider="facebook",
            user_id=user_id,
            access_token=access_token
        )
        self.modify(push__provided_identities=prid)
        logging.debug("Added provided identity.")

    def get_provider_token(self, provider, user_id=None):
        """Gets the access token for a specific provided identity."""
        for identity in self.provided_identities:
            if identity.provider == provider:
                if user_id == None or identity.user_id == user_id:
                    return identity.access_token
        return None

    @classmethod
    def get_by_provided_identity(cls, provider, user_id):
        """Gets the User associated with the given provided identity."""
        user = cls.objects(provided_identities__provider=provider, provided_identities__user_id=user_id).first()
        logging.debug("Tried to get user by provided identity. %r" % {
            "provider": provider,
            "user_id": user_id,
            "found": user
        })
        return user

    @classmethod
    def login(cls, provider, provider_response):
        """Get or create the user given the name of the auth provider, and the provider's response."""
        logging.debug("login attempt with %s" % provider)
        if not hasattr(cls, "login_%s" % provider):
            logging.debug("provider not found")
            abort(404)
        return getattr(cls, "login_%s" % provider)(provider_response)

    @classmethod
    def login_facebook(cls, facebook_response):
        """Gets or creates a user, based on the facebook_response."""
        try:
            access_token = facebook_response["access_token"]
            logging.debug("Got access token from facebook.")
        except:
            raise ValueError("%s: %s\n%s" % (facebook_response.type, facebook_response.message, facebook_response.data))
        fb_user = facebook_api.get_current_user(access_token)
        logging.debug("Got facebook user: %r" % fb_user)
        user = cls.get_by_provided_identity("facebook", fb_user["id"])
        if not user:
            user = cls.create(fb_user["name"], fb_user["email"], facebook_api.get_avatar(fb_user["id"]))
            user.put()
            logging.debug("Saved new user.")
        user.add_provided_identity("facebook", fb_user["id"], access_token)
        return user

    @classmethod
    def login_twitter(cls, twitter_response):
        access_token = twitter_response.get("access_token")
        logging.debug("Got twitter access token.")
        tw_user = TwitterProvider.api(access_token).me()
        logging.debug("Got twitter user: %r" % tw_user)
        user = cls.get_by_provided_identity("twitter", tw_user.id_str)
        if not user:
            user = cls.create(tw_user.screen_name, None, tw_user.profile_image_url_https)
            user.put()
            logging.debug("Saved new user.")
        user.add_provided_identity("twitter", tw_user.id_str, access_token)
        return user

    @classmethod
    def login_google(cls, google_response):
        try:
            access_token = google_response["access_token"]
        except:
            raise ValueError("%s: %s\n%s" % (google_response.type, google_response.message, google_response.data))
        raise ValueError("response: %s" % google_response)