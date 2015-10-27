import urllib

from flask import abort
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus import abort

from webapp.utils import AttributeHider
from webapp.api.oauth import oauth
from webapp.api.oauth import AuthorizationRequired
from webapp.api.blueprint import api
from webapp.api.representations import podcast_full_fields, podcast_fields
from webapp.podcasts import Podcast


ns = api.namespace("podcasts")

parser = api.parser()
parser.add_argument(name="fetch", required=False, location="args", type=bool)
parser.add_argument(name="max_episodes", required=False, location="args", type=int, default=30)

@ns.route("/<path:podcastId>", endpoint="podcast")
@api.doc(params={"podcastId":"A podcast's id (the same as its URL. If the API returns a podcast with a different URL, it means the podcast has moved."})
class PodcastResource(Resource):
    """Resource that represents a podcast."""
    @api.marshal_with(podcast_full_fields)
    @api.doc(id="getPodcast", parser=parser)
    def get(self, podcastId):
        """Get a podcast by id."""
        args = parser.parse_args()
        fetch = args.get("fetch")
        max_episodes = args.get("max_episodes")
        podcastId = urllib.unquote(podcastId)
        if fetch:
            podcast = Podcast.get_or_fetch(podcastId, max_episodes=max_episodes)
        else:
            podcast = Podcast.get_by_url(podcastId, max_episodes=max_episodes)

        if podcast == None:
            abort(404, message="Podcast not found: %s" % podcastId)
        podcast.ensure_episode_images()
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
    """Resource representing the collection of al podcasts."""

    @api.marshal_with(podcast_fields, as_list=True)
    @api.doc(id="query", parser=queryParser)
    def get(self):
        """Query for podcasts."""
        args = queryParser.parse_args()
        return Podcast.query(**args)
