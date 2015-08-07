from webapp.db import Model, ValidationError

NO_TITLE = "E_NO_TITLE"
NO_DESCRIPTION = "E_NO_DESCRIPTION"
NO_AUTHOR = "E_NO_AUTHOR"
NO_OWNER = "E_NO_OWNER"
NO_IMAGE = "E_NO_IMAGE"
NO_DURATION = "E_NO_DURATION"
NO_ENCLOSURE = "E_NO_ENCLOSURE"
MALFORMED_DURATION = "E_MALFORMED_DURATION"
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



class CrawlError(Model):

    def __init__(self, error_type=UNKNOWN_ERROR, attrs=None):
        self.error_type = error_type
        self.attrs = attrs or {}

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    @classmethod
    def create(cls, attrs={}, **kwargs):
        instance = cls(attrs=attrs, **kwargs)
        instance.validate()
        return instance

    def validate(self):
        if self.error_type not in [NO_TITLE, NO_DESCRIPTION, NO_AUTHOR, NO_OWNER,
                                   NO_IMAGE, NO_DURATION, NO_ENCLOSURE,
                                   MALFORMED_DURATION, UNKNOWN_ERROR, NO_LANGUAGE,
                                   NO_SUBTITLE, NOT_FOUND, SERVER_ERROR, ACCESS_DENIED,
                                   REDIRECT_LOOP, TIMEOUT]
            raise ValidationError("unknown error_type %s" % self.error_type)