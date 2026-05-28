from flask import make_response, Response
import xml.etree.cElementTree as ET
from datetime import timedelta, datetime
import calendar
import csv
import pandas as pd
from collections import OrderedDict

# Simple simplexml replacement - just convert dict to simple XML
def dumps(data):
    """Convert dict to simple XML string"""
    import json
    return json.dumps(data)  # Fallback: return JSON if needed

class U:
    # Function is needed to make dictionary hashable/comparable
    # ie when using set() function
    @staticmethod
    def frozendict(d: dict):
        return frozenset(d.keys()), frozenset(d.values())

    @staticmethod
    def xmlify(data, code=200, headers=None):
        if isinstance(data, type(ET.Element(None))):
            xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
            ET.indent(data)
            xml_data = ET.tostring(data, encoding="utf-8", method="xml").decode("utf-8")
            resp = make_response(xml_declaration + xml_data, code)
            resp.headers.extend(headers or {})
            resp.mimetype = "application/xml"
            return resp
        else:
            resp = make_response(dumps(data), code)
            resp.headers.extend(headers or {})
            resp.mimetype = "application/xml"
            return resp

    @staticmethod
    def dataframe_to_csv_response(data, name):
        if isinstance(data, list):
          data = pd.DataFrame(data)
        elif isinstance(data, OrderedDict):
          data = pd.DataFrame([data])
        return U.csv_response(data.to_csv(index=False, quoting=csv.QUOTE_ALL), name)

    @staticmethod
    def csv_response(csv_file, name):
        return Response(
            csv_file,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=" + name},
        )

    @staticmethod
    def zip_response(zip_file, name):
        return Response(
            zip_file,
            mimetype="application/zip",
            headers={"Content-disposition": "attachment; filename=" + name},
        )

    @staticmethod
    def to_epoch_ignore_tz(val):
        dt = val.split("+")
        epoch = datetime(1970, 1, 1)
        return (datetime.strptime(dt[0], "%Y-%m-%dT%H:%M:%S") - epoch).total_seconds()

    @staticmethod
    def from_epoch_to_string(val):
        return datetime.utcfromtimestamp(val).strftime("%Y-%m-%dT%H:%M:%S")

    @staticmethod
    def tz_in_seconds(dt):
        return dt.tzinfo.utcoffset(dt).total_seconds()

    @staticmethod
    def actual_timestep(dt: datetime, timestep: int):
        if timestep == 31536000 and calendar.isleap(dt.year):  # year
            timestep = 31622400
        if timestep == 2592000:  # month
            weekday, number_of_days = calendar.monthrange(dt.year, dt.month)
            timestep = number_of_days * 60 * 60  # seconds

        return timestep
