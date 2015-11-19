import urllib
import logging

from flask import abort
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus import abort

from webapp.utils import AttributeHider
from webapp.api.oauth import oauth
from webapp.api.oauth import AuthorizationRequired
from webapp.api.blueprint import api
from webapp.api.representations import podcast_full_fields, podcast_fields, episode_list
from webapp.podcasts import Podcast


ns = api.namespace("podcasts")

podcast_parser = api.parser()
podcast_parser.add_argument(name="fetch", required=False, location="args")
podcast_parser.add_argument(name="maxEpisodes", required=False, location="args", type=int, default=30)

@ns.route("/<path:podcastId>", endpoint="podcast")
@api.doc(params={
    "podcastId":"A podcast's id (the same as its URL. If the API returns a podcast with a different URL, it means the podcast has moved.",
    "fetch": "Whether to fetch the podcast if it's not in the database.",
    "maxEpisodes": "The maximum number of episodes to return."
})
class PodcastResource(Resource):
    """Resource that represents a podcast."""
    @api.marshal_with(podcast_full_fields)
    @api.doc(id="getPodcast", parser=podcast_parser)
    def get(self, podcastId):
        """Get a podcast by id."""
        args = podcast_parser.parse_args()
        fetch = args.get("fetch")
        max_episodes = args.get("maxEpisodes")
        podcastId = urllib.unquote(podcastId)
        if fetch:
            podcast = Podcast.get_or_fetch(podcastId, max_episodes=max_episodes)
        else:
            podcast = Podcast.get_by_url(podcastId, max_episodes=max_episodes)

        if podcast == None:
            abort(404, message="Podcast not found: %s" % podcastId)
        podcast.ensure_episode_images()
        return podcast

episode_parser = api.parser()
episode_parser.add_argument(name="perPage", required=False, location="args", type=int)
episode_parser.add_argument(name="page", required=False, location="args", type=int)

@ns.route("/details/<path:podcastId>/episodes", endpoint="episodes")
@api.doc(params={
    "podcastId":"A podcast's id (the same as its URL)",
    "perPage": "The number of episodes to return per page.",
    "page": "The page of results to return."
})
class EpisodesResource(Resource):
    """Resource that represent a podcast's episodes"""

    @api.marshal_with(episode_list)
    @api.doc(id="getEpisodes", parser=episode_parser)
    def get(self, podcastId):
        args = episode_parser.parse_args()
        return Podcast.get_episodes(podcastId, args.get("perPage"), args.get("page"))

query_parser = api.parser()
query_parser.add_argument(name="order", required=False, location="args", default="subscriptions")
query_parser.add_argument(name="category", required=False, location="args")
query_parser.add_argument(name="author", required=False, location="args")
query_parser.add_argument(name="language", required=False, location="args")
query_parser.add_argument(name="page", default=1, type=int)
query_parser.add_argument(name="per_page", default=30, type=int)

@ns.route("/")
class PodcastQueryResource(Resource):
    """Resource representing the collection of al podcasts."""

    @api.marshal_with(podcast_fields, as_list=True)
    @api.doc(id="query", parser=query_parser)
    def get(self):
        """Query for podcasts."""
        args = query_parser.parse_args()
        return Podcast.query(**args)
