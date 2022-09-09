from xml.etree.cElementTree import QName, Element, SubElement

from .namespaces import Namespaces


class Pollutant:
    uri = None
    target = None
    zone_id = None

    # Attribute(s) not data bound (using object mapping):
    _protection_target_uri = "http://dd.eionet.europa.eu/vocabulary/aq/protectiontarget"

    def as_element(self):
        root = Element("{" + Namespaces.aqd + "}pollutants")

        pollutant = SubElement(root, "{" + Namespaces.aqd + "}Pollutant")

        pollutant_code_attrib = {QName(Namespaces.xlink, "href"): self.uri}
        SubElement(pollutant, "{" + Namespaces.aqd + "}pollutantCode", pollutant_code_attrib)

        protection_target_attrib = {QName(Namespaces.xlink, "href"): self._protection_target_uri + "/" + self.target}
        SubElement(pollutant, "{" + Namespaces.aqd + "}protectionTarget", protection_target_attrib)

        return root
