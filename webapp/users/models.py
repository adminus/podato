import md5
import datetime
import random
import logging
import uuid

from webapp.db import r, Model
from webapp import cache

from webapp.users import auth
from webapp.podcasts import SubscriptionHolder
from webapp import utils


class User(Model, auth.ProviderTokenHolder, SubscriptionHolder):
    """Model that represents a user."""

    attributes = ["id", "username", "primary_email", "email_addresses", "avatar_url",
                  "following", "joined", "is_new", "is_email_verified"]

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
            id=str(uuid.uuid4()),
            username=utils.strip_control_chars(username),
            primary_email=email,
            email_addresses=emails,
            avatar_url=avatar_url or "https://gravatar.com/avatar/%s" % email_hash,
            following=[],
            joined=datetime.datetime.now(),
            provided_identities=[],
            subscriptions=[],
            is_new=True,
            is_email_verified=False
        )
        return instance

    @classmethod
    @cache.cached_function(expires=3600)
    def get_by_id(cls, id):
        return cls.from_dict(
            cls.run(
                cls.get_table().get(id)
            )
        )

    def update_profile(self, username=None, email=None, avatar_url=None):
        errors = []
        if username and username != user.username:
            username = utils.strip_control_chars(username)
            if self.is_username_available(username):
                self.username = username
            else:
                errors.append("The username you entered is taken.")

        if email:
            if "@" in email:
                self.primary_email = email
            else:
                errors.append("That email address is invalid.")

        if avatar_url:
            try:
                utils.validate_url(avatar_url)
                self.avatar_url = avatar_url
            except ValueError:
                errors.append("The avatar url is invalid.")

        return errors

    @classmethod
    @cache.cached_function(expires=0)
    def is_username_available(cls, username):
        """Returns True if no user with the given username exists, False otherwise"""
        users = cls.run(cls.get_table().get_all(username, index="username").count())
        logging.debug("Checked for the availability of username %s, got %s" % (username, users))
        return users == 0

    def follow(self, other_user_ids):
        """Follow the users with the given ids"""
        if not isinstance(other_user_idss, list):
            other_user_idss = [other_user_ids]
        self.run(self.table.get(self.id).update(
            {"following": r.row["following"].set_union(other_user_ids)}
        ))

    def unfollow(self, other_user_ids):
        """unfollow the users with the given ids"""
        if not isinstance(other_user_ids, list):
            other_user_ids = [other_user_ids]
        self.run(self.table.get(self.id).update(
            {"following": r.row["following"].set_difference(other_user_ids)}
        ))

User.register()