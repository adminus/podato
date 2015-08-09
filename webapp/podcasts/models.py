from webapp.db import Model, r


from crawl_errors import CrawlError

class Person(Model):
    """Model that represents a person within a podcast feed."""

    attributes = ["name", "email"]

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email


class Enclosure(Model):
    """Model that represents an enclosure (an episode's file.)"""

    attributes = ["url", "type"]

    def __init__(self, url=None, type=None):
        self.url = url
        self.type = type


class Episode(Model):
    """Model that represents a podcast episode."""

    attributes = ["title", "subtitle", "description", "author", "guid",
                  "published", "image", "duration", "explicit", "enclosure"]

    def __init__(self, title, guid, enclosure, subtitle=None, description=None, author=None, published=None, image=None, duration=None, explicit=None):
        self.title = title
        self.guid = guid
        self.enclosure = enclosure
        self.subtitle=subtitle
        self.description = description
        self.author = author
        self.published = published,
        self.image = image
        self.duration = duration
        self.explicit = explicit


class Podcast(Model):
    """Model that represents a podcast."""

    attributes = ["url", "title", "author", "description", "language", "copyright",
                  "image", "categories", "owner", "last_fetched", "previous_urls",
                  "episodes", "subscribers", "errors"]

    def __init__(self, url, title=None, author=None, description=None, language=None,
                 copyright=None, image=None, categories=None, owner=None,
                 last_fetched=None, previous_urls=None, episodes=None,
                 subscribers=None, errors=None):

        self.url = url
        self.title = title
        self.author = author
        self.description = description
        self.language = language
        self.copyright = copyright
        self.image = image
        self.categories = categories or []
        self.owner = owner
        self.last_fetched = last_fetched
        self.previous_urls = previous_urls or []
        self.episodes = episodes or []
        self.subscribers = subscribers
        self.errors = errors

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
    def get_multi_by_url(cls, urls=[]):
        """Given a list of urls, returns a dictionary mapping from url to podcast."""
        urls = set(urls)
        d = {}

        podcasts = cls.run(cls.get_table().get_all(r.args(urls)))

        for pod in podcasts:
            urls.remove(pod.url)
            d[pod.url] = cls.from_dict(pod)

        moved_podcasts = cls.run(cls.get_table().filter(
            lambda pod: pod["previous_urls"].set_intersection(urls).count() > 0
        ))

        for pod in moved_podcasts:
            for key in urls.intersection(pod["previous_urls"]):
                d[key] = cls.from_dict(pod)

        return d