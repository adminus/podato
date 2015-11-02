from webapp.db import Model, r
from webapp import cache

class PlaybackProgress(Model):
    """Represents listening progress of a particular user with a particular episode. Progress is represented as an integer number of seconds."""
    attributes=["id", "user_id", "episode_id", "progress"]
    table_name="playbackprogress"

    @classmethod
    def set_progress(cls, user_id, episode_id, progress):
        id = cls._make_id(user_id, episode_id)
        cls.run(
            cls.get_table().get(id).replace({
                "id": id,
                "episode_id": episode_id,
                "user_id": user_id,
                "progress": progress
            })
        )
        cache.set("progress_%s" % id, progress)

    @classmethod
    def get_progress(cls, user_id, episode_id):
        id = cls._make_id(user_id, episode_id)
        progress = cache.get("progress_%s" % id)
        return progress or cls.get(id).progress

    @classmethod
    def get_multi(cls, user_id, *episode_ids):
        results = {}
        ids = [cls._make_id(user_id, e_id) for e_id in episode_ids]
        cached_results = cache.get_multi(ids)

        for id in cached_results:
            ids.remove(id)
            results[cls._episode_id_from_id(id)] = cached_results[id]

        if len(ids) == 0:
            return results

        db_results = cls.run(
            cls.get_table().get_all(*ids).pluck("__type__", "progress", "episode_id")
        )
        for result in db_results:
            results[result.get("episode_idd")] = result.get("progress")
        return results


    @classmethod
    def _make_id(cls, user_id, episode_id):
        return "%s--*--%s" % (user_id, episode_id)

    @classmethod
    def _episode_id_from_id(cls, id):
        return id.split("--*--")[1]


PlaybackProgress.register()

