import xml.etree.cElementTree as ET
from .namespaces import Namespaces
from .inspire import Inspire
from .time_period import TimePeriod


class Station:
    namespace = None
    id = None
    begin_position = None
    end_position = None
    name = None
    media_monitored = None
    measurement_regime = None
    mobile = None
    latitude = None
    longitude = None
    altitude = None
    epsg = None
    network_id = None
    national_station_code = None
    municipality = None
    eoi_code = None
    area_classification = None
    station_info = None
    uom_m = None

    def as_element(self):
        fm = ET.Element("{" + Namespaces.gml + "}featureMember")
        sta = ET.SubElement(fm, "{" + Namespaces.aqd + "}AQD_Station", {ET.QName(Namespaces.gml, "id"): self.id})

        sta.append(Inspire(self.namespace, self.id).as_element())

        (ET.SubElement(sta, "{" + Namespaces.ef + "}name")).text = self.name
        ET.SubElement(sta, "{" + Namespaces.ef + "}mediaMonitored", {
            ET.QName(Namespaces.xlink, "href"): self.media_monitored})

        geometry = ET.SubElement(sta, "{" + Namespaces.ef + "}geometry")
        point_attrib = {"srsName": "urn:ogc:def:crs:EPSG::" + str(self.epsg),
                        ET.QName(Namespaces.gml, "id"): "Point_" + self.id}
        point = ET.SubElement(geometry, "{" + Namespaces.gml + "}Point", point_attrib)
        (ET.SubElement(point, "{" + Namespaces.gml + "}pos", {"srsDimension": "2"})).text = str(
            self.latitude) + " " + str(self.longitude)

        ET.SubElement(sta, "{" + Namespaces.ef + "}measurementRegime", {
            ET.QName(Namespaces.xlink, "href"): self.measurement_regime})

        (ET.SubElement(sta, "{" + Namespaces.ef + "}mobile")).text = str(self.mobile).lower()

        act = ET.SubElement(sta, "{" + Namespaces.ef + "}operationalActivityPeriod")
        act2 = ET.SubElement(act, "{" + Namespaces.ef + "}OperationalActivityPeriod",
                             {ET.QName(Namespaces.gml, "id"): "OperationalActivityPeriod_" + self.id})
        act3 = ET.SubElement(act2, "{" + Namespaces.ef + "}activityTime")
        act3.append(TimePeriod(self.id, self.begin_position, self.end_position).as_element())

        ET.SubElement(sta, "{" + Namespaces.ef + "}belongsTo",
                      {ET.QName(Namespaces.xlink, "href"): self.namespace + "/" + self.network_id})
        (ET.SubElement(sta, "{" + Namespaces.aqd + "}natlStationCode")).text = str(self.national_station_code)
        (ET.SubElement(sta, "{" + Namespaces.aqd + "}municipality")).text = str(self.municipality)
        (ET.SubElement(sta, "{" + Namespaces.aqd + "}EUStationCode")).text = self.eoi_code

        if self.station_info is not None:
            (ET.SubElement(sta, "{" + Namespaces.aqd + "}stationInfo")).text = str(self.station_info)

        ET.SubElement(sta, "{" + Namespaces.aqd + "}areaClassification",
                      {ET.QName(Namespaces.xlink, "href"): self.area_classification})
        (ET.SubElement(sta, "{" + Namespaces.aqd + "}altitude", {"uom": self.uom_m})).text = str(self.altitude)

        return fm
