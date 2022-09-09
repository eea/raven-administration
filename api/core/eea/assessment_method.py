import xml.etree.cElementTree as ET
from .namespaces import Namespaces

class Assessmentmethod:
    id = None
    assessmentregime_id = None
    assessmentlocal_id = None
    assessmenttype = None
    assessmentmethodedescription = None

    def as_element(self, namespace):
        
        _modelAssessmentTypeUrl = "http://dd.eionet.europa.eu/vocabulary/aq/assessmenttype/model"

        root = ET.Element("{" + Namespaces.aqd + "}root")

        assessmentmetode_elm = ET.SubElement(root, "{" + Namespaces.aqd + "}assessmentMethods")
        assessmentmetode_subelm = ET.SubElement(assessmentmetode_elm, "{" + Namespaces.aqd + "}AssessmentMethods")
       
        # AssessmentType
        assessmenttype_elm = {ET.QName(Namespaces.xlink, "href"): self.assessmenttype}
        ET.SubElement(assessmentmetode_subelm, "{" + Namespaces.aqd + "}assessmentType", assessmenttype_elm)

        # AssessmentTypeDescription
        (ET.SubElement(assessmentmetode_subelm, "{" + Namespaces.aqd + "}assessmentTypeDescription")).text = self.assessmentmethodedescription

        ids = self.assessmentlocal_id.split(',')
        for id in ids:
            # SamplingPointAssessmentMetadata and/or ModelAssessmentMetadata
            local_id = namespace + "/" + id
            local_id_elm = {ET.QName(Namespaces.xlink, "href"): local_id}
            if self.assessmenttype == _modelAssessmentTypeUrl:
                ET.SubElement(assessmentmetode_subelm, "{" + Namespaces.aqd + "}modelAssessmentMetadata", local_id_elm)
            else:
                ET.SubElement(assessmentmetode_subelm, "{" + Namespaces.aqd + "}samplingPointAssessmentMetadata", local_id_elm)

        return assessmentmetode_elm