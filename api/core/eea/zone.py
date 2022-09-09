from xml.etree.cElementTree import QName, Element, SubElement
from .exceptions import ArgumentNullException, SchemaException
from .namespaces import Namespaces
from .inspire import Inspire
from .geometry import Geometry
from .related_party import RelatedParty, GeographicalName
from .pollutant import Pollutant


class DesignationPeriod:
    id = None
    qualified_start_year = None

    def __init__(self, year: int, timezone_offset: int, qualified_zone_id: str):
        # TODO(high): The handling of timezone offset is not robust. Create date object instead.
        self.qualified_start_year = (
            str(year) + "-01-01T00:00:00+0" + str(timezone_offset) + ":00"
        )
        self.id = qualified_zone_id + "_TimePeriod_DesignationPeriod"

    def as_element(self):

        root = Element("{" + Namespaces.am + "}designationPeriod")

        time_period_attributes = {QName(Namespaces.gml, "id"): self.id}

        time_period = SubElement(
            root, "{" + Namespaces.gml + "}TimePeriod", time_period_attributes
        )

        SubElement(
            time_period, "{" + Namespaces.gml + "}beginPosition"
        ).text = self.qualified_start_year

        SubElement(
            time_period,
            "{" + Namespaces.gml + "}endPosition",
            indeterminatePosition="unknown",
        )

        return root


class LegalBasis:
    id = "LegislationCitation_"
    name = "2011/850/EC"
    short_name = "AQ IPR for e-Reporting"
    date = "2011-12-12"
    link = "http://rod.eionet.europa.eu/instruments/650"
    identification_number = "2011/850/EC"
    official_document_number = "OJ L 335, 17.12.2011, p. 86&#x2013;106"
    date_entered_into_force = "2014-01-01"
    legislation_level = (
        "http://inspire.ec.europa.eu/codeList/LegislationLevelValue/european"
    )

    def as_element(self, zone_code):

        root = Element("{" + Namespaces.am + "}legalBasis")

        legislation_citation_attributes = {QName(Namespaces.gml, "id"): self.id + str(zone_code)}
        lc = SubElement(
            root,
            "{" + Namespaces.base2 + "}LegislationCitation",
            legislation_citation_attributes,
        )
        SubElement(lc, "{" + Namespaces.base2 + "}name").text = self.name
        SubElement(lc, "{" + Namespaces.base2 + "}shortName").text = self.short_name

        # Date
        date = Element("{" + Namespaces.base2 + "}date")
        ci_date = SubElement(date, "{" + Namespaces.gmd + "}CI_Date")
        ci_date_child = SubElement(ci_date, ("{" + Namespaces.gmd + "}date"))

        SubElement(ci_date_child, "{" + Namespaces.gco + "}Date").text = self.date

        # According to "USER GUIDE TO XML & DATA MODEL v3.4", "B-Zones", page 84,
        # XML element below can be empty.
        # DateType
        dateType = SubElement(ci_date, "{" + Namespaces.gmd + "}dateType")
        SubElement(dateType, "{" + Namespaces.gmd + "}CI_DateTypeCode codeList=\"\" codeListValue=\"\"")

        lc.append(date)

        SubElement(lc, "{" + Namespaces.base2 + "}link").text = self.link
        SubElement(
            lc, "{" + Namespaces.base2 + "}identificationNumber"
        ).text = self.identification_number
        SubElement(
            lc, "{" + Namespaces.base2 + "}officialDocumentNumber"
        ).text = self.official_document_number
        SubElement(
            lc, "{" + Namespaces.base2 + "}dateEnteredIntoForce"
        ).text = self.date_entered_into_force

        legislation_level_attributes = {
            QName(Namespaces.xlink, "href"): self.legislation_level
        }
        SubElement(
            lc, "{" + Namespaces.base2 + "}level", legislation_level_attributes
        )

        return root


class ResidentPopulationYear:
    year = None
    qualified_id = None

    def __init__(self, year: int, qualified_id: str):
        self.year = str(year)
        self.qualified_id = qualified_id + "_TimePeriod_ResidentPopulationYear"

    def as_element(self):

        root = Element("{" + Namespaces.aqd + "}residentPopulationYear")

        time_instant_attributes = {QName(Namespaces.gml, "id"): self.qualified_id}

        time_instant = SubElement(
            root, "{" + Namespaces.gml + "}TimeInstant", time_instant_attributes
        )

        SubElement(
            time_instant, "{" + Namespaces.gml + "}timePosition"
        ).text = self.year

        return root


