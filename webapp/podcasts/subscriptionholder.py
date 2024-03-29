import logging

from webapp.db import r
from webapp.podcasts.models import Podcast
from webapp.podcasts import crawler
from webapp.async import GroupResult

class SubscribeResult(object):

    def __init__(self, id=None, success=None, progress=None, total=None):
        self.id = id
        self.success = success
        self.progress = progress
        self.total = total

    @classmethod
    def get(cls, id):
        """Get a SubscribeResult by its id."""
        r = GroupResult.restore(id=id)
        if not r:
            return None
        instance = cls(id=id, progress=r.completed_count(), total=len(r.results))
        if r.successful():
            instance.success = True
        if r.failed():
            instance.success = False
        return instance

    def __repr__(self):
        return "<SubscribeResult id=%s, success=%s, progress=%s, total=%s>" % (
            self.id, self.success, self.progress, self.total
        )

    def __str__(self):
        return repr(self)


class SubscriptionHolder(object):
    """A mixin to be applied to the User model, which represents the user's subscriptions."""

    attributes = ["subscriptions"]

    def subscribe(self, podcast):
        """Subscribe the user to the given podcast."""
        if podcast.url in self.subscriptions:
            return SubscribeResult(success=False)
        self.run(self.table.get(self.id).update({
            "subscriptions": r.row["subscriptions"].append(podcast.url)
        }))
        Podcast.run(Podcast.get_table().get(podcast.url).update({
            "subscribers": (r.row["subscribers"].default(0) + 1)
        }))
        return SubscribeResult(success=True)

    def subscribe_by_url(self, url):
        """Subscribe the user to the podcast at the given feed url."""
        podcast = Podcast.get_by_url(url)
        if podcast == None:
            id = crawler.fetch(url, subscribe=self).id
            SubscribeResult(id=id)
        return SubscribeResult(success=self.subscribe(podcast))

    def unsubscribe(self, podcast):
        """Unsubscribe the user from the podcast."""
        if podcast.url in self.subscriptions:
            self.run(self.table.get(self.id).update(
                {"subscriptions": r.row["subscriptions"].set_difference([podcast.url])}
            ))
            Podcast.run(Podcast.get_table().get(podcast.url).update({
                "subscribers": (r.row["subscribers"].default(0) - 1)
            }))
            return True
        return False

    def unsubscribe_by_url(self, url):
        """Unsubscribe the user from the podcast at the given feed url."""
        podcast = Podcast.get_by_url(url)
        if not podcast:
            return SubscribeResult(success=False)
        return SubscribeResult(success=self.unsubscribe(podcast))

    def subscribe_multi(self, podcasts):
        """Subscribe the user to multiple podcasts. podcasts should be an iterable of Podcast objects."""
        not_already_subscribed = []
        for podcast in podcasts:
            if podcast.url not in self.subscriptions:
                not_already_subscribed.append(podcast.url)

        self.run(self.table.get(self.id).update(
            {"subscriptions": r.row["subscriptions"].set_union(not_already_subscribed)}
        ))
        Podcast.run(Podcast.get_table().get_all(r.args(not_already_subscribed)).update({
            "subscribers": (r.row["subscribers"].default(0) + 1)
        }))
        return SubscribeResult(success=True)

    def subscribe_multi_by_url(self, urls):
        """Subscribe the user to all the podcasts at the given feed urls. urls should be an iterable of strings."""
        podcasts = Podcast.get_multi_by_url(urls)
        already_fetched = []
        to_fetch = []
        for url in urls:
            if url in podcasts:
                already_fetched.append(podcasts[url])
            else:
                to_fetch.append(url)

        if already_fetched:
            self.subscribe_multi(already_fetched)

        res = None
        success = None
        if to_fetch:
            id = crawler.fetch(to_fetch, subscribe=self).id
            return SubscribeResult(id=id)
        else:
            return SubscribeResult(success=True)

    def get_subscriptions(self):
        """Get the Podcast objects of podcasts the user has subscribed to."""
        if len(self.subscriptions) == 0:
            return []
        res = self.run(Podcast.get_table().get_all(r.args(self.subscriptions)))
        return [Podcast.from_dict(p) for p in res]