import os
import urlparse


from flask import request
from flask import url_for
from flask import redirect
from flask import render_template
from flask import abort

from webapp import cache
from webapp.users.blueprint import  users_blueprint
from webapp.users import models
from webapp.users.auth.providers import get_provider
from webapp.users.auth import session
from webapp.users.auth import errors



def _validate_next(next):
    """next must be a relative url, or its host must match the host where the request is running."""
    parsed = urlparse.urlparse(next)
    if parsed.netloc and parsed.netloc != request.host:
        raise errors.AuthError("Can't redirect to an absolute url after login. (%s is absolute.)" % next)

def _save_next(next):
    """Save the url to go to after login, and return te key with which it is associated."""
    key = os.urandom(16).encode("hex")
    cache.set(key, next, 600)
    return key


def _get_next(key):
    """Get the url to go to after login, by its associated key."""
    return cache.get(key)


@users_blueprint.route("/login")
def login():
    """Show a page to select a login provider."""
    next = request.args.get("next")
    return render_template("login.html", next=next)


@users_blueprint.route("/login/<provider>")
def provider_login(provider):
    """Log in with the given provider."""
    # The next_token doesn't only store the 'next' value, but it also acts as a CSRF token.
    next = request.args.get("next") or "/"
    next_token = _save_next(next)

    provider_instance = get_provider(provider)
    if not provider_instance:
        abort(404)

    # Twitter uses OAuth 1.0a, which doesn't support the 'state' parameter, so we include it in the callback url.
    callback_state = None
    if provider == "twitter":
        callback_state = next_token

    return provider_instance.authorize(callback=url_for("auth.authorized", _external=True, provider=provider, state=callback_state), state=next_token)


@users_blueprint.route("/authorized/<provider>")
def authorized(provider):
    provider_instance = get_provider(provider)
    if not provider_instance:
        abort(404)

    resp = provider_instance.authorized_response()
    next = _get_next(request.args.get("state"))
    _validate_next(next)
    user = models.User.login(provider, resp)
    session.create_session_token(user)
    if user.is_new:
        return redirect(url_for("auth.signup", next=next))
    return redirect(next)


@users_blueprint.route("/signup", methods=["GET", "POST"])
def signup():
    user = session.get_user()
    username = request.values.get("username", user.username)
    email = request.values.get("email", user.primary_email)
    next = request.values.get("next")

    errors = []
    if request.method == "POST":
        errors = user.update_profile(email=email, username=username)
        if len(errors) == 0:
            user.is_new = False
            user.save()
            return redirect(next)

    return render_template("signup.html", email=email, username=username, next=next, errors=errors)
