import logging

from webapp import cache
from webapp.db import Model, r
from webapp.podcasts import error_store
from crawl_errors import CrawlError

class Person(Model):
    """Model that represents a person within a podcast feed."""

    attributes = ["name", "email"]


class Enclosure(Model):
    """Model that represents an enclosure (an episode's file.)"""

    attributes = ["url", "type"]


class Episode(Model):
    """Model that represents a podcast episode."""

    attributes = ["title", "subtitle", "description", "author", "guid",
                  "published", "image", "duration", "explicit", "enclosure"]


class Podcast(Model):
    """Model that represents a podcast."""

    attributes = ["url", "title", "author", "description", "language", "copyright",
                  "image", "categories", "owner", "last_fetched", "previous_urls",
                  "episodes", "subscribers", "errors", "complete"]

    @classmethod
    def get_update_needed(cls):
        """Returns an iterable of podcasts that need to be updated. It is only
        guaranteed to return the 'url' property for each podcast."""
        return [cls.from_dict(p) for p in cls.run(
            cls.get_table().filter(lambda p:
                                   p["last_fetched"] < (r.now() - 1800)
            ).pluck("url", "__type")
        )]

    def update(self, data):
        data = self.prepare_value(data)
        return self.run(
            self.table.get(self.url).update(data)
        )

    @classmethod
    def get_or_fetch(cls, url):
        """Get a podcast by its feed url. If it's not in the db, fetch it."""
        p = cls.get_by_url(url)
        if not p:
            logging.debug("Not in the database, need to fetch.")
            code = error_store.get_error(url)
            if code:
                logging.debug("Refusing to fetch, because we've encountered an error recently: %s" % code)
                return None

            # Doing this import inside a function to avoid circular import.
            from webapp.podcasts import crawler
            results = list(crawler.fetch(url).results[0].collect())
            logging.debug("Fetched, got %s." % results)
            p = cls.get_by_url(url)
        return p

    @classmethod
    def get_by_url(cls, url):
        """Get a podcast by its feed url. If the podcast has moved, the podcast at its new url will be returned."""
        logging.debug("Retrieving podcast: %s" % url)
        p = cls.get(url)
        if p:
            logging.debug("found it.")
            return p
        logging.debug("Checking if it might have moved.")
        res = list(cls.run(cls.get_table().get_all(url, index="previous_urls")))

        if res:
            logging.debug("found it.")
            return cls.from_dict(res[0])
        return None



    @classmethod
    def delete_by_url(cls, url):
        """Delete the podcast at the given url."""
        return cls.run(
            cls.get_table().get(url).delete()
        )

    @classmethod
    def get_multi_by_url(cls, urls=[]):
        """Given a list of urls, returns a dictionary mapping from url to podcast."""
        urls = set(urls)
        d = {}

        podcasts = [cls.from_dict(p) for p in cls.run(cls.get_table().get_all(r.args(urls)))]

        for pod in podcasts:
            urls.remove(pod.url)
            d[pod.url] = pod

        moved_podcasts = cls.run(cls.get_table().filter(
            lambda pod: pod["previous_urls"].set_intersection(urls).count() > 0
        ))

        for pod in moved_podcasts:
            for key in urls.intersection(pod["previous_urls"]):
                d[key] = cls.from_dict(pod)

        return d

    @classmethod
    def query(cls, order=None, category=None, author=None, language=None, page=1, per_page=30, fields=None  ):
        if page < 3:
            cached = cls._query_cached(order=order, category=category, author=author, language=language, page=page, per_page=per_page)
            if cached:
                return cached

        query = cls.get_table()
        if order:
            indexed = ["subscribers", "author"]
            if order in indexed:
                query = query.order_by(index=order)
            else:
                query = query.order_by(order)
        if category:
            query = query.filter(lambda p:p["categories"].contains(category))
        if author:
            query = query.filter({"author": author})
        if language:
            query = query.filter({"language":language})

        if page < 1:
            page = 1
        per_page = max(1, min(per_page, 30))
        query = query.skip((page-1)*per_page)
        query = query.limit(per_page)
        fields = fields or ["url", "title", "author", "image", "description", "categories"]
        query = query.pluck("__type", *fields)

        results = [cls.from_dict(p) for p in cls.run(query)]
        cls._cache_query(results, order, category, author, language, page, per_page)
        return results

    @classmethod
    def _query_cached(cls, order=None, category=None, author=None, language=None, page=1, per_page=30):
        key = cls._make_query_key(order, category, author, language, page, per_page)
        return cache.get(key)

    @classmethod
    def _cache_query(cls, results, *args):
        key = cls._make_query_key(*args)
        return cache.set(key, results)

    @classmethod
    def _make_query_key(self, *args):
        return "|".join([str(a) for a in args])

    def ensure_episode_images(self):
        for episode in self.episodes:
            if not episode.image:
                episode.image = self.image


Person.register()
Podcast.register()
Episode.register()
Enclosure.register()