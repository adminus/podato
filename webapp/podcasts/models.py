from webapp.db import db, Model

from mongoengine import Q

from crawl_errors import CrawlError

class Person(db.EmbeddedDocument):
    """Model that represents a person within a podcast feed."""
    name = db.StringField()
    email = db.EmailField()


class Enclosure(db.EmbeddedDocument):
    """Model that represents an enclosure (an episode's file.)"""
    url = db.URLField()
    length = db.IntField()
    type = db.StringField()


class Episode(db.EmbeddedDocument):
    """Model that represents a podcast episode."""
    title = db.StringField(required=True)
    subtitle = db.StringField()
    description = db.StringField()
    author = db.StringField()
    guid = db.StringField(required=True)
    published = db.DateTimeField(required=True)
    image = db.URLField()
    duration = db.IntField()
    explicit = db.IntField()
    enclosure = db.EmbeddedDocumentField(Enclosure, required=True)



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
    errors = db.EmbeddedDocumentListField(CrawlError, default=[])

    @classmethod
    def get_by_url(cls, url):
        """Get a podcast by its feed url. If the podcast has moved, the podcast at its new url will be returned."""
        return cls.objects(db.Q(url=url) | db.Q(previous_urls=url)).first()

    @classmethod
    def get_multi_by_url(cls, urls):
        """Given a list of urls, returns a dictionary mapping from url to podcast."""
        podcasts = cls.objects(db.Q(url__in=urls) | db.Q(previous_urls__in=urls))
        return {cls._pick_key(podcast, urls) : podcast for podcast in podcasts}

    @classmethod
    def _pick_key(cls, podcast, urls):
        """Helper method for get_multi_by_url that determines which key to use for a given podcast in the returned dictionary."""
        if podcast.url in urls:
            return podcast.url
        else:
            for url in podcast.previous_urls:
                if url in urls:
                    return url