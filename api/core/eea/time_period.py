import xml.etree.cElementTree as ET
from .namespaces import Namespaces


class TimePeriod:
    def __init__(self, id, begin_position, end_position):
        self._add_time_period(id, begin_position, end_position)

    _UNKNOWN = "unknown"
    _tp = None

    def as_element(self):
        return self._tp

    def _add_time_period(self, id, begin_position, end_position):
        gml = Namespaces.gml

        tp_id = "TimePeriod_" + id
        self._tp = ET.Element("{" + gml + "}TimePeriod", {ET.QName(Namespaces.gml, "id"): tp_id})
        (ET.SubElement(self._tp, "{" + gml + "}beginPosition")).text = begin_position

        if end_position is None:
            ET.SubElement(self._tp, "{" + gml + "}endPosition", {"indeterminatePosition": self._UNKNOWN})
        else:
            (ET.SubElement(self._tp, "{" + gml + "}endPosition")).text = end_position
