import xml.etree.cElementTree as ET
from .network import Network
from .zone import Zone
from .assessment_regime import Assessmentregime
from .attainment import Attainment
from .station import Station
from .process import Process
from .sample import Sample
from .sampling_point import SamplingPoint
from .observation import Observation
from .namespaces import Namespaces
from .exceptions import *
from .responsible_reporter import ResponsibleReporter

'''
    Using pyxb to generate python classes based on the xsd schema failed.
    I therefor had to create  schema classes manually
'''


class FeatureCollection:
    def __init__(self, id):
        # Can register all. Only used ns are added
        ET.register_namespace('xsi', Namespaces.xsi)
        ET.register_namespace('gml', Namespaces.gml)
        ET.register_namespace('aqd', Namespaces.aqd)
        ET.register_namespace('ef', Namespaces.ef)
        ET.register_namespace('base', Namespaces.base)
        ET.register_namespace('xlink', Namespaces.xlink)
        ET.register_namespace('base2', Namespaces.base2)
        ET.register_namespace('gco', Namespaces.gco)
        ET.register_namespace('ad', Namespaces.ad)
        ET.register_namespace('gn', Namespaces.gn)
        ET.register_namespace('ompr', Namespaces.ompr)
        ET.register_namespace('gmd', Namespaces.gmd)
        ET.register_namespace('sams', Namespaces.sams)
        ET.register_namespace('sam', Namespaces.sam)
        ET.register_namespace('om', Namespaces.om)
        ET.register_namespace('am', Namespaces.am)
        ET.register_namespace('swe', Namespaces.swe)
        self._add_feature_collection(id)

    _fc = None

    def as_element(self):
        return self._fc

    def _add_feature_collection(self, id):
        xsi_val = "http://dd.eionet.europa.eu/schemaset/id2011850eu-1.0 " \
                  "http://dd.eionet.europa.eu/schemas/id2011850eu-1.0/AirQualityReporting.xsd"

        fc_attributes = {
            ET.QName(Namespaces.xsi, "schemaLocation"): xsi_val,
            ET.QName(Namespaces.gml, "id"): id
        }
        self._fc = ET.Element("{" + Namespaces.gml + "}FeatureCollection", fc_attributes)

    def add_zone(self, zone):
        if not isinstance(zone, Zone):
            raise InternalSchemaException("Object is not of type Zone")

        self._fc.append(zone.as_element())

    def add_assessmentregime(self, assessmentregime):
        if not isinstance(assessmentregime, Assessmentregime):
            raise InternalSchemaException("Object is not of type Assessmentregime")

        self._fc.append(assessmentregime.as_element())

    def add_attainment(self, attainment):
        if not isinstance(attainment, Attainment):
            raise InternalSchemaException("Object is not of type Attainment")

        self._fc.append(attainment.as_element())

    def add_network(self, network):
        if not isinstance(network, Network):
            raise InternalSchemaException("Object is not of type Network")

        self._fc.append(network.as_element())

    def add_station(self, station):
        if not isinstance(station, Station):
            raise InternalSchemaException("Object is not of type Station")

        self._fc.append(station.as_element())

    def add_process(self, process):
        if not isinstance(process, Process):
            raise InternalSchemaException("Object is not of type Process")

        self._fc.append(process.as_element())

    def add_sampling_point(self, sampling_point):
        if not isinstance(sampling_point, SamplingPoint):
            raise InternalSchemaException("Object is not of type SamplingPoint")

        self._fc.append(sampling_point.as_element())

    def add_sample(self, sample):
        if not isinstance(sample, Sample):
            raise InternalSchemaException("Object is not of type Sample")

        self._fc.append(sample.as_element())

    def add_responsible_reporter(self, reporter):
        if not isinstance(reporter, ResponsibleReporter):
            raise InternalSchemaException("Object is not of type ResponsibleReporter")

        self._fc.insert(0, reporter.as_element())

    def add_observation(self, observation):
        if not isinstance(observation, Observation):
            raise InternalSchemaException("Object is not of type Observation")

        self._fc.append(observation.as_element())
