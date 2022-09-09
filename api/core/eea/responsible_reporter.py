from xml.etree.cElementTree import QName, Element, SubElement
from .namespaces import Namespaces
from .inspire import Inspire
from .time_period import TimePeriod
from .related_party import RelatedParty


class ResponsibleReporter:
    namespace = None
    prefix = None
    id = None
    change = None
    begin = None
    end = None
    description = None
    name = None
    organisation = None
    locator = None
    postcode = None
    email = None
    address = None
    phone = None
    website = None
    ids = None
    language_code = None

    def as_element(self):
        fm = Element("{" + Namespaces.gml + "}featureMember")
        header = SubElement(fm, "{" + Namespaces.aqd + "}AQD_ReportingHeader",
                            {QName(Namespaces.gml, "id"): self.prefix + "_ReportingHeader"})

        (SubElement(header, "{" + Namespaces.aqd + "}change")).text = (str(self.change)).lower()
        (SubElement(header, "{" + Namespaces.aqd + "}changeDescription")).text = self.description
        header.append(
            Inspire(self.namespace, "ReportingHeader_" + self.prefix, Namespaces.aqd).as_element())

        ra = SubElement(header, "{" + Namespaces.aqd + "}reportingAuthority")
        ra.append(RelatedParty(self.name, self.organisation, self.locator, self.postcode, self.email,
                               self.address, self.phone, self.website,self.language_code, False).as_element())

        act = SubElement(header, "{" + Namespaces.aqd + "}reportingPeriod")
        act.append(TimePeriod(self.prefix, self.begin, self.end).as_element())

        for i in self.ids:
            SubElement(header, "{" + Namespaces.aqd + "}content",
                       {QName(Namespaces.xlink, "href"): self.namespace + "/" + i})

        return fm
