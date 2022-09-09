import xml.etree.cElementTree as ET
from .namespaces import Namespaces
from .inspire import Inspire
from .time_period import TimePeriod
from .parameter import Parameter
from .eea_utils import EeaUtils


class Observation:
    id = None
    namespace = None
    prefix = None
    sampling_point_id = None
    cnt = None
    vals = None
    concentration = None
    timestep = None
    min_begin_position = None
    max_begin_position = None
    min_end_position = None
    max_end_position = None
    process_id = None
    sample_id = None
    assessment_type = None
    pollutant = None

    def as_element(self):
        fm = ET.Element("{" + Namespaces.gml + "}featureMember")
        obs = ET.SubElement(fm, "{" + Namespaces.om + "}OM_Observation", {ET.QName(Namespaces.gml, "id"): self.prefix + "_" + self.id})

        pt = ET.SubElement(obs, "{" + Namespaces.om + "}phenomenonTime")
        pt.append(TimePeriod(self.prefix + "_" + self.id, self.min_begin_position, self.max_end_position).as_element())

        rt = ET.SubElement(obs, "{" + Namespaces.om + "}resultTime")
        ti = ET.SubElement(rt, "{" + Namespaces.gml + "}TimeInstant", {ET.QName(Namespaces.gml, "id"): "TimeInstant_" + self.prefix + "_" + self.id})
        (ET.SubElement(ti, "{" + Namespaces.gml + "}timePosition")).text = EeaUtils.local_datetime()

        ET.SubElement(obs, "{" + Namespaces.om + "}procedure", {
            ET.QName(Namespaces.xlink, "href"): self.namespace + "/" + self.process_id})

        obs.append(
            Parameter("http://dd.eionet.europa.eu/vocabulary/aq/processparameter/AssessmentType", self.assessment_type).as_element())

        obs.append(
            Parameter("http://dd.eionet.europa.eu/vocabulary/aq/processparameter/SamplingPoint",
                      self.namespace + "/" + self.sampling_point_id).as_element())

        ET.SubElement(obs, "{" + Namespaces.om + "}observedProperty", {
            ET.QName(Namespaces.xlink, "href"): self.pollutant})

        ET.SubElement(obs, "{" + Namespaces.om + "}featureOfInterest", {
            ET.QName(Namespaces.xlink, "href"): self.namespace + "/" + self.sample_id})

        re = ET.SubElement(obs, "{" + Namespaces.om + "}result")
        da = ET.SubElement(re, "{" + Namespaces.swe + "}DataArray")

        ec = ET.SubElement(da, "{" + Namespaces.swe + "}elementCount")
        ec2 = ET.SubElement(ec, "{" + Namespaces.swe + "}Count")
        (ET.SubElement(ec2, "{" + Namespaces.swe + "}value")).text = str(self.cnt)

        et = ET.SubElement(da, "{" + Namespaces.swe + "}elementType", {"name": "FixedObservations"})
        dr = ET.SubElement(et, "{" + Namespaces.swe + "}DataRecord")

        dr1 = ET.SubElement(dr, "{" + Namespaces.swe + "}field", {"name": "StartTime"})
        dr1_1 = ET.SubElement(dr1, "{" + Namespaces.swe + "}Time", {"definition": "http://www.opengis.net/def/property/OGC/0/SamplingTime"})
        ET.SubElement(dr1_1, "{" + Namespaces.swe + "}uom", {ET.QName(Namespaces.xlink, "href"): "http://www.opengis.net/def/uom/ISO-8601/0/Gregorian"})

        dr2 = ET.SubElement(dr, "{" + Namespaces.swe + "}field", {"name": "EndTime"})
        dr2_1 = ET.SubElement(dr2, "{" + Namespaces.swe + "}Time", {"definition": "http://www.opengis.net/def/property/OGC/0/SamplingTime"})
        ET.SubElement(dr2_1, "{" + Namespaces.swe + "}uom", {ET.QName(Namespaces.xlink, "href"): "http://www.opengis.net/def/uom/ISO-8601/0/Gregorian"})

        dr3 = ET.SubElement(dr, "{" + Namespaces.swe + "}field", {"name": "Verification"})
        ET.SubElement(dr3, "{" + Namespaces.swe + "}Category", {"definition": "http://dd.eionet.europa.eu/vocabulary/aq/observationverification"})

        dr4 = ET.SubElement(dr, "{" + Namespaces.swe + "}field", {"name": "Validity"})
        ET.SubElement(dr4, "{" + Namespaces.swe + "}Category", {"definition": "http://dd.eionet.europa.eu/vocabulary/aq/observationvalidity"})

        dr5 = ET.SubElement(dr, "{" + Namespaces.swe + "}field", {"name": "Value"})
        dr5_1 = ET.SubElement(dr5, "{" + Namespaces.swe + "}Quantity", {"definition": str(self.timestep)})
        ET.SubElement(dr5_1, "{" + Namespaces.swe + "}uom", {ET.QName(Namespaces.xlink, "href"): self.concentration})

        en = ET.SubElement(da, "{" + Namespaces.swe + "}encoding")
        ET.SubElement(en, "{" + Namespaces.swe + "}TextEncoding", {"blockSeparator": "@@", "tokenSeparator": ",", "decimalSeparator": "."})

        (ET.SubElement(da, "{" + Namespaces.swe + "}values")).text = self.vals

        return fm
