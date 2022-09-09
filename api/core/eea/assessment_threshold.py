import xml.etree.cElementTree as ET
from xml.etree.cElementTree import QName, Element, SubElement
from .environmental_objective import Environmentalobjective
from .namespaces import Namespaces


class Assessmentthreshold:
    
    def __init__(self, assessregimeId,
                    objecttype, 
                    reportingmetric, 
                    protectiontarget, 
                    assessmentthresholdexceedance, 
                    thresholdclassificationyear, 
                    thresholdclassificationreport):

        self._add_assessmentthreshold(assessregimeId,
                                    objecttype, 
                                    reportingmetric, 
                                    protectiontarget, 
                                    assessmentthresholdexceedance, 
                                    thresholdclassificationyear, 
                                    thresholdclassificationreport)

    _in = None

    def as_element(self):
        return self._in

    def _add_assessmentthreshold(self, assessregimeId, 
                                    objecttype, 
                                    reportingmetric, 
                                    protectiontarget, 
                                    assessmentthresholdexceedance, 
                                    thresholdclassificationyear, 
                                    thresholdclassificationreport):
        
         #  Assessmentthreshold
        self._in = ET.Element("{" + Namespaces.aqd + "}assessmentThreshold")
        assessmentthreshold_elm = ET.SubElement(self._in, "{" + Namespaces.aqd + "}AssessmentThreshold")
        
        assessmentthreshold_elm.append(Environmentalobjective(objecttype, 
                                                            reportingmetric, 
                                                            protectiontarget
                                                            ).as_element()
        )
             
        # Exceedance Attainment
        assessmentthresholdexceedance_elm = {ET.QName(Namespaces.xlink, "href"): assessmentthresholdexceedance}
        ET.SubElement(assessmentthreshold_elm, "{" + Namespaces.aqd + "}exceedanceAttainment", assessmentthresholdexceedance_elm)

        # ClassificationDate
        cldate_elm = ET.SubElement(assessmentthreshold_elm, "{" + Namespaces.aqd + "}classificationDate")
        ti_elm = ET.SubElement(cldate_elm, 
                               "{" + Namespaces.gml + "}TimeInstant", 
                               {QName(Namespaces.gml, "id"): assessregimeId + "_TimeInstant_ClassificationDate"},
                               )
        (ET.SubElement(ti_elm, "{" + Namespaces.gml + "}timePosition")).text = str(thresholdclassificationyear) + "-01-01"
    
        # # Classification Report
        (ET.SubElement(assessmentthreshold_elm, "{" + Namespaces.aqd + "}classificationReport")).text = thresholdclassificationreport


