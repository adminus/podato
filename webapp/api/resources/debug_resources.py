
from flask_restplus import Resource

from webapp.api.oauth import AuthorizationRequired
from webapp.api.blueprint import api
from webapp.api.oauth import oauth

ns = api.namespace("debug_")

def dictify(d, seen=None, depth=0):
    seen = seen or []
    if depth > 6:
        return "maximum depth"
    seen.append(d)

    if isinstance(d, dict):
        for key in d:
            try:
                d[key] = dictify(d[key], seen, depth+1)
            except Exception as e:
                d[key] = "Got an exception trying to get this item; %s" % e
        return d
    if isinstance(d, (list, tuple)):
        d = list(d)
        for i in xrange(len(d)):
            d[i] = dictify(d[i], seen, depth+1)
        return d
    if isinstance(d, (basestring, int, float, bool, type(None),)):
        return d

    dd = dict(getattr(d, "__dict__", {}))
    for attr in dir(d):
        if attr.startswith("__"):
            continue
        try:
            dd[attr] = getattr(d, attr, "could not getattr.")
        except Exception as e:
            dd[attr] = "Exception while trying to get this attribute: %s" % e

    dd["@type"]=str(type(d))
    dd["@class"] = d.__class__.__name__ if hasattr(d, "__class__") else "unknown"

    try:
        dd["@str"] = str(d)
    except Exception as e:
        dd["@str"] = "Got an exception trying to str(): %s" % e
    try:
        dd["@repr"] = repr(d)
    except Exception as e:
        dd["@repr"] = "Got an exception trying to repr(): %s" % e
    res = dictify(dd, seen, depth+1)
    import json
    try:
        json.dumps(res)
        return res
    except:
        return str(res).encode("utf-8", "replace")


@ns.route("/test")
class Test(Resource):
    """This resource can be used for debugging auth issues."""
    @api.doc(id="test")
    def get(self):
        valid, req = oauth.verify_request([])
        if not req.client.get_app().trusted:
            raise AuthorizationRequired
        return dictify(req)

