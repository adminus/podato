from flask import current_app
from flask import redirect
from flask import request
from flask import session
from oauth2client import client
import apiclient

import httplib2

class GoogleProvider(object):
    @classmethod
    def make_flow(cls, callback=None):
        if callback:
            session["google_callback"] = callback
        else:
            callback = session["google_callback"]
        return client.OAuth2WebServerFlow(
            client_id=current_app.config["GOOGLE_CONSUMER_KEY"],
            client_secret=current_app.config["GOOGLE_CONSUMER_SECRET"],
            scope=["https://www.googleapis.com/auth/plus.login","https://www.googleapis.com/auth/plus.profile.emails.read"],
            user_agent="Podato",
            redirect_uri=callback
        )

    @classmethod
    def authorize(cls, callback, state=None, **kwargs):
        flow = cls.make_flow(callback)
        return redirect(flow.step1_get_authorize_url())

    @classmethod
    def authorized_response(cls):
        code = request.args["code"]
        flow = cls.make_flow()
        creds = flow.step2_exchange(code=code)
        return {"access_token": creds.to_json()}

    @classmethod
    def get_service(cls, service, version, access_token=None):
        http = httplib2.Http()

        if access_token:
            creds = client.OAuth2Credentials.from_json(access_token)
            creds.authorize(http)

        return apiclient.discovery.build(service, version, http=http)

    @classmethod
    def getUser(cls, access_token=None, user_id="me"):
        return cls.get_service("plus", "v1").people().get(userId=user_id)