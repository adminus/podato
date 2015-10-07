from webapp.podcasts.crawler import update_podcasts
from webapp.app import app
from webapp import cache
import sys

def list_cache_keys():
    p = sys.argv[2]
    print "Finding keys matching %s..." % p
    print cache.list_keys(p)

commands = {
    "update_podcasts": update_podcasts,
    "flush_cache": cache.flush,
    "list_cache_keys": list_cache_keys,
    "get_cache_key": cache.get
}

subcommand = sys.argv[1]
if not subcommand in commands:
    print "No command named %s, supported commands: %s" % (subcommand, ", ".join(commands.keys()))
else:
    command = commands[subcommand]
    args = sys.argv[2:]
    arity = command.func_code.co_argcount
    args = args[:arity]
    value = command(*args)
    print "returned %s: %s" % (type(value), value)
    print "done!"
