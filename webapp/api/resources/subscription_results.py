import logging

from flask import request
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus import abort

from webapp.api.oauth import oauth
from webapp.api.blueprint import api
from webapp.api.representations import subscribe_result_fields
from webapp.podcasts import SubscribeResult

ns = api.namespace("subscriptionResults")

@ns.route("/<string:resultId>", endpoint="subscribeResult")
@api.doc(params={"resultId": "A subscription result ID,"})
class SubscriptionResultResource(Resource):
    """Resource representing the result of a podcast subscription request. Such
    requests may take a while, because we might need to fetch the feed if we
    don't already have it in the db.."""

    @api.marshal_with(subscribe_result_fields)
    @api.doc(id="getSubscriptionResult", security=[{"javascript":[]}, {"server":[]}])
    def get(self, resultId):
        """Get a subscription result.."""
        return SubscribeResult.get(resultId)
