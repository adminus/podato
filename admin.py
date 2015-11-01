from webapp.main import app

with app.app_context():
    from webapp.podcasts.crawler import update_podcasts
    from webapp import cache
    from webapp.db import get_connection, r

    import sys, code

    def list_cache_keys():
        p = sys.argv[2]
        print "Finding keys matching %s..." % p
        print cache.list_keys(p)

    def repl():
        get_connection().repl()
        code.InteractiveConsole(locals=globals()).interact()

    commands = {
        "update_podcasts": update_podcasts,
        "flush_cache": cache.flush,
        "list_cache_keys": list_cache_keys,
        "get_cache_key": cache.get,
        "db_repl": repl
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
