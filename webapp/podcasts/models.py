from webapp.db import Model, r


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
                                   p.last_fetched.during(r.now(), r.now() - 1800)
            ).pluck("url")
        )]

    def update(self, data):
        data = self.prepare_value(data)
        return self.run(
            self.table.get(self.url).update(data)
        )

    @classmethod
    def get_by_url(cls, url):
        """Get a podcast by its feed url. If the podcast has moved, the podcast at its new url will be returned."""
        p = cls.get(url)
        if not p:
            p = cls.run(cls.get_table().filter(
                lambda podcast: podcast["previous_urls"].contains(url)
            ))[0]

        if p:
            return cls.from_dict(p)

    @classmethod
    def delete_by_url(cls):
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
    def query(cls, order=None, category=None, author=None, language=None, page=1, per_page=30):

        query = cls.get_table()
        if order:
            query = query.order_by(order)
        if category:
            query = query.filter(lambda p:p["categories"].contains(category))
        if author:
            query = query.filter({"author": author})
        if language:
            query = query.filter({"language":language})
        query.skip((page-1)*per_page)
        query.limit(per_page)

        return [cls.from_dict(p) for p in cls.run(query)]


Person.register()
Podcast.register()
Episode.register()
Enclosure.register()