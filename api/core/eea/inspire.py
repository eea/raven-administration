import xml.etree.cElementTree as ET
from .namespaces import Namespaces


class Inspire:
    def __init__(self, namespace, id, ns=Namespaces.ef):
        self._add_inspire(namespace, id, ns)

    _in = None

    def as_element(self):
        return self._in

    def _add_inspire(self, namespace, id, ns):
        base = Namespaces.base

        self._in = ET.Element("{" + ns + "}inspireId")
        el_identifier = ET.SubElement(self._in, "{" + base + "}Identifier")
        (ET.SubElement(el_identifier, "{" + base + "}localId")).text = id
        (ET.SubElement(el_identifier, "{" + base + "}namespace")).text = namespace
