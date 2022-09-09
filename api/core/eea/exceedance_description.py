import xml.etree.cElementTree as ET
from .namespaces import Namespaces
from .exceptions import ArgumentNullException, SchemaException
from .exceeding_method import Exceedingmethod


class Exceedancedescription:
    id = None
    attainment_id = None
    exceedances = None
    excedance_type = None
    max_value = None
    adjustment_type = None
    adjustment_source = None
    surface_area = None
    exposed_population = None
    population_reference_year = None
    vegetation_area = None
    area_classification = None
    exceedance_reason = None
    other_exceedance_reason = None
    exceedancedescription_element = None
    modelassessmentmetadata = None

    _exceedingmethods = list()
    _surfaceAreaUnit = 'http://dd.eionet.europa.eu/vocabularyconcept/uom/area/km2'
    _otherReason = 'http://dd.eionet.europa.eu/vocabulary/aq/exceedancereason/other'
    _assessmentType = 'http://dd.eionet.europa.eu/vocabulary/aq/assessmenttype/objective'
    _assessmentTypeDescription = 'objective'

    def as_element(self, namespace):

        root = ET.Element("{" + Namespaces.aqd + "}root")

        exceedanceDescription_elm = ET.SubElement(root, "{" + Namespaces.aqd + "}exceedanceDescription" + self.exceedancedescription_element)
        exceedanceDescription_subelm = ET.SubElement(exceedanceDescription_elm, "{" + Namespaces.aqd + "}ExceedanceDescription")

        # Exceedances
        (ET.SubElement(exceedanceDescription_subelm, "{" + Namespaces.aqd + "}exceedance")).text = str(self.exceedances).lower()
        (ET.SubElement(exceedanceDescription_subelm, "{" + Namespaces.aqd + "}" + self.excedance_type)).text = str(self.max_value)

        if self.exceedancedescription_element == "Adjustment":
            deductionAssessmentMethod_elm = ET.SubElement(exceedanceDescription_subelm, "{" + Namespaces.aqd + "}deductionAssessmentMethod")
            adjustmentMethod_elm = ET.SubElement(deductionAssessmentMethod_elm, "{" + Namespaces.aqd + "}AdjustmentMethod")

            assessmentMethod_elm = ET.SubElement(adjustmentMethod_elm, "{" + Namespaces.aqd + "}assessmentMethod")
            AssessmentMethods_elm = ET.SubElement(assessmentMethod_elm, "{" + Namespaces.aqd + "}AssessmentMethods")

            assessmentType_elm = {ET.QName(Namespaces.xlink, "href"): self._assessmentType}
            ET.SubElement(AssessmentMethods_elm, "{" + Namespaces.aqd + "}assessmentType", assessmentType_elm)

            (ET.SubElement(AssessmentMethods_elm, "{" + Namespaces.aqd + "}assessmentTypeDescription")).text = str(self._assessmentTypeDescription)

            if self.modelassessmentmetadata is not None:
                modelAssessmentMetadata_elm = {ET.QName(Namespaces.xlink, "href"): self.modelassessmentmetadata}
                ET.SubElement(AssessmentMethods_elm, "{" + Namespaces.aqd + "}modelAssessmentMetadata", modelAssessmentMetadata_elm)

            if self.adjustment_type is not None:
                adjustmentType_elm = {ET.QName(Namespaces.xlink, "href"): self.adjustment_type}
                ET.SubElement(adjustmentMethod_elm, "{" + Namespaces.aqd + "}adjustmentType", adjustmentType_elm)

            if self.adjustment_source is not None:
                adjustmentSource_elm = {ET.QName(Namespaces.xlink, "href"): self.adjustment_source}
                ET.SubElement(adjustmentMethod_elm, "{" + Namespaces.aqd + "}adjustmentSource", adjustmentSource_elm)

        if self.exceedances == True:
            # Exceedance Area
            exceedanceArea_elm = ET.SubElement(exceedanceDescription_subelm, "{" + Namespaces.aqd + "}exceedanceArea")
            exceedanceArea_subelm = ET.SubElement(exceedanceArea_elm, "{" + Namespaces.aqd + "}ExceedanceArea")
            areaClassification_elm = {ET.QName(Namespaces.xlink, "href"): self.area_classification}
            ET.SubElement(exceedanceArea_subelm, "{" + Namespaces.aqd + "}areaClassification", areaClassification_elm)

            # Surface Area
            ET.SubElement(exceedanceArea_subelm, "{" + Namespaces.aqd + "}surfaceArea", {"uom": self._surfaceAreaUnit}).text = str(self.surface_area)

            # Add Exceeding Methods
            for exceedingmethod in self._exceedingmethods:
                exceedingmethod.as_SubElement(namespace, exceedanceArea_subelm)

            # Exceedance Exposure
            exceedanceExposure_elm = ET.SubElement(exceedanceDescription_subelm, "{" + Namespaces.aqd + "}exceedanceExposure")
            exceedanceExposure_subelm = ET.SubElement(exceedanceExposure_elm, "{" + Namespaces.aqd + "}ExceedanceExposure")

            # Population Exposed
            (ET.SubElement(exceedanceExposure_subelm, "{" + Namespaces.aqd + "}populationExposed")).text = str(self.exposed_population)

            # Reference Date
            referenceYear_elm = ET.SubElement(exceedanceExposure_subelm, "{" + Namespaces.aqd + "}referenceYear")
            ti_elm = ET.SubElement(referenceYear_elm, "{" + Namespaces.gml + "}TimeInstant", {ET.QName(Namespaces.gml, "id"): "TimeInstant_" + self.id})
            (ET.SubElement(ti_elm, "{" + Namespaces.gml + "}timePosition")).text = str(self.population_reference_year) + "-01-01"

            # Exceedance Reason
            reason_elm = {ET.QName(Namespaces.xlink, "href"): self.exceedance_reason}
            ET.SubElement(exceedanceDescription_subelm, "{" + Namespaces.aqd + "}reason", reason_elm)

            if self.exceedance_reason == self._otherReason:
                other_reason_elm = {ET.QName(Namespaces.xlink, "href"): self.other_exceedance_reason}
                ET.SubElement(exceedanceDescription_subelm, "{" + Namespaces.aqd + "}reasonOther", other_reason_elm)

        return exceedanceDescription_elm

    def add_exceedingmethod(self, exceedingmethod: Exceedingmethod):
        if exceedingmethod is None:
            raise ArgumentNullException("Exceedingmethods cannot be a null reference.")
        self._exceedingmethods.append(exceedingmethod)
