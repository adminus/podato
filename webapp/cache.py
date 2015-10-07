import cPickle

from flask.ext.redis import Redis

redis = Redis()

def _add_key_prefix(collection, prefix):
    if isinstance(collection, dict):
        return {prefix + key: value for key, value in collection.iteritems()}
    elif isinstance(collection, list):
        return [prefix + key for key in collection]
    else:
        raise ValueError("Expected dictionary or list, got %s" % type(collection))


def init_cache(app):
    redis.init_app(app)


def set(name, value, expires=0):
    """Sets the value for the given key. If expires is not 0, the value will be removed after the given number of seconds."""
    value = _serialize(value)
    if expires == 0:
        return redis.set(name, value)
    return redis.setex(name, value, expires)

def set_multi(pairs, expires=0, key_prefix=""):
    """Sets multiple keys at once. key_prefix is added to every key."""
    serialized = {}
    for key, value in pairs.iteritems():
        serialized[key] = _serialize(value)
    if key_prefix:
        pairs = _add_key_prefix(serialized, key_prefix)
    if expires == 0:
        return redis.mset(serialized)
    p = redis.pipeline()
    p.mset(serialized)
    for name in serialized.keys():
        p.expire(name, expires)
    r = p.execute()
    return r

def get(key):
    """Get the value associated with the given key."""
    return _deserialize(redis.get(key))

def get_multi(keys, key_prefix=""):
    """Returns all values associated with the given keys.
    Returns a dictionary mapping keys to values.
    key_prefix is not included in the dictionary keys."""
    original_keys = keys
    if key_prefix:
        keys = _add_key_prefix(keys, key_prefix)

    values = redis.mget(keys)
    return {original_keys[i]: _deserialize(values[i]) for i in xrange(len(keys))}


def flush():
    redis.flushdb()


def list_keys(pattern):
    return redis.keys(pattern)


def _deserialize(v):
    if not isinstance(v, basestring):
        return v
    return cPickle.loads(v)


def _serialize(v):
    return cPickle.dumps(v)