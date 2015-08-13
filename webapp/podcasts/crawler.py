import datetime
import time
import logging

import feedparser
from eventlet.green import urllib2
from flask import current_app

from webapp import utils
from webapp.podcasts.models import  Podcast, Episode, Person, Enclosure
from webapp.podcasts import crawl_errors
from webapp.async import app, group

from mongoengine.base import fields


PODATO_USER_AGENT = "Podato Crawler"

class FetchError(Exception):
    pass

class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_302(self, req, fp,
                                                                 code, msg,
                                                                 headers)
        result.status = code
        result.headers = headers
        return result

    http_error_301 = http_error_303 = http_error_307 = http_error_302

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

    return group(tasks).apply_async()


@app.task
def _fetch_podcast_data(url):
    utils.validate_url(url, allow_hash=False)
    try:
        request = urllib2.Request(url)
        opener = urllib2.build_opener(SmartRedirectHandler)
        request.add_header('User-Agent', current_app.config["USER_AGENT"])
        logging.info("fetching %s" % url)
        resp = opener.open(request)
        parsed = feedparser.parse(resp)
    except Exception as e:
        logging.exception("Exception raised trying to fetch %s" % url)
        return {"url": url,"errors": [crawl_errors.CrawlError.create(error_type=crawl_errors.UNKNOWN_ERROR, attrs={"error": str(e)})]}
    return _handle_feed(url, parsed, getattr(resp, "status", resp.getcode()))

def _handle_feed(url, parsed, code):
    """Handles the parsed result of a feed, putting it into a dict for storage."""
    previous_url = None
    logging.info("response_code: %s" % code)
    if code == 404:
        return {"url": url, "errors": [crawl_errors.CrawlError.create(error_type=crawl_errors.NOT_FOUND)]}
    if code == 401:
        return {"url": url, "errors": [crawl_errors.CrawlError.create(error_type=crawl_errors.ACCESS_DENIED)]}
    elif code == 410:
        return {"url": url, "errors": [crawl_errors.CrawlError.create(error_type=crawl_errors.GONE)]}
    elif code == 301: # Permanent redirect
        previous_url = url
    elif code == 304: # Not modified
        return {"url": url}
    elif code not in [200, 302, 303, 307]:
        return {"url": url, "errors": [crawl_errors.CrawlError.create(error_type=crawl_errors.UNKNOWN_ERROR, attrs={"code":code})]}

    try:
        errors = []
        episodes = []
        for entry in parsed.entries:
            episode, ep_errors = _make_episode(entry    )
            if ep_errors:
                errors += ep_errors
            if episode:
                episodes.append(episode)

        feed = parsed.feed
        publisher = _get_or_errors(feed, "author_detail", errors, crawl_errors.NO_OWNER) or {}
        d = {
            "url": parsed.href,
            "title": _get_or_errors(feed, "title", errors, crawl_errors.NO_TITLE),
            "author": _get_or_errors(feed, "author", errors, crawl_errors.NO_AUTHOR),
            "description": _get_or_errors(feed, "description", errors, crawl_errors.NO_DESCRIPTION),
            "language": _get_or_errors(feed, "language", errors, crawl_errors.NO_LANGUAGE),
            "copyright": parsed.feed.get("rights"),
            "image": _get_or_errors(feed, "image", errors, crawl_errors.NO_IMAGE, default={"href":None})["href"],
            "categories": [tag["term"] for tag in parsed.feed.get("tags", [{"term": ""}])],
            "owner": Person(name=publisher.get("name"),
                            email=publisher.get("email")),
            "last_fetched": datetime.datetime.now(),
            "complete": parsed.feed.get("itunes_complete") or False,
            "episodes": episodes,
            "errors": errors
        }
        if previous_url:
            d["previous_urls"] = [previous_url]
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
    podcast = Podcast(**podcast_data)
    podcast.save()
    return podcast

@app.task
def _subscribe_user(podcast, user):
    """Subscribe the given users to all the podcasts in the list."""
    return user.subscribe(podcast)

def _get_or_errors(d, key, errors, error_type, default=None, **error_props):
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