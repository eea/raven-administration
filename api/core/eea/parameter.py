import xml.etree.cElementTree as ET
from .namespaces import Namespaces


class Parameter:
    def __init__(self, link, value):
        self._add_parameter(link, value)

    _para = None

    def as_element(self):
        return self._para

    def _add_parameter(self, link, value):
        self._para = ET.Element("{" + Namespaces.om + "}parameter")
        nv = ET.SubElement(self._para, "{" + Namespaces.om + "}NamedValue")
        ET.SubElement(nv, "{" + Namespaces.om + "}name", {ET.QName(Namespaces.xlink, "href"): link})
        (ET.SubElement(nv, "{" + Namespaces.om + "}value")).text = value

