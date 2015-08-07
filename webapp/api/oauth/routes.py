import logging

from flask import render_template
from flask import request

from webapp.api.blueprint import api_blueprint
from webapp.api.oauth import oauth
from webapp.api.oauth import clients
from webapp.users.auth import session


@api_blueprint.route('/oauth/token')
@oauth.token_handler
def access_token():
    pass # We don't need to actually do anything, just attach the handler.


@api_blueprint.route('/oauth/authorize', methods=['GET', 'POST'], endpoint="authorize")
@session.require
@oauth.authorize_handler
def authorize(*args, **kwargs):
    if request.method == 'GET':
        client_id = kwargs.get('client_id')
        client = clients.Client.get_by_id(client_id)
        kwargs['client'] = client

        if client.get_app().trusted == True:
            return True #we don't ask the user for permissions for our own "trusted" app.

        return render_template('oauthorize.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'

@api_blueprint.route("/oauth/js")
def javascript_endpoint():
    return render_template("oauth_js.html")