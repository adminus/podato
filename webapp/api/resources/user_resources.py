import logging

from flask import request
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus import abort

from webapp.utils import AttributeHider
from webapp.api.oauth import oauth
from webapp.api.oauth import AuthorizationRequired
from webapp.api.blueprint import api
from webapp.api.representations import user_fields, subscribe_fields, podcast_fields, success_status, subscribe_result_fields
from webapp.users import User
from webapp.users.auth import session

ns = api.namespace("users")


@ns.route("/<string:userId>", endpoint="user")
@api.doc(params={"userId": "A user ID, or \"me\" without quotes, for the user associated with the provided access token."})
class UserResource(Resource):
    """Resource representing a single user."""
    @api.marshal_with(user_fields)
    @api.doc(id="getUser", security=[{"javascript":[]}, {"server":[]}])
    def get(self, userId):
        """Get a user."""
        if userId == "me":
            valid, req = oauth.verify_request(["publicuserinfo/read"])
            if not valid:
                raise AuthorizationRequired()
            user = req.user
        else:
            user = User.get_by_id(userId)

        if not user:
            abort(404, message="User not found: %s." % userId)
            return

        # make sure the client is authorized to get the user's email.
        valid, req = oauth.verify_request(["userinfo/email"])
        if not (valid and (userId == "me" or userId == req.user.id)):
            return AttributeHider(user, ["primary_email"])
        return user

followParser = api.parser()
followParser.add_argument(name="otherUser", required=True, location="values")

@ns.route("/<string:userId>/following", endpoint="following")
@api.doc({"userId": "A user ID, or \"me\" without quotes, for the user associated with the provided access token."})
class FollowingResource(Resource):
    @api.marshal_with(success_status)
    @api.doc(id="follow", security=[{"javascript":[]}, {"server":[]}], parser=followParser)
    def post(self, userId):
        if userId == "me":
            valid, req = oauth.verify_request([])
            follow = followParser.parse_args()["otherUser"].split(",")
            if not valid:
                raise AuthorizationRequired()
            user = req.user
            others = [User.get_by_id(f) for f in follow]
            user.follow(others)
            return {"success": True}

    @api.marshal_with(success_status)
    @api.doc(id="unfollow", security=[{"javascript":[]}, {"server":[]}], parser=followParser)
    def delete(self, userId):
        if userId == "me":
            valid, req = oauth.verify_request([])
            if not valid:
                raise AuthorizationRequired()
            unfollow = followParser.parse_args()["otherUser"].split(",")
            others = [User.get_by_id(u) for u in unfollow]
            req.user.unfollow(others)
            return {"success": True}

    @api.marshal_with(user_fields, as_list=True)
    @api.doc(id="getFollowing")
    def get(self, userId):
        user = User.get_by_id(userId)
        return user.following


podcastsParser = api.parser()
podcastsParser.add_argument(name="podcast", required=True, location="form")

@ns.route("/<string:userId>/subscriptions", endpoint="subscriptions")
@api.doc({"userId": "A user ID, or \"me\" without quotes, for the user associated with the provided access token.", "podcast":"a podcast feed url."})
class SubscriptionsResource(Resource):
    """Resource representing a user's subscriptions."""
    @api.marshal_with(subscribe_result_fields)
    @api.doc(id="subscribe", security=[{"javascript":[]}, {"server":[]}], parser=podcastsParser)
    def post(self, userId):
        """Subscribe the user to a podcast"""
        podcasts = podcastsParser.parse_args()["podcast"].split(",")
        if userId == "me":
            valid, req = oauth.verify_request([])
            if not valid:
                raise AuthorizationRequired()
            user = req.user
            res = user.subscribe_multi_by_url(podcasts)
            logging.error("Result from user.subscribe_multi_by_url: %s" % res)
            return res



    @api.marshal_with(success_status)
    @api.doc(id="unsubscribe", parser=podcastsParser)
    def delete(self, userId):
        """Unsubscribe the user from a podcast."""
        podcast = podcastsParser.parse_args()["podcast"]
        if userId == "me":
            valid, req = oauth.verify_request([])
            if not valid:
                raise AuthorizationRequired()
            user = req.user
        else:
            user = User.get_by_id(userId)

        return user.unsubscribe_by_url(podcast)

    @api.marshal_with(podcast_fields, as_list=True)
    @api.doc(id="getSubscriptions", security=[{"javascript":[]}, {"server":[]}])
    def get(self, userId):
        """Get all the user's subscriptions."""
        if userId == "me":
            valid, req = oauth.verify_request([])
            if not valid:
                raise AuthorizationRequired()
            user = req.user
        else:
            user = User.get_by_id(userId)
        if not user:
            abort(404, message="User not found.")
            return
        return user.get_subscriptions()


@ns.route("/logout", endpoint="logout")
class Logout(Resource):
    """Log out the current user. This method can only be called by trusted applications."""
    @api.doc(id="logout", security=[{"javascript":[]}, {"server":[]}])
    def get(self):
        valid, req = oauth.verify_request([])
        if not valid or not req.client.get_app().trusted:
            raise AuthorizationRequired
        session.destroy_session()
        return {"success": True}