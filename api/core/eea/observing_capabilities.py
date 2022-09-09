import xml.etree.cElementTree as ET
from .namespaces import Namespaces
from .inspire import Inspire
from .time_period import TimePeriod


class ObservingCapabilities:
    namespace = None
    id = None
    begin_position = None
    end_position = None
    process_id = None
    pollutant = None
    sample_id = None
    process_type = None
    result_nature = None

    def as_element(self):

        obs = ET.Element("{" + Namespaces.ef + "}ObservingCapability",
                             {ET.QName(Namespaces.gml, "id"): self.id})

        obs2 = ET.SubElement(obs, "{" + Namespaces.ef + "}observingTime")
        obs2.append(
            TimePeriod("Observing" + self.id, self.begin_position, self.end_position).as_element())

        ET.SubElement(obs, "{" + Namespaces.ef + "}processType", {
            ET.QName(Namespaces.xlink, "href"): self.process_type})
        ET.SubElement(obs, "{" + Namespaces.ef + "}resultNature", {
            ET.QName(Namespaces.xlink, "href"): self.result_nature})
        ET.SubElement(obs, "{" + Namespaces.ef + "}procedure", {
            ET.QName(Namespaces.xlink, "href"): self.namespace + "/" + self.process_id})
        ET.SubElement(obs, "{" + Namespaces.ef + "}featureOfInterest", {
            ET.QName(Namespaces.xlink, "href"): self.namespace + "/" + self.sample_id})
        ET.SubElement(obs, "{" + Namespaces.ef + "}observedProperty", {
            ET.QName(Namespaces.xlink, "href"): self.pollutant})

        return obs


