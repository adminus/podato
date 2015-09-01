from webapp.podcasts.crawler import update_podcasts
import sys

commands = {
    "update_podcasts": update_podcasts
}

subcommand = sys.argv[1]
if not subcommand in commands:
    print "No command named %s, supported commands: %s" % (subcommand, ", ".join(commands.keys()))
else:
    commands[subcommand]()
    print "done!"
