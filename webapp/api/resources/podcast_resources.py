import urllib

from flask import abort
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus import abort

from webapp.utils import AttributeHider
from webapp.api.oauth import oauth
from webapp.api.oauth import AuthorizationRequired
from webapp.api.blueprint import api
from webapp.api.models import podcast_full_fields, podcast_fields
from webapp.podcasts import Podcast


ns = api.namespace("podcasts")

@ns.route("/<path:podcastId>", endpoint="podcast")
@api.doc(params={"podcastId":"A podcast's id (the same as its URL. If the API returns a podcast with a different URL, it means the podcast has moved."})
class PodcastResource(Resource):

    @api.marshal_with(podcast_full_fields)
    @api.doc(id="getPodcast")
    def get(self, podcastId):
        podcastId = urllib.unquote(podcastId)
        podcast = Podcast.get_by_url(podcastId)
        if podcast == None:
            abort(404, message="Podcast not found: %s" % podcastId)
        return podcast

queryParser = api.parser()
queryParser.add_argument(name="order", required=False, location="args", default="subscriptions")
queryParser.add_argument(name="category", required=False, location="args")
queryParser.add_argument(name="author", required=False, location="args")
queryParser.add_argument(name="language", required=False, location="args")
queryParser.add_argument(name="page", default=1, type=int)
queryParser.add_argument(name="per_page", default=30, type=int)

@ns.route("/")
class PodcastQueryResource(Resource):

    @api.marshal_with(podcast_fields, as_list=True)
    @api.doc(id="query", parser=queryParser)
    def get(self):
        args = queryParser.parse_args()
        query = Podcast.objects
        if args.get("order"):
            query = query.order_by(args.get('order'))
        if args.get("category"):
            query = query.filter(categories=args.get("category"))
        if args.get("author"):
            query = query.filter(author=args.get("author"))
        if args.get("language"):
            query = query.filter(language=args.get("language"))

        return query.paginate(page=args["page"], per_page=args["per_page"]).items
