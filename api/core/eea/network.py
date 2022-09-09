from xml.etree.cElementTree import QName, Element, SubElement
from .namespaces import Namespaces
from .inspire import Inspire
from .time_period import TimePeriod
from .related_party import RelatedParty


class Network:
    namespace = None
    prefix = None
    id = None
    begin_position = None
    end_position = None
    name = None
    media_monitored = None
    organisational = None
    aggregation_timezone = None
    rname = None
    rorganisation = None
    rlocator = None
    rpostcode = None
    remail = None
    raddress = None
    rphone = None
    rwebsite = None
    language_code = None

    def as_element(self):
        fm = Element("{" + Namespaces.gml + "}featureMember")
        netw = SubElement(fm, "{" + Namespaces.aqd + "}AQD_Network", {QName(Namespaces.gml, "id"): self.id})

        netw.append(Inspire(self.namespace, self.id).as_element())

        (SubElement(netw, "{" + Namespaces.ef + "}name")).text = self.name
        SubElement(netw, "{" + Namespaces.ef + "}mediaMonitored", {
            QName(Namespaces.xlink, "href"): self.media_monitored})

        rp = SubElement(netw, "{" + Namespaces.ef + "}responsibleParty")
        rp.append(
            RelatedParty(self.rname, self.rorganisation, self.rlocator, self.rpostcode, self.remail, self.raddress, self.rphone, self.rwebsite, self.language_code).as_element())

        SubElement(netw, "{" + Namespaces.ef + "}organisationLevel", {
            QName(Namespaces.xlink, "href"): self.organisational})

        act = SubElement(netw, "{" + Namespaces.aqd + "}operationActivityPeriod")
        act.append(TimePeriod(self.id, self.begin_position, self.end_position).as_element())

        atz_attrib = {QName(Namespaces.xlink, "href"): self.aggregation_timezone}
        SubElement(netw, "{" + Namespaces.aqd + "}aggregationTimeZone", atz_attrib)

        return fm
