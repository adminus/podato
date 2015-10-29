import cache
import datetime


def test_cache_set(mock_cache):
    redis, clock = mock_cache
    cache.set("foo", "bar")
    assert cache.get("foo") == "bar"


def test_cache_get(mock_cache):
    redis, clock = mock_cache
    cache.set("foo", "bar")
    assert cache.get("foo") == "bar"


def test_cache_set_expire(mock_cache):
    redis, clock = mock_cache
    cache.set("foo", "bar", expires=60)
    assert cache.get("foo") == "bar"
    clock.set_time(datetime.datetime.now() + datetime.timedelta(seconds=61))
    redis.do_expire()
    assert cache.get("foo") == None


def test_set_multi(mock_cache):
    redis, clock = mock_cache
    cache.set_multi({"foo1": "bar1", "foo2": "bar2"})
    assert cache.get("foo1") == "bar1"
    assert cache.get("foo2") == "bar2"


def test_set_multi_prefix(mock_cache):
    redis, clock = mock_cache
    cache.set_multi({"foo1": "bar1", "foo2": "bar2"}, key_prefix="test_")
    assert cache.get("test_foo1") == "bar1"
    assert cache.get("test_foo2") == "bar2"
    assert cache.get("foo1") == None


def test_set_multi_expires(mock_cache):
    redis, clock = mock_cache
    cache.set_multi({"foo1": "bar1", "foo2": "bar2"}, expires=60)
    assert cache.get("foo1") == "bar1"
    assert cache.get("foo2") == "bar2"
    clock.set_time(datetime.datetime.now() + datetime.timedelta(seconds=61))
    redis.do_expire()
    assert cache.get("foo1") == None
    assert cache.get("foo2") == None


def test_get_multi(mock_cache):
    redis, clock = mock_cache
    cache.set("foo1", "bar1")
    cache.set("foo2", "bar2")
    assert cache.get_multi(["foo1", "foo2"]) == {"foo1": "bar1", "foo2": "bar2"}


def test_get_multi_prefix(mock_cache):
    redis, clock = mock_cache
    cache.set("test-foo1", "bar1")
    cache.set("test-foo2", "bar2")
    assert cache.get_multi(["foo1", "foo2"], key_prefix="test-") == {"foo1": "bar1", "foo2": "bar2"}


def test_cached_function_is_cached(mock_cache):
    called = [0]
    @cache.cached_function(expires=0    )
    def test_function(a, b, c=3, d=4):
        called[0] += 1
        return "%s%s%s%s" % (a, b, c, d)

    res1 = test_function(1, 2, 3)
    res2 = test_function(1, 2, 3)

    assert res1 == "1234"
    assert res1 == res2
    assert called[0] == 1


def test_cached_function_returning_none_is_cached(mock_cache):
    called = [0]
    @cache.cached_function(expires=0)
    def test_function(a, b, c=3, d=4):
        called[0] += 1
        return None

    assert test_function(1, 2, 3) is None
    assert test_function(1, 2, 3) is None
    assert called[0] == 1


def test_cached_function_with_different_args(mock_cache):
    called = [0]
    @cache.cached_function(expires=0)
    def test_function(a, b, c=3, d=4):
        called[0] += 1
        return "%s%s%s%s" % (a, b, c, d)

    assert test_function(1, 2) == "1234"
    assert test_function(1, 2, 3) == "1234"
    assert test_function(1, b=2, c=3) == "1234"
    assert test_function(1, 2, c="c", d={}) == "12c{}"
    assert called[0] == 4


def test_cached_function_with_force(mock_cache):
    called = [0]
    @cache.cached_function(expires=0    )
    def test_function(a, b, c=3, d=4):
        called[0] += 1
        return "%s%s%s%s" % (a, b, c, d)

    res1 = test_function(1, 2, 3)
    res2 = test_function(1, 2, 3)
    res3 = test_function(1, 2, 3, force=True)

    assert res1 == "1234"
    assert res1 == res2
    assert res3 == res2
    assert called[0] == 2