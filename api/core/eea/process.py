import xml.etree.cElementTree as ET
from .namespaces import Namespaces
from .inspire import Inspire
from .related_party import RelatedParty


class Process:
    namespace = None
    id = None
    responsible_authority_id = None
    measurement_type = None
    measurement_method = None
    other_measurement_method = None
    sampling_method = None
    other_sampling_method = None
    analytical_tech = None
    other_analytical_tech = None
    sampling_equipment = None
    other_sampling_equipment = None
    measurement_equipment = None
    other_measurement_equipment = None
    equiv_demonstration = None
    equiv_demonstration_report = None
    detection_limit = None
    detection_limit_uom = None
    uncertainty_estimate = None
    documentation = None
    qa_report = None
    duration_number = None
    duration_unit = None
    cadence_number = None
    cadence_unit = None
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
        fm = ET.Element("{" + Namespaces.gml + "}featureMember")
        proc = ET.SubElement(fm, "{" + Namespaces.aqd + "}AQD_SamplingPointProcess", {ET.QName(Namespaces.gml, "id"): self.id})

        proc.append(Inspire(self.namespace, self.id, Namespaces.ompr).as_element())

        (ET.SubElement(proc, "{" + Namespaces.ompr + "}type")).text = "Ambient air quality measurement instrument configuration"

        rp = ET.SubElement(proc, "{" + Namespaces.ompr + "}responsibleParty")
        rp.append(RelatedParty(self.rname, self.rorganisation, self.rlocator, self.rpostcode, self.remail, self.raddress, self.rphone, self.rwebsite, self.language_code).as_element())

        mt_attrib = {ET.QName(Namespaces.xlink, "href"): self.measurement_type}
        ET.SubElement(proc, "{" + Namespaces.aqd + "}measurementType", mt_attrib)

        if self.measurement_method is not None:
            mm = ET.SubElement(proc, "{" + Namespaces.aqd + "}measurementMethod")
            mm2 = ET.SubElement(mm, "{" + Namespaces.aqd + "}MeasurementMethod")
            ET.SubElement(mm2, "{" + Namespaces.aqd + "}measurementMethod", {ET.QName(Namespaces.xlink, "href"): self.measurement_method})
            if self.other_measurement_method is not None:
                (ET.SubElement(mm2, "{" + Namespaces.aqd + "}otherMeasurementMethod")).text = self.other_measurement_method

        if self.measurement_equipment is not None:
            me = ET.SubElement(proc, "{" + Namespaces.aqd + "}measurementEquipment")
            me2 = ET.SubElement(me, "{" + Namespaces.aqd + "}MeasurementEquipment")
            ET.SubElement(me2, "{" + Namespaces.aqd + "}equipment", {ET.QName(Namespaces.xlink, "href"): self.measurement_equipment})
            if self.other_measurement_equipment is not None:
                (ET.SubElement(me2, "{" + Namespaces.aqd + "}otherEquipment")).text = self.other_measurement_equipment

        if self.sampling_method is not None:
            sm = ET.SubElement(proc, "{" + Namespaces.aqd + "}samplingMethod")
            sm2 = ET.SubElement(sm, "{" + Namespaces.aqd + "}SamplingMethod")
            ET.SubElement(sm2, "{" + Namespaces.aqd + "}samplingMethod", {ET.QName(Namespaces.xlink, "href"): self.sampling_method})
            if self.other_sampling_method is not None:
                (ET.SubElement(sm2, "{" + Namespaces.aqd + "}otherSamplingMethod")).text = self.other_sampling_method

        if self.analytical_tech is not None:
            at = ET.SubElement(proc, "{" + Namespaces.aqd + "}analyticalTechnique")
            at2 = ET.SubElement(at, "{" + Namespaces.aqd + "}AnalyticalTechnique")
            ET.SubElement(at2, "{" + Namespaces.aqd + "}analyticalTechnique", {ET.QName(Namespaces.xlink, "href"): self.analytical_tech})
            if self.other_analytical_tech is not None:
                (ET.SubElement(at2, "{" + Namespaces.aqd + "}otherAnalyticalTechnique")).text = self.other_analytical_tech

        if self.sampling_equipment is not None:
            se = ET.SubElement(proc, "{" + Namespaces.aqd + "}samplingEquipment")
            se2 = ET.SubElement(se, "{" + Namespaces.aqd + "}SamplingEquipment")
            ET.SubElement(se2, "{" + Namespaces.aqd + "}equipment", {ET.QName(Namespaces.xlink, "href"): self.sampling_equipment})
            if self.other_sampling_equipment is not None:
                (ET.SubElement(se2, "{" + Namespaces.aqd + "}otherEquipment")).text = self.other_sampling_equipment

        if self.equiv_demonstration is not None:
            ed = ET.SubElement(proc, "{" + Namespaces.aqd + "}equivalenceDemonstration")
            ed2 = ET.SubElement(ed, "{" + Namespaces.aqd + "}EquivalenceDemonstration")
            ET.SubElement(ed2, "{" + Namespaces.aqd + "}equivalenceDemonstrated", {ET.QName(Namespaces.xlink, "href"): self.equiv_demonstration})
            if self.equiv_demonstration_report is not None:
                (ET.SubElement(ed2, "{" + Namespaces.aqd + "}demonstrationReport")).text = self.equiv_demonstration_report

        dq = ET.SubElement(proc, "{" + Namespaces.aqd + "}dataQuality")
        dq2 = ET.SubElement(dq, "{" + Namespaces.aqd + "}DataQuality")
        if self.detection_limit is not None:
            (ET.SubElement(dq2, "{" + Namespaces.aqd + "}detectionLimit", {"uom": str(self.detection_limit_uom)})).text = str(self.detection_limit)

        (ET.SubElement(dq2, "{" + Namespaces.aqd + "}documentation")).text = str(self.documentation) if self.documentation is not None else ""
        (ET.SubElement(dq2, "{" + Namespaces.aqd + "}qaReport")).text = str(self.qa_report) if self.qa_report is not None else ""

        du = ET.SubElement(proc, "{" + Namespaces.aqd + "}duration")
        du2 = ET.SubElement(du, "{" + Namespaces.aqd + "}TimeReferences")
        ET.SubElement(du2, "{" + Namespaces.aqd + "}unit", {ET.QName(Namespaces.xlink, "href"): self.duration_unit})
        (ET.SubElement(du2, "{" + Namespaces.aqd + "}numUnits")).text = str(self.duration_number)

        ca = ET.SubElement(proc, "{" + Namespaces.aqd + "}cadence")
        ca2 = ET.SubElement(ca, "{" + Namespaces.aqd + "}TimeReferences")
        ET.SubElement(ca2, "{" + Namespaces.aqd + "}unit", {ET.QName(Namespaces.xlink, "href"): self.cadence_unit})
        (ET.SubElement(ca2, "{" + Namespaces.aqd + "}numUnits")).text = str(self.cadence_number)

        return fm
