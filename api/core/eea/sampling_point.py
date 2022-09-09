import xml.etree.cElementTree as ET
from .namespaces import Namespaces
from .inspire import Inspire
from .time_period import TimePeriod


class SamplingPoint:
    namespace = None
    id = None
    assessment_type = None
    station_id = None
    network_id = None
    station_classification = None
    main_emission_sources = None
    traffic_emissions = None
    heating_emissions = None
    industrial_emissions = None
    distance_source = None
    begin_position = None
    end_position = None
    change_aei_stations = None
    measurement_regime = None
    mobile = None
    latitude = None
    longitude = None
    epsg = None
    media_monitored = None
    used_aqd = None
    observing_capabilities = None

    def as_element(self):
        fm = ET.Element("{" + Namespaces.gml + "}featureMember")
        spo = ET.SubElement(fm, "{" + Namespaces.aqd + "}AQD_SamplingPoint",
                            {ET.QName(Namespaces.gml, "id"): self.id})

        spo.append(Inspire(self.namespace, self.id).as_element())

        (ET.SubElement(spo, "{" + Namespaces.ef + "}name")).text = self.station_id

        ET.SubElement(spo, "{" + Namespaces.ef + "}mediaMonitored", {
            ET.QName(Namespaces.xlink, "href"): self.media_monitored})

        geometry = ET.SubElement(spo, "{" + Namespaces.ef + "}geometry")
        point_attrib = {"srsName": "urn:ogc:def:crs:EPSG::" + str(self.epsg),
                        ET.QName(Namespaces.gml, "id"): "Point_" + self.id}
        point = ET.SubElement(geometry, "{" + Namespaces.gml + "}Point", point_attrib)
        (ET.SubElement(point, "{" + Namespaces.gml + "}pos", {"srsDimension": "2"})).text = str(
            self.latitude) + " " + str(self.longitude)

        # obs = ET.SubElement(spo, "{" + Namespaces.ef + "}observingCapability")
        for oc in self.observing_capabilities:
            obs = ET.SubElement(spo, "{" + Namespaces.ef + "}observingCapability")
            obs.append(oc.as_element())

        ET.SubElement(spo, "{" + Namespaces.ef + "}broader", {
            ET.QName(Namespaces.xlink, "href"): self.namespace + "/" + self.station_id})

        ET.SubElement(spo, "{" + Namespaces.ef + "}measurementRegime", {
            ET.QName(Namespaces.xlink, "href"): self.measurement_regime})

        (ET.SubElement(spo, "{" + Namespaces.ef + "}mobile")).text = str(self.mobile).lower()

        act = ET.SubElement(spo, "{" + Namespaces.ef + "}operationalActivityPeriod")
        act2 = ET.SubElement(act, "{" + Namespaces.ef + "}OperationalActivityPeriod",
                             {ET.QName(Namespaces.gml, "id"): "OperationalActivityPeriod_" + self.id})
        act3 = ET.SubElement(act2, "{" + Namespaces.ef + "}activityTime")
        act3.append(TimePeriod("Operational_" + self.id, self.begin_position, self.end_position).as_element())

        ET.SubElement(spo, "{" + Namespaces.ef + "}belongsTo", {
            ET.QName(Namespaces.xlink, "href"): self.namespace + "/" + self.network_id})

        ET.SubElement(spo, "{" + Namespaces.aqd + "}assessmentType", {
            ET.QName(Namespaces.xlink, "href"): self.assessment_type})

        emi = ET.SubElement(spo, "{" + Namespaces.aqd + "}relevantEmissions")
        emi2 = ET.SubElement(emi, "{" + Namespaces.aqd + "}RelevantEmissions")

        if self.distance_source is not None:
            di_em = ET.SubElement(emi2, "{" + Namespaces.aqd + "}distanceSource", {"uom": 'http://dd.eionet.europa.eu/vocabulary/uom/length/m'})
            di_em.text = self.distance_source

        if self.heating_emissions is not None:
            he_em = ET.SubElement(emi2, "{" + Namespaces.aqd + "}heatingEmissions", {"uom": 'http://dd.eionet.europa.eu/vocabulary/uom/emission/t.km-2.year-1'})
            he_em.text = self.heating_emissions

        if self.industrial_emissions is not None:
            in_em = ET.SubElement(emi2, "{" + Namespaces.aqd + "}industrialEmissions", {"uom": 'http://dd.eionet.europa.eu/vocabulary/uom/emission/t.year-1'})
            in_em.text = self.industrial_emissions

        if self.main_emission_sources is not None:
            ET.SubElement(emi2, "{" + Namespaces.aqd + "}mainEmissionSources", {
                ET.QName(Namespaces.xlink, "href"): self.main_emission_sources})

        ET.SubElement(emi2, "{" + Namespaces.aqd + "}stationClassification", {
            ET.QName(Namespaces.xlink, "href"): self.station_classification})

        if self.traffic_emissions is not None:
            tr_em = ET.SubElement(emi2, "{" + Namespaces.aqd + "}trafficEmissions", {"uom": 'http://dd.eionet.europa.eu/vocabulary/uom/emission/t.km-1.year-1'})
            tr_em.text = self.traffic_emissions

        (ET.SubElement(spo, "{" + Namespaces.aqd + "}usedAQD")).text = str(self.used_aqd).lower()

        if self.change_aei_stations is not None:
            (ET.SubElement(spo, "{" + Namespaces.aqd + "}changeAEIStations")).text = str(self.change_aei_stations)

        return fm
