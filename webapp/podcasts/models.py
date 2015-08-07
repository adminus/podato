from webapp.db import Model, r


from crawl_errors import CrawlError

class Person(Model):
    """Model that represents a person within a podcast feed."""

    attributes = ["name", "email"]

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


class Enclosure(Model):
    """Model that represents an enclosure (an episode's file.)"""

    attributes = ["url", "type"]

    def __init__(self, url=None, type=None):
        self.url = url
        self.type = type

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


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

    @classmethod
    def from_dict(cls, d):
        d["enclosure"] = Enclosure.from_dict(d["enclosure"])
        return cls(**d)


class Podcast(Model):
    """Model that represents a podcast."""
    url = db.URLField(required=True, unique=True)
    title = db.StringField(required=True)
    author = db.StringField(required=True)
    description = db.StringField()
    language = db.StringField()
    copyright = db.StringField()
    image = db.StringField()
    categories = db.ListField(db.StringField())
    owner = db.EmbeddedDocumentField(Person)
    last_fetched = db.DateTimeField()
    previous_urls = db.ListField(db.StringField(), default=[])
    complete = db.BooleanField()
    episodes = db.EmbeddedDocumentListField(Episode)
    subscribers = db.IntField(default=0)
    errors = db.ListField(db.EmbeddedDocumentField(CrawlError), default=[])

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
    def from_dict(cls, d):
        if "owner" in d:
            d["owner"] = Person.from_dict(d["owner"])
        if "episodes" in d
            d["episodes"] = [Episode.from_dict(d2) for d2 in d["episodes"]]
        if "errors" in d
            d["errors"] = [CrawlError.from_dict(d2) for d2 in d["errors"]]

        return cls(**d)

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