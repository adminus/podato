import datetime
import time
import logging

import feedparser
from eventlet import import_patched
from flask import current_app
httplib2 = import_patched("httplib2")

from webapp import utils
from webapp.podcasts.models import  Podcast, Episode, Person, Enclosure
from webapp.podcasts import crawl_errors
from webapp.podcasts import error_store
from webapp.async import app, group


PODATO_USER_AGENT = "Podato Crawler"

class FetchError(Exception):
    pass


def fetch(url_or_urls, subscribe=None):
    """This fetches a (list of) podcast(s) and stores it in the db. It assumes that it only gets called
    by Podcast.get_by_url, or some other method that knows whether a given podcast has
    already been fetched.

    If *subscribe* is given, it should be a User instance to be subscribed to the given podcasts."""
    if isinstance(url_or_urls, basestring):
        url_or_urls = [url_or_urls]

    tasks = []
    for url in url_or_urls:
        store = _store_podcast.s()
        task = _fetch_podcast_data.s(url)
        if subscribe:
            store.link(_subscribe_user.s(subscribe))
        task.link(store)
        tasks.append(task)

    result = group(tasks).apply_async()
    result.save()
    return result

def update_podcasts():
    _update_podcasts.apply_async()


@app.task
def _update_podcasts()
    to_update = Podcast.get_update_needed()@
    for podcast in to_update:
        _update_podcast.apply_async(url=podcast.url)


@app.task
def _update_podcast(url):
    data = _fetch_podcast_data(url)
    if not data:
        return
    if data["url"] != url:
        _handle_moved_podcast(url, data)
        return
    _make_updates(url, data)


def _handle_moved_podcast(previous_url, data):
    Podcast.delete_by_url(url)
    _store_podcast(data)


def _make_updates(url, data):
    podcast = Podcast.get_by_url(url)
    data["previous_urls"] = list(set(podcast.previous_urls()).union(data["previous_urls"]))
    podcast.update(data)


http = httplib2.Http()
http.force_exception_to_status_code = True


@app.task
def _fetch_podcast_data(url):
    utils.validate_url(url, allow_hash=False)
    try:
        error_code = error_store.get_error(url):
        if error_code:
            logging.info("Won't fetch %s, since we got a %s response recently." % (url, error_code))
            return

        headers = {"User-Agent": current_app.config["USER_AGENT"]}
        logging.info("fetching %s" % url)
        resp, body = http.request(url, headers=headers)

        if resp.status != 200:
            logging.info("Received an error (%s) when trying to fetch %s" % (url, resp.status))
            _handle_error_response(resp)
            return
        parsed = feedparser.parse(body)
    except Exception as e:
        logging.exception("Exception raised trying to fetch %s" % url)
        return
    return _handle_feed(parsed, resp)


def _handle_error_response(response):
    if response.previous:
        status = response.status
        urls = []
        while response is not None:
            urls.append(response["content-location"])
            response = response.previous
        error_store.store_error(urls, status)
    else:
        error_store.store_error(response["content-location"], response.status)


def _handle_feed(parsed, http_response):
    """Handles the parsed result of a feed, putting it into a dict for storage."""

    try:
        errors = []
        episodes = []
        for entry in parsed.entries:
            episode, ep_errors = _make_episode(entry    )
            if ep_errors:
                errors += ep_errors
            if episode:
                episodes.append(episode)

        url = http_response["content-location"]
        previous_urls = []
        r = http_response
        while r.previous is not None:
            previous_urls.append(r.previous["content-location"])
            r = r.previous

        feed = parsed.feed
        publisher = _get_or_errors(feed, "author_detail", errors, crawl_errors.NO_OWNER) or {}
        d = {
            "url": url,
            "title": _get_or_errors(feed, "title", errors, crawl_errors.NO_TITLE),
            "author": _get_or_errors(feed, "author", errors, crawl_errors.NO_AUTHOR),
            "description": _get_or_errors(feed, "description", errors, crawl_errors.NO_DESCRIPTION),
            "language": _get_or_errors(feed, "language", errors, crawl_errors.NO_LANGUAGE),
            "copyright": parsed.feed.get("rights"),
            "image": _get_or_errors(feed, "image", errors, crawl_errors.NO_IMAGE, default={"href":None})["href"],
            "categories": list(set([tag["term"] for tag in parsed.feed.get("tags", [{"term": ""}])])),
            "owner": Person(name=publisher.get("name"),
                            email=publisher.get("email")),
            "last_fetched": datetime.datetime.now(),
            "complete": parsed.feed.get("itunes_complete") or False,
            "episodes": episodes,
            "errors": errors,
            "previous_urls": previous_urls
        }
        return d
    except Exception as e:
        logging.exception("Encountered an exception while parsing %s" % (parsed.href))
        raise


