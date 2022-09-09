import xml.etree.cElementTree as ET
from .namespaces import Namespaces


class Environmentalobjective:
    
    def __init__(self,
                    objecttype, 
                    reportingmetric, 
                    protectiontarget, 
                    ):

        self._add_environmentalobjective(objecttype, 
                                    reportingmetric, 
                                    protectiontarget
                                    )

    _in = None

    def as_element(self):
        return self._in

    def _add_environmentalobjective(self,
                                objecttype, 
                                reportingmetric, 
                                protectiontarget, 
                                ):
        
        # Environmental Objective
        self._in = ET.Element("{" + Namespaces.aqd + "}environmentalObjective")
        envobj_subelm = ET.SubElement(self._in, "{" + Namespaces.aqd + "}EnvironmentalObjective")
              
        # Object 
        objecttype_elm = {ET.QName(Namespaces.xlink, "href"): objecttype}
        ET.SubElement(envobj_subelm, "{" + Namespaces.aqd + "}objectiveType", objecttype_elm)

        # Reporting Metric
        reportingmetric_elm = {ET.QName(Namespaces.xlink, "href"): reportingmetric}
        ET.SubElement(envobj_subelm, "{" + Namespaces.aqd + "}reportingMetric", reportingmetric_elm)

        # Protection Target
        protectiontarget_elm = {ET.QName(Namespaces.xlink, "href"): protectiontarget}
        ET.SubElement(envobj_subelm, "{" + Namespaces.aqd + "}protectionTarget", protectiontarget_elm)
