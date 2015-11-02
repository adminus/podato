
from flask_restplus import Resource

from webapp.api.oauth import AuthorizationRequired
from webapp.api.blueprint import api
from webapp.api.oauth import oauth
from webapp.podcasts.progress import PlaybackProgress

ns = api.namespace("episodes")

progress_parser = api.parser()
progress_parser.add_argument(name="progress", location="form", type=int)
@ns.route("/<string:episodeId>/progress")
class ProgressResource(Resource):
    """This resource represents the current user's listening progress on an episode."""
    @api.doc(id="getProgress")
    def get(self, episodeId):
        valid, req = oauth.verify_request([])
        if not valid:
            raise AuthorizationRequired()
        user = req.user

        return {"progress": PlaybackProgress.get_progress(user_id=user.id, episode_id=episodeId)}

    @api.doc(id="setProgress", parser=progress_parser)
    def post(self, episodeId):
        valid, req = oauth.verify_request([])
        if not valid:
            raise AuthorizationRequired()

        user = req.user
        PlaybackProgress.set_progress(user.id, episodeId, progress_parser.parse_args()["progress"])
        return {"success": True}