class Zone:
    id = None
    code = None
    name = None
    epsg = None
    gml = None
    type = None
    zone_type_uri = None
    population = None
    population_year = None
    year = None
    area = None
    ra_name = None
    ra_organisation = None
    ra_locator = None
    ra_postcode = None
    ra_email = None
    ra_address = None
    ra_phone = None
    ra_website = None
    beginLifespanVersion = "1997-07-16T19:00:00+01:00"

    # Attribute(s) not data bound (using object mapping):
    _prefix = ""
    _namespace = None
    _timezone_offset = None
    _language_code = None
    _time_extension_exemption_uri = (
        "http://dd.eionet.europa.eu/vocabulary/aq/timeextensiontypes/none"
    )
    _environmental_domain_uri = "http://inspire.ec.europa.eu/codeList/MediaValue/air"
    _pollutants = list()  # empty list as default

    def as_element(self):

        zone_feature_member = Element("{" + Namespaces.gml + "}featureMember")

        # Zone sub-root element
        zone_elm = SubElement(
            zone_feature_member,
            "{" + Namespaces.aqd + "}AQD_Zone",
            {QName(Namespaces.gml, "id"): self.id},
        )

        # Zone inspire
        zone_elm.append(
            Inspire(self._namespace, self.id,  Namespaces.am).as_element()
        )

        # Zone name
        zone_name = SubElement(zone_elm, "{" + Namespaces.am + "}name")
        zone_name.append(GeographicalName(self.name, self._language_code).as_element())

        # Zone geometry
        zone_elm.append(
            Geometry(
                self.name, self.gml
            ).as_element()
        )

        # AM Zone type
        am_zone_type_attributes = {
            QName(Namespaces.xlink, "href"): self.zone_type_uri
        }
        SubElement(zone_elm, "{" + Namespaces.am + "}zoneType", am_zone_type_attributes)

        # Designation Period
        zone_elm.append(
            DesignationPeriod(
                self.year, self._timezone_offset, self.get_qualified_code()
            ).as_element()
        )

        # Environmental Domain
        environmental_domain_attributes = {
            QName(Namespaces.xlink, "href"): self._environmental_domain_uri
        }
        SubElement(
            zone_elm,
            "{" + Namespaces.am + "}environmentalDomain",
            environmental_domain_attributes,
        )

      # Competent Authority
        ca = SubElement(zone_elm, "{" + Namespaces.am + "}competentAuthority")
        ca.append(
            RelatedParty(
                self.ra_name,
                self.ra_organisation,
                self.ra_locator,
                self.ra_postcode,
                self.ra_email,
                self.ra_address,
                self.ra_phone,
                self.ra_website,
                self._language_code
            ).as_element()
        )

        # beginLifespanVersion
        (SubElement(zone_elm, "{" + Namespaces.am + "}beginLifespanVersion")).text = self.beginLifespanVersion

        # Legal Basis
        zone_elm.append(LegalBasis().as_element(self.code))

        # Zone code
        (SubElement(zone_elm, "{" + Namespaces.aqd + "}zoneCode")).text = str(self.code)

        # AQD Zone type
        aqd_zone_type_attributes = {
            QName(Namespaces.xlink, "href"): self.type
        }
        SubElement(
            zone_elm, "{" + Namespaces.aqd + "}aqdZoneType", aqd_zone_type_attributes
        )

        # Resident Population
        SubElement(zone_elm, "{" + Namespaces.aqd + "}residentPopulation").text = str(
            self.population
        )

        # Resident Population Year
        zone_elm.append(
            ResidentPopulationYear(
                self.population_year, self.get_qualified_code()
            ).as_element()
        )

        # Area
        (SubElement(zone_elm, "{" + Namespaces.aqd + "}area", uom="km2")).text = str(
            self.area
        )

        # Pollutants
        if len(self._pollutants) == 0:
            raise SchemaException(
                "Zone (id = {}) must have at least one pollutant defined.".format(
                    self.id
                )
            )
        for pollutant in self._pollutants:
            zone_elm.append(pollutant.as_element())

        # Time Extension Exemption
        time_extension_exemption = {
            QName(Namespaces.xlink, "href"): self._time_extension_exemption_uri
        }
        (
            SubElement(
                zone_elm,
                "{" + Namespaces.aqd + "}timeExtensionExemption",
                time_extension_exemption,
            )
        )

        return zone_feature_member

    def set_timezone_offset(self, timezone_offset: int):

        self._timezone_offset = timezone_offset

    def set_language_code(self, language_code: str):

        self._language_code = language_code

    def set_namespace(self, namespace: str):

        self._namespace = namespace

    def get_qualified_code(self):

        return self._prefix + str(self.code)

    def add_pollutant(self, pollutant: Pollutant):

        if pollutant is None:
            raise ArgumentNullException("Pollutant cannot be a null reference.")

        self._pollutants.append(pollutant)
