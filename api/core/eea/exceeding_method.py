import xml.etree.cElementTree as ET
from .namespaces import Namespaces

class Exceedingmethod:
    exceedancedescription_id = None
    assessmentlocal_id = None

    def as_SubElement(self, namespace, root):

        stationUsed = namespace + "/" + self.assessmentlocal_id
        exceedingMethod_elm = {ET.QName(Namespaces.xlink, "href"): stationUsed}
        ET.SubElement(root, "{" + Namespaces.aqd + "}stationUsed", exceedingMethod_elm)
       
        return exceedingMethod_elm