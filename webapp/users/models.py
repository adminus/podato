import md5
import datetime

import logging

from webapp.db import db, Model

from webapp.users import auth
from webapp.podcasts import SubscriptionHolder
from webapp import utils


class User(Model, auth.ProviderTokenHolder, SubscriptionHolder):
    """Model that represents a user."""
    username = db.StringField(required=True, unique=True)
    primary_email = db.EmailField(required=False)
    email_addresses = db.ListField(db.EmailField())
    avatar_url = db.URLField()
    following = db.ListField(db.ReferenceField("User"))
    joined = db.DateTimeField(default=datetime.datetime.now)

    @classmethod
    def create(cls, username, email, avatar_url=None):
        """Create a new user with the given username, email and avatar url."""
        logging.debug("Create a new user %r" % {
            "username": username,
            "email": email,
            "avatar_url": avatar_url,
        })
        email_hash = None
        emails = []
        if email:
            email_hash = md5.md5(email).hexdigest()
            emails = [email]
        instance = cls(
            username=utils.strip_control_chars(username),
            primary_email=email,
            email_addresses=emails,
            avatar_url=avatar_url or "https://gravatar.com/avatar/%s" % email_hash
        )
        return instance

    def follow(self, other_user):
        self.modify(push__following=other_user)

    def unfollow(self, other_user):
        self.modify(pull_following=other_user)