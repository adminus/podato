import md5
import datetime
import random
import logging

from webapp.db import r, Model

from webapp.users import auth
from webapp.podcasts import SubscriptionHolder
from webapp import utils


class User(Model, auth.ProviderTokenHolder, SubscriptionHolder):
    """Model that represents a user."""

    attributes = ["id", "username", "primary_email", "email_addresses", "avatar_url",
                  "following", "joined"]

    def __init__(self, id=None, username=None, primary_email=None, email_addresses=None,
                 avatar_url=None, following=None, joined=None, **kwargs):
        super(User, self).__init__(self, **kwargs)
        self.username = username
        self.primary_email = primary_email
        self.email_addresses = email_addresses or []
        self.avatar_url = avatar_url
        self.following = following
        self.joined = joined

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
        while not cls.is_username_available(username):
            username += random.choice("1234567890")

        instance = cls(
            username=utils.strip_control_chars(username),
            primary_email=email,
            email_addresses=emails,
            avatar_url=avatar_url or "https://gravatar.com/avatar/%s" % email_hash
        )
        return instance

    @classmethod
    def get_by_id(cls, id):
        return cls.from_dict(
            cls.run(
                cls.get_table().get(id)
            )
        )

    @classmethod
    def is_username_available(cls, username):
        return cls.run(cls.table.get_all(username, index=username).count()) == 0

    def follow(self, other_user_ids):
        if not isinstance(other_user_idss, list):
            other_user_idss = [other_user_ids]
        self.run(self.table.get(self.id).update(
            {"following": r.row["following"].set_union(other_user_ids)}
        ))

    def unfollow(self, other_user_ids):
        if not isinstance(other_user_ids, list):
            other_user_ids = [other_user_ids]
        self.run(self.table.get(self.id).update(
            {"following": r.row["following"].set_difference(other_user_ids)}
        ))