def _make_episode(entry):
    """Crate an Episode object from the given feedparser item."""
    errors = []
    if not entry.get('enclosures'):
         return None, [crawl_errors.CrawlError.create(error_type=crawl_errors.NO_ENCLOSURE, attrs={"episode": entry.get("id")})]
    try:
        episode = Episode(
            title=_get_or_errors(entry, "title", errors, crawl_errors.NO_TITLE, episode=entry.get("id")),
            subtitle=_get_or_errors(entry, "subtitle", errors, crawl_errors.NO_SUBTITLE, episode=entry.get("id")),
            description=_get_episode_description(entry),
            author=_get_or_errors(entry, "author", errors, crawl_errors.NO_AUTHOR, episode=entry.get("id")),
            guid=entry.guid,
            published=datetime.datetime.fromtimestamp(
                time.mktime(entry.published_parsed
            )),
            image=entry.get("image", {}).get("href"),  #The use of .get ensures no errors are raised when there's no episode image.
            duration=_parse_duration(entry, errors),
            explicit=_parse_explicit(entry),
            enclosure=Enclosure(type=entry.enclosures[0].get("type"),
                              url=entry.enclosures[0].href
            )
        )
        return episode, errors
    except Exception as e:
        logging.exception("Got an exception while parsing episode: %s." % entry.get("id"))
        return None, [crawl_errors.CrawlError.create(error_type=crawl_errors.UNKNOWN_ERROR, attrs={"episode": entry.get("id")})]


def _get_episode_description(entry):
    """Pull an episode's description (show notes) from the episode."""
    for content in entry.get('content', []):
        if "html" in content.type:
            return content.value

    return max(entry.get("description", ""), entry.get("summary", ""), key=len)


def _parse_duration(entry, errors):
    """Parse an episode's duration into an integer representing the number of seconds."""
    try:
        parts = _get_or_errors(entry, "itunes_duration", errors, crawl_errors.NO_DURATION, default="0").split(":")
        d = 0
        for i in xrange(min(len(parts), 3)):
            if parts[-(i+1)].strip():
                d += int(float(parts[-(i+1)])) * 60**i
            else:
                break
    except ValueError:
        logging.exception("Encountered an error while parsing duration %s, %s" % (entry.itunes_duration, entry.get("id")))
        errors.append(crawl_errors.CrawlError.create(error_type=crawl_errors.MALFORMED_DURATION, attrs={"episode": entry.get("id"), "duration":entry.itunes_duration}))
        return 0
    return d

def _parse_explicit(entry):
    """Parse the itunes:explicit tag of an episode."""
    exp = entry.get("itunes_explicit")
    if exp == "yes":
        return 1
    elif exp == "clean":
        return 2
    else:
        return 0

@app.task
def _store_podcast(podcast_data):
    """Given a list of dictionaries representing podcasts, store them all in the database."""
    if not podcast_data:
        return
    podcast = Podcast(**podcast_data)
    podcast.save()
    return podcast

@app.task
def _subscribe_user(podcast, user):
    """Subscribe the given users to all the podcasts in the list."""
    if podcast:
        return user.subscribe(podcast)

def _get_or_errors(d, key, errors, error_type, default=None, **error_props):
    """Gets the value at the given key from dictionary 'd' if it is present, otherwise
    appends an error to 'errors', with the given value

    arguments:
      - d: the dictionary to access
      - key: the key to get
      - errors: a lis of errors to append to
      - error_type: the error type to append when the key is not present
      - tdefault: the default value to return when there's no value for the given key.
        An error will still be appended if the default value is returned.
      - **error_props: properties to be stored with the error.
    """
    error = crawl_errors.CrawlError.create(error_type=error_type, attrs=error_props)
    try:
        not_found = "COULD+NOT+ACCESS"
        val = d.get(key, not_found)
        if val == not_found:
            errors.append(error)
            return default
    except:
        errors.append(error)
        logging.exception("Got an exception trying to get %s" % key)
        return default
    return val