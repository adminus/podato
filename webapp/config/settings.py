import json
import os
import logging

data = json.load(open(os.path.join(os.path.dirname(__file__), "settings.json")))

for key, value in data.iteritems():
    locals()[key] = value

DEBUG = bool(int(os.environ.get("DEBUG", 0)))
SECRET_KEY = os.environ["SECRET_KEY"]

SERVER_NAME = os.environ.get("HTTP_HOST", "localhost:"+os.environ["PORT"])

DEFAULT_PROTOCOL = "https"
if "localhost" in SERVER_NAME:
    DEFAULT_PROTOCOL = "http"

REDIS_URL = os.environ.get("REDISCLOUD_URL")
if REDIS_URL.endswith("/"):
    REDIS_URL += "0"
else:
    REDIS_URL += "/0"

MONGODB_HOST = os.environ.get("MONGOLAB_URI")

RETHINKDB_HOST = os.environ.get("RETHINKDB_HOST")
RETHINKDB_PORT = os.environ.get("RETHINKDB_PORT")
RETHINKDB_AUTH = os.environ.get("RETHINKDB_AUTH")
RETHINKDB_DB = os.environ.get("RETHINKDB_DB")

FACEBOOK_CONSUMER_KEY = os.environ["FACEBOOK_CONSUMER_KEY"]
FACEBOOK_CONSUMER_SECRET = os.environ["FACEBOOK_CONSUMER_SECRET"]
TWITTER_CONSUMER_KEY = os.environ["TWITTER_CONSUMER_KEY"]
TWITTER_CONSUMER_SECRET = os.environ["TWITTER_CONSUMER_SECRET"]
GOOGLE_CONSUMER_KEY = os.environ["GOOGLE_CONSUMER_KEY"]
GOOGLE_CONSUMER_SECRET = os.environ["GOOGLE_CONSUMER_SECRET"]
for client in TRUSTED_CLIENTS:
    key = client["NAME"].upper() + "_CLIENT_SECRET"
    locals()[key] = os.environ[key]