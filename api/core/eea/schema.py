from typing import List

from .exceptions import SchemaException
from .feature_collection import FeatureCollection
from .pollutant import Pollutant
from .responsible_reporter import ResponsibleReporter
from .zone import Zone
from .attainment import Attainment
from .assessment_regime import Assessmentregime
from .assessment_method import Assessmentmethod
from .attainment import Attainment
from .exceedance_description import Exceedancedescription
from .exceeding_method import Exceedingmethod


class Schema:
    namespace = None
    observation_prefix = None
    uom_m = None
    language_code = None

    #  Data flow B (Zones & Agglomerations)
    def get_dataflow_b(self, reporting_header: ResponsibleReporter, zones: List[Zone],
                       pollutants: List[Pollutant], timezone_offset: int):

        ids = []
        fc = FeatureCollection('B_FeatureCollection')

        # Create reporting header
        if reporting_header == None:
            raise SchemaException("ReportingHeader cannot be empty")
        reporting_header.namespace = self.namespace
        reporting_header.prefix = "B"
        reporting_header.ids = ids
        reporting_header.language_code = self.language_code

        # Add zones to feature collection
        if zones == None or len(zones) == 0:
            raise SchemaException("Zone collection cannot be empty")

        for zone in zones:
            ids.append(zone.id)
            zone.set_namespace(self.namespace)
            zone.set_language_code(self.language_code)
            zone.set_timezone_offset(timezone_offset)

            # Clean Pollutants
            zone._pollutants = []

            for pollutant in pollutants:
                if pollutant.zone_id == zone.id:
                    zone.add_pollutant(pollutant)

            fc.add_zone(zone)

        # Add the reporting header to feature collection
        fc.add_responsible_reporter(reporting_header)

        return fc.as_element()

    #  Data flow D (Assessment Metadata)
    def get_dataflow_d(self, reporting_header, networks, stations, sampling_points, samples, processes):
        ids = []
        fc = FeatureCollection('D_FeatureCollection')

        # Add AQD_Networks
        if networks == None or len(networks) == 0:
            raise SchemaException("Networks cannot be empty")
        for n in networks:
            ids.append(n.id)
            n.namespace = self.namespace
            n.language_code = self.language_code

            fc.add_network(n)

        # Add AQD_Stations
        if stations == None or len(stations) == 0:
            raise SchemaException("Stations cannot be empty")
        for s in stations:
            ids.append(s.id)
            s.namespace = self.namespace
            s.uom_m = self.uom_m
            fc.add_station(s)

        # Add AQD_SamplingPoint
        if sampling_points == None or len(sampling_points) == 0:
            raise SchemaException("Sampling points cannot be empty")
        for sa in sampling_points:
            ids.append(sa.id)
            sa.namespace = self.namespace

            if sa.observing_capabilities == None or len(sa.observing_capabilities) == 0:
                raise SchemaException("Observation capabilities cannot be empty for sampling point " + sa.id)
            for oc in sa.observing_capabilities:
                oc.namespace = self.namespace

            fc.add_sampling_point(sa)

        # Add AQD_Sample
        if samples == None or len(samples) == 0:
            raise SchemaException("Samples cannot be empty")
        for sa in samples:
            ids.append(sa.id)
            sa.namespace = self.namespace
            sa.uom_m = self.uom_m
            fc.add_sample(sa)

        # Add AQD_SamplingPointProcess
        if processes == None or len(processes) == 0:
            raise SchemaException("Processes cannot be empty")
        for p in processes:
            ids.append(p.id)
            p.namespace = self.namespace
            p.language_code = self.language_code
            fc.add_process(p)

        # Add AQD_ReportingHeader
        if reporting_header == None:
            raise SchemaException("ReportingHeader cannot be empty")
        reporting_header.namespace = self.namespace
        reporting_header.prefix = "D"
        reporting_header.ids = ids
        reporting_header.language_code = self.language_code
        fc.add_responsible_reporter(reporting_header)

        return fc.as_element()

    #  Data flow E (Assessment Data)
    def get_dataflow_e(self, reporting_header, observations):
        ids = []
        fc = FeatureCollection(self.observation_prefix + '_FeatureCollection')

        # Add OM_Observation
        for o in observations:
            ids.append(self.observation_prefix + "_" + o.sampling_point_id)
            o.namespace = self.namespace
            o.prefix = self.observation_prefix
            fc.add_observation(o)

        # Add AQD_ReportingHeader
        if reporting_header is None:
            raise SchemaException("ReportingHeader cannot be empty")
        reporting_header.namespace = self.namespace
        reporting_header.prefix = self.observation_prefix
        reporting_header.ids = ids
        reporting_header.language_code = self.language_code
        fc.add_responsible_reporter(reporting_header)

        return fc.as_element()

    #  Dataflow C (Assessment Regime)
    def get_dataflow_c(self, reporting_header: ResponsibleReporter, assessmentregimes: List[Assessmentregime],
                       assessmentmethods: List[Assessmentmethod], timezone_offset: int):

        ids = []
        fc = FeatureCollection('C_FeatureCollection')

        # Create reporting header
        if reporting_header == None:
            raise SchemaException("ReportingHeader cannot be empty")
        reporting_header.namespace = self.namespace
        reporting_header.prefix = "C"
        reporting_header.ids = ids
        reporting_header.language_code = self.language_code

        # Add Assessment Regimes to feature collection
        if assessmentregimes == None or len(assessmentregimes) == 0:
            raise SchemaException("Assessment regimes collection cannot be empty")

        for assessmentregime in assessmentregimes:
            ids.append(assessmentregime.id)
            assessmentregime.set_namespace(self.namespace)
            assessmentregime.set_language_code(self.language_code)
            assessmentregime.set_timezone_offset(timezone_offset)

            # Clean Assessmentmethods
            assessmentregime._assessmentmethods = []

            for assessmentmethod in assessmentmethods:
                if assessmentmethod.assessmentregime_id == assessmentregime.id:
                    assessmentregime.add_assessmentmethod(assessmentmethod)

            fc.add_assessmentregime(assessmentregime)

        # Add the reporting header to feature collection
        fc.add_responsible_reporter(reporting_header)

        return fc.as_element()

    #  Dataflow G (Attainment)
    def get_dataflow_g(self, reporting_header: ResponsibleReporter,
                       attainments: List[Attainment],
                       exceedancedescriptions: List[Exceedancedescription],
                       exceedingmethods: List[Exceedingmethod],
                       timezone_offset: int):

        ids = []
        fc = FeatureCollection('G_FeatureCollection')

        # Create reporting header
        if reporting_header == None:
            raise SchemaException("ReportingHeader cannot be empty")
        reporting_header.namespace = self.namespace
        reporting_header.prefix = "G"
        reporting_header.ids = ids
        reporting_header.language_code = self.language_code

        # Add Attainments to feature collection
        if attainments == None or len(attainments) == 0:
            raise SchemaException("Attainments collection cannot be empty")

        for attainment in attainments:
            ids.append(attainment.id)
            attainment.set_namespace(self.namespace)
            attainment.set_language_code(self.language_code)
            attainment.set_timezone_offset(timezone_offset)

            # Clean Exceedance Description
            attainment._exceedancedescriptions = []

            for exceedancedescription in exceedancedescriptions:
                # Clean Exceedingmethods
                exceedancedescription._exceedingmethods = []

                if exceedancedescription.attainment_id == attainment.id:
                    attainment.add_exceedancedescription(exceedancedescription)

                    for exceedingmethod in exceedingmethods:
                        if exceedingmethod.exceedancedescription_id == exceedancedescription.id:
                            exceedancedescription.add_exceedingmethod(exceedingmethod)

            fc.add_attainment(attainment)

        # Add the reporting header to feature collection
        fc.add_responsible_reporter(reporting_header)

        return fc.as_element()
