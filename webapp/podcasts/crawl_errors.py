from webapp.db import db

NO_TITLE = "E_NO_TITLE"
NO_DESCRIPTION = "E_NO_DESCRIPTION"
NO_AUTHOR = "E_NO_AUTHOR"
NO_OWNER = "E_NO_OWNER"
NO_IMAGE = "E_NO_IMAGE"
NO_DURATION = "E_NO_DURATION"
NO_ENCLOSURE = "E_NO_ENCLOSURE"
MALFORMED_DURATION = "E_MALFORMED_DURATION"
MALFORMED_ENCLOSURE_SIZE = "E_MALFORMED_ENCLOSURE_SIZE"
UNKNOWN_ERROR = "E_UNKNOWN"

# WARNINGS

NO_LANGUAGE = "W_NO_LANGUAGE"
NO_SUBTITLE = "W_NO_SUBTITLE"

#http errors
NOT_FOUND = "E_NOT_FOUND"
SERVER_ERROR = "E_SERVER_ERROR"
ACCESS_DENIED = "E_ACCESS_DENIED"
REDIRECT_LOOP = "E_REDIRECT_LOOP"
TIMEOUT = "E_TIMEOUT"



class CrawlError(db.EmbeddedDocument):
    error_type = db.StringField(choices=[
        NO_TITLE,
        NO_AUTHOR,
        NO_DESCRIPTION,
        NO_DURATION,
        NO_ENCLOSURE,
        NO_IMAGE,
        NO_OWNER,

        NOT_FOUND,
        SERVER_ERROR,
        ACCESS_DENIED,
        REDIRECT_LOOP,
        TIMEOUT
    ], default=UNKNOWN_ERROR)

    attrs = db.DictField()

    @classmethod
    def create(cls, attrs={}, **kwargs):
        return cls(attrs=attrs, **kwargs)