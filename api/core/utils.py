from simplexml import dumps
from flask import make_response


class U:
    # Function is needed to make dictionary hashable/comparable
    # ie when using set() function
    @staticmethod
    def frozendict(d: dict):
        return frozenset(d.keys()), frozenset(d.values())

    @staticmethod
    def xmlify(data, code=200, headers=None):
        resp = make_response(dumps({'response': data}), code)
        resp.headers.extend(headers or {})
        resp.mimetype = "application/xml"
        return resp
