from simplexml import dumps
from flask import make_response
import xml.etree.cElementTree as ET


class U:
    # Function is needed to make dictionary hashable/comparable
    # ie when using set() function
    @staticmethod
    def frozendict(d: dict):
        return frozenset(d.keys()), frozenset(d.values())

    @staticmethod
    def xmlify(data, code=200, headers=None):
        if isinstance(data, type(ET.Element(None))):
            xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'
            xml_data = ET.tostring(data, encoding='utf-8', method="xml").decode('utf-8')
            resp = make_response(xml_declaration + xml_data, code)
            resp.headers.extend(headers or {})
            resp.mimetype = "application/xml"
            return resp
        else:
            resp = make_response(dumps(data), code)
            resp.headers.extend(headers or {})
            resp.mimetype = "application/xml"
            return resp
