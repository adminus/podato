"""The error store stores HTTP errors that occur when trying to fetch a podcast."""
from webapp import cache

ERROR_TTL = 3600

def store_error(url, code):
    """Store an error for a given url."""
    cache.set(url, code, expires=ERROR_TTL)

def get_error(url):
    """Check whether the given url returned an error code"""
    return cache.get(url)
