from webapp.podcasts.crawler import update_podcasts
from webapp.app import app
from webapp import cache
import sys

def list_cache_keys():
    p = sys.argv[2]
    print cache.list_keys(p)

commands = {
    "update_podcasts": update_podcasts,
    "flush_cache": cache.flush,
    "list_cache_keys": list_cache_keys
}

subcommand = sys.argv[1]
if not subcommand in commands:
    print "No command named %s, supported commands: %s" % (subcommand, ", ".join(commands.keys()))
else:
    commands[subcommand]()
    print "done!"
