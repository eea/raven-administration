import xml.etree.cElementTree as ET
from .namespaces import Namespaces
from .inspire import Inspire


class Sample:
    namespace = None
    uom_m = None
    id = None
    inlet_height = None
    building_distance = None
    kerb_distance = None
    latitude = None
    longitude = None
    epsg = None

    def as_element(self):
        fm = ET.Element("{" + Namespaces.gml + "}featureMember")
        sam = ET.SubElement(fm, "{" + Namespaces.aqd + "}AQD_Sample", {ET.QName(Namespaces.gml, "id"): self.id})

        ET.SubElement(sam, "{" + Namespaces.sam + "}sampledFeature", {ET.QName(Namespaces.xlink, "href"): "SAF_" + self.id})

        shp = ET.SubElement(sam, "{" + Namespaces.sams + "}shape")
        point_attrib = {"srsName": "urn:ogc:def:crs:EPSG::" + str(self.epsg),
                        ET.QName(Namespaces.gml, "id"): "Point_" + self.id}
        point = ET.SubElement(shp, "{" + Namespaces.gml + "}Point", point_attrib)
        (ET.SubElement(point, "{" + Namespaces.gml + "}pos", {"srsDimension": "2"})).text = str(
            self.latitude) + " " + str(self.longitude)

        sam.append(Inspire(self.namespace, self.id, Namespaces.aqd).as_element())

        (ET.SubElement(sam, "{" + Namespaces.aqd + "}inletHeight", {"uom": self.uom_m})).text = str(self.inlet_height)
        if self.building_distance is not None:
            (ET.SubElement(sam, "{" + Namespaces.aqd + "}buildingDistance", {"uom": self.uom_m})).text = str(self.building_distance)
        if self.kerb_distance is not None:
            (ET.SubElement(sam, "{" + Namespaces.aqd + "}kerbDistance", {"uom": self.uom_m})).text = str(self.kerb_distance)

        return fm



