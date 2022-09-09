from xml.etree.cElementTree import QName, Element, SubElement
from .exceptions import ArgumentNullException, SchemaException
from .namespaces import Namespaces
from .inspire import Inspire
from .assessment_threshold import Assessmentthreshold
from .assessment_method import Assessmentmethod
# from .related_party import RelatedParty, GeographicalName
from .assessment_method import Assessmentmethod


class Assessmentregime:
    id = None
    name = None
    zoneid = None
    pollutant = None
    objecttype = None
    reportingmetric = None
    protectiontarget = None
    assessmentthresholdexceedance = None
    thresholdclassificationyear = None
    thresholdclassificationreport = None

    # Attribute(s) not data bound (using object mapping):
    _namespace = None
    _timezone_offset = None
    _language_code = None
    _assessmentmethods = list()  # empty list as default

    def as_element(self):

        assessmentregime_feature_member = Element("{" + Namespaces.gml + "}featureMember")

        # Assessmentregime sub-root element
        assessmentregime_elm = SubElement(assessmentregime_feature_member,
                                          "{" + Namespaces.aqd + "}AQD_AssessmentRegime",
                                          {QName(Namespaces.gml, "id"): self.id},
                                          )

        # Inspire
        assessmentregime_elm.append(
            Inspire(self._namespace, self.id,  Namespaces.aqd).as_element()
        )

        # Pollutant
        pollutant_elm = {QName(Namespaces.xlink, "href"): self.pollutant}
        SubElement(assessmentregime_elm, "{" + Namespaces.aqd + "}pollutant", pollutant_elm)

        #  Assessmentthreshold
        assessmentregime_elm.append(
            Assessmentthreshold(self.id,
                                self.objecttype,
                                self.reportingmetric,
                                self.protectiontarget,
                                self.assessmentthresholdexceedance,
                                self.thresholdclassificationyear,
                                self.thresholdclassificationreport
                                ).as_element()
        )

        # Assessmentmethod
        if len(self._assessmentmethods) == 0:
            raise SchemaException(
                "Assessment regime (id = {}) must have at least one assessment methode defined.".format(
                    self.id
                )
            )

        for assessmentmethod in self._assessmentmethods:
            assessmentregime_elm.append(assessmentmethod.as_element(self._namespace))

        # Zone
        if self.zoneid is None:
            zone_elm = {"nilReason": "inapplicable"}
        else:
            zone_id = self._namespace + "/" + str(self.zoneid)
            zone_elm = {QName(Namespaces.xlink, "href"): zone_id}

        SubElement(assessmentregime_elm, "{" + Namespaces.aqd + "}zone", zone_elm)

        return assessmentregime_feature_member

    def set_timezone_offset(self, timezone_offset: int): self._timezone_offset = timezone_offset

    def set_language_code(self, language_code: str): self._language_code = language_code

    def set_namespace(self, namespace: str): self._namespace = namespace

    def add_assessmentmethod(self, assessmentmethod: Assessmentmethod):
        if assessmentmethod is None:
            raise ArgumentNullException("Assessmentmethod cannot be a null reference.")
        self._assessmentmethods.append(assessmentmethod)
