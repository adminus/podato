from flask import request
from flask import current_app
from flask import session
from flask import redirect
from flask_oauthlib.contrib.apps import facebook, google, twitter
from flask_oauthlib.client import OAuth

import tweepy
tweepy.TweepError

def _make_token_getter(provider):
    def token_getter():
        user = request.oauth.user
        return (user.get_provider_token(provider), "")
    return token_getter

oauth = OAuth()

facebook = facebook.register_to(oauth, scope=["public_profile", "email"])
facebook.tokengetter(_make_token_getter("facebook"))

google = google.register_to(oauth, scope=["https://www.googleapis.com/auth/plus.profile.emails.read"])
google.tokengetter(_make_token_getter("google"))

class TwitterProvider(object):
    @classmethod
    def make_auth(cls, callback_url=None, request_token=None, access_token=None):
        cons_key = current_app.config["TWITTER_CONSUMER_KEY"]
        cons_sec = current_app.config["TWITTER_CONSUMER_SECRET"]

        auth = tweepy.OAuthHandler(cons_key, cons_sec, callback_url)
        if request_token:
            auth.request_token = request_token
        if access_token:
            auth.set_access_token(*access_token.split("\n"))
        return auth

    @classmethod
    def authorize(cls, callback, **kwargs):
        auth = cls.make_auth(callback)
        url = auth.get_authorization_url()
        session["twitter_request_token"] = auth.request_token
        return redirect(url)

    @classmethod
    def authorized_response(cls):
        verifier = request.args.get("oauth_verifier")
        request_token = session["twitter_request_token"]
        del session["twitter_request_token"]
        auth = cls.make_auth(request_token=request_token)
        try:
            auth.get_access_token(verifier)
        except tweepy.TweepError as e:
            raise ValueError(e.reason)

        return {"access_token": cls.make_access_token(auth.access_token, auth.access_token_secret)}

    @classmethod
    def make_access_token(cls, access_token, token_secret):
        return access_token + "\n" + token_secret

    @classmethod
    def api(cls, access_token):
        auth = cls.make_auth(access_token=access_token)
        return tweepy.API(auth)

def get_provider(provider):
    """Returns the requested identity provider or None if it doesn't exist."""
    return {
        "facebook": facebook,
        "google": google,
        "twitter": TwitterProvider
    }.get(provider)
