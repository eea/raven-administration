from xml.etree.cElementTree import QName, Element, SubElement
import xml.etree.ElementTree as ET
import io
from .namespaces import Namespaces

class Geometry:

    qualified_id = None
    name = None
    gml = None
    epsg = None
    namespace = None

    def __init__(self, name: str, gml: str, ns=Namespaces.am):
        self.name = name
        self.gml = gml
        self.namespace = ns

    def as_element(self):
        # Need to have unique gml:id on sub polygon level       
        toBeReplaced = "gml:Polygon gml:id=" + '"' + self.name + '">'
        numberOfOccurences = self.gml.count(toBeReplaced)
      
        for n in range(1, numberOfOccurences+1):
            replacer = "gml:Polygon gml:id=" + '"' + self.name + "_" + str(n) + '">'
            self.gml = self.gml.replace(toBeReplaced, replacer, 1)      
        
        root = Element("{" + self.namespace + "}geometry")
        gml = io.StringIO('''<root xmlns:gml="http://www.opengis.net/gml/3.2">''' + self.gml + '</root>' )
        gml_info = ET.parse(gml).getroot()

        root.extend(gml_info)

        return root
