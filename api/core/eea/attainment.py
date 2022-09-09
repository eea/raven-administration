from xml.etree.cElementTree import QName, Element, SubElement
from .exceptions import ArgumentNullException, SchemaException
from .namespaces import Namespaces
from .inspire import Inspire
from .environmental_objective import Environmentalobjective
from .exceedance_description import Exceedancedescription


class Attainment:
    id = None
    name = None
    assessmentregime_id = None
    comment = None
    pollutant = None
    objecttype = None
    reportingmetric = None
    protectiontarget = None
    assessmentregime_id = None
    zoneid = None

    # Attribute(s) not data bound (using object mapping):
    _namespace = None
    _timezone_offset = None
    _language_code = None
    _exceedancedescriptions = list()  # empty list as default

    def as_element(self):

        attainment_feature_member = Element("{" + Namespaces.gml + "}featureMember")

        # Attainment sub-root element
        attainment_elm = SubElement(attainment_feature_member,
                                    "{" + Namespaces.aqd + "}AQD_Attainment",
                                    {QName(Namespaces.gml, "id"): self.id},
                                    )

        # Inspire
        attainment_elm.append(
            Inspire(self._namespace, self.id,  Namespaces.aqd).as_element()
        )

        # Pollutant
        pollutant_elm = {QName(Namespaces.xlink, "href"): self.pollutant}
        SubElement(attainment_elm, "{" + Namespaces.aqd + "}pollutant", pollutant_elm)

        #  Environmental Objective
        attainment_elm.append(Environmentalobjective(self.objecttype,
                                                     self.reportingmetric,
                                                     self.protectiontarget
                                                     ).as_element()
                              )

        # Exceedance Description
        for exceedancedescription in self._exceedancedescriptions:
            attainment_elm.append(exceedancedescription.as_element(self._namespace))

        # Comment
        SubElement(attainment_elm, "{" + Namespaces.aqd + "}comment").text = self.comment

        # Zone
        if self.zoneid is None:
            zone_elm = {"nilReason": "inapplicable"}
        else:
            zone_id = self._namespace + "/" + str(self.zoneid)
            zone_elm = {QName(Namespaces.xlink, "href"): zone_id}
        SubElement(attainment_elm, "{" + Namespaces.aqd + "}zone", zone_elm)

        # Assessment Regime
        assessmentregimeid = self._namespace + "/" + str(self.assessmentregime_id)
        assessmentregime_elm = {QName(Namespaces.xlink, "href"): assessmentregimeid}
        SubElement(attainment_elm, "{" + Namespaces.aqd + "}assessment", assessmentregime_elm)

        return attainment_feature_member

    def set_timezone_offset(self, timezone_offset: int): self._timezone_offset = timezone_offset

    def set_language_code(self, language_code: str): self._language_code = language_code

    def set_namespace(self, namespace: str): self._namespace = namespace

    def add_exceedancedescription(self, exceedancedescription: Exceedancedescription):
        if exceedancedescription is None:
            raise ArgumentNullException("Exceedancedescription cannot be a null reference.")
        self._exceedancedescriptions.append(exceedancedescription)
