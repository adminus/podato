"""The error store stores HTTP errors that occur when trying to fetch a podcast."""
from webapp import cache

ERROR_TTL = 3600

def store_error(url, code):
    """Store an error for a given url. Url can also be a list of urls."""
    if isinstance(url, list):
        urls = url
        cache.set_multi({u: code for u in urls}, expires=ERROR_TTL)
        return
    cache.set(url, code, expires=ERROR_TTL)

def get_error(url):
    """Check whether the given url returned an error code"""
    return cache.get(url)
