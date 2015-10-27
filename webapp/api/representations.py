"""
This module contains representations of data to be returned by the API. flask-restplus calls them models,
But that's confusing, because the name clashes with database models.
"""
from webapp.api.blueprint import api
from flask_restplus import fields

id_field = api.model("id", {
    "id": fields.String
})

success_status = api.model("success_status", {
    "success": fields.Boolean(required=False),
    "state": fields.String(required=False),
    "id": fields.String(required=False)
})

user_fields = api.extend("user", id_field, {
    "username": fields.String,
    "avatar_url": fields.String,
    "email_address": fields.String(attribute="primary_email"),
    "following": fields.List(fields.Nested(id_field))
})

subscribe_fields = api.model("subscribe", {
    "podcast": fields.String
})

podcast_fields = api.model("podcast_simple", {
    "id": fields.String(attribute="url"),
    "title": fields.String,
    "author": fields.String,
    "image": fields.String,
    "description": fields.String,
    "subscribers": fields.Integer
})

class Duration(fields.Raw):
    def format(self, value):
        seconds = value % 60
        value = value-seconds
        minutes = (value % 3600)/60
        value = value-minutes*60
        hours = value / 3600
        if hours == 0:
            return "%02d:%02d" % (minutes, seconds)
        return "%s:%02d:%02d" % (hours, minutes, seconds)


class Explicit(fields.Raw):
    def format(self, value):
        return ["undefined", "clean", "explicit"][value]

enclosure_fields = api.model("enclosure", {
        "type": fields.String,
        "url": fields.String
})

episode_fields = api.extend("episode", podcast_fields, {
    "subtitle": fields.String,
    "duration": Duration,
    "summary": fields.String,
    "explicit": Explicit,
    "summary": fields.String,
    "guid": fields.String,
    "published": fields.DateTime,
    "enclosure": fields.Nested(enclosure_fields)
})

podcast_full_fields = api.extend("podcast_full", podcast_fields, {
    "copyright": fields.String,
    "language": fields.String,
    "complete": fields.Boolean,
    "episodes": fields.List(fields.Nested(episode_fields)),
    "previous_urls": fields.List(fields.String),
    "last_fetched": fields.DateTime
})

subscribe_result_fields = api.extend("subscribe_result", id_field, {
    "success": fields.Boolean,
    "total": fields.Integer,
    "progress": fields.Integer
})