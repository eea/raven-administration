from xml.etree.cElementTree import QName, Element, SubElement
from .namespaces import Namespaces


class GeographicalName:

    name = None
    language_code = None

    def __init__(self, name: str,language_code: str):

        self.name = name
        self.language_code = language_code

    def as_element(self):

        root = Element("{" + Namespaces.gn + "}GeographicalName")

        gn_attr = {QName(Namespaces.xsi, "nil"): "true", "nilReason": "missing"}

        SubElement(root,"{" + Namespaces.gn + "}language").text = self.language_code
        SubElement(root, "{" + Namespaces.gn + "}nativeness", gn_attr)
        SubElement(root, "{" + Namespaces.gn + "}nameStatus", gn_attr)
        SubElement(root, "{" + Namespaces.gn + "}sourceOfName", gn_attr)
        SubElement(root, "{" + Namespaces.gn + "}pronunciation", gn_attr)

        spelling = SubElement(root, "{" + Namespaces.gn + "}spelling")
        spelling_of_name = SubElement(spelling, "{" + Namespaces.gn + "}SpellingOfName")

        (SubElement(spelling_of_name, "{" + Namespaces.gn + "}text")).text = self.name
        SubElement(spelling_of_name, "{" + Namespaces.gn + "}script", gn_attr)

        return root


class RelatedParty:
    def __init__(self, name, organisation, locator, postcode, email, address, phone, website, language_code, localized=True):
        self._add_reporting_authority(name, organisation, locator, postcode, email, address, phone, website, language_code, localized)

    _ra = None

    def as_element(self):
        return self._ra

    def _add_reporting_authority(self, name, organisation, locator, postcode, email, address, phone, website, language_code, localized):
        self._ra = Element("{" + Namespaces.base2 + "}RelatedParty")
        iname = SubElement(self._ra, "{" + Namespaces.base2 + "}individualName")

        if localized:
            (SubElement(iname, "{" + Namespaces.gmd + "}LocalisedCharacterString")).text = name
        else:
            (SubElement(iname, "{" + Namespaces.gco + "}CharacterString")).text = name

        # Organisation name
        organisation_name = SubElement(self._ra, "{" + Namespaces.base2 + "}organisationName")
        (SubElement(organisation_name, "{" + Namespaces.gco + "}CharacterString")).text = organisation

        # Organisation contact
        c = SubElement(self._ra, "{" + Namespaces.base2 + "}contact")
        c2 = SubElement(c, "{" + Namespaces.base2 + "}Contact")

        # Organisation address
        authority_address = SubElement(c2, "{" + Namespaces.base2 + "}address")
        address_representation = SubElement(authority_address, "{" + Namespaces.ad + "}AddressRepresentation")
        admin_unit = SubElement(address_representation, "{" + Namespaces.ad + "}adminUnit")

        # Organisation geographical name
        admin_unit.append(GeographicalName(address,language_code).as_element())

        (SubElement(address_representation, "{" + Namespaces.ad + "}locatorDesignator")).text = locator
        (SubElement(address_representation, "{" + Namespaces.ad + "}postCode")).text = str(postcode)
        (SubElement(c2, "{" + Namespaces.base2 + "}electronicMailAddress")).text = email
        (SubElement(c2, "{" + Namespaces.base2 + "}telephoneVoice")).text = phone
        (SubElement(c2, "{" + Namespaces.base2 + "}website")).text = website
