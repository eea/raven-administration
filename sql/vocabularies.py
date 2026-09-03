"""Registry of the EEA vocabularies that AQR3 v5.02 reporting depends on.

Kept separate from `populate_vocabularies.py` so tests can import the registry
without pulling in psycopg2 or touching the network.

The v5.02 CSVs are largely codelist values — `MeasurementType`, `AuthorityRole`,
`Validity`, `SamplingPointCategory`, `ObjectiveType`, `DataTable` and a dozen
more all read `eea_*.notation`. An empty vocabulary table is a blank CSV column,
so this registry is effectively part of the reporting contract.

Vocabulary URLs are a path suffix, not a query parameter:

    https://dd.eionet.europa.eu/vocabulary/<collection>/<vocabulary>/rdf
    https://dd.eionet.europa.eu/vocabulary/<collection>/<vocabulary>/csv

`id_from` matters because the three conventions genuinely differ:

    notation            id = skos:notation           most aq/* vocabularies
    uri_suffix          id = last URI segment        where the notation is not URL-safe
                                                     (uom/concentration notation is 'µg/m3')
                                                     or is a short code (datatable notation is 'ARZ')
    numeric_uri_suffix  id = int(last URI segment)   pollutants and meteoparameters

`notation_from` exists because one vocabulary supplies no notation at all. When
skos:notation is absent the parser falls back to the URI's last segment, which is
usually the right answer — but for aq/meteoparameter that segment is a bare number
('51', '52', ...). Every display in Raven reads
`COALESCE(NULLIF(notation, ''), label)`, precisely so a vocabulary without a notation
falls through to its label; a synthesised numeric notation defeats that and the UI
shows "51" instead of "Wind velocity". `notation_from='label'` stores the label as
the notation, which is what sql/meteo.sql — the offline seed for these same concepts —
does too, so the two produce identical rows.
"""
from dataclasses import dataclass, field
from typing import Tuple

DD_BASE = 'https://dd.eionet.europa.eu/vocabulary'


@dataclass(frozen=True)
class Vocabulary:
    """One EEA vocabulary and the table it populates."""
    table: str
    path: str                          # '<collection>/<vocabulary>'
    aqr3: str = ''                     # attribute code(s) this feeds, for the summary
    id_from: str = 'notation'          # notation | uri_suffix | numeric_uri_suffix
    notation_from: str = 'notation'    # notation | label
    fmt: str = 'rdf'                   # rdf | csv
    prefer: Tuple[str, ...] = ()       # try these paths first (recast before base)
    fallback: Tuple[dict, ...] = ()     # used only when every fetch attempt fails
    fallback_note: str = ''            # why the fallback exists / how trustworthy it is
    also_into: Tuple[str, ...] = ()    # extra legacy tables fed the same rows

    @property
    def url(self):
        return f'{DD_BASE}/{self.path}/{self.fmt}'

    def urls(self):
        """Every path to try, in order."""
        return [f'{DD_BASE}/{p}/{self.fmt}' for p in (*self.prefer, self.path)]


def _rows(*triples):
    """(id, label, notation) tuples -> row dicts, uri derived from the vocabulary."""
    return tuple({'id': i, 'label': l, 'notation': n} for i, l, n in triples)


# ---------------------------------------------------------------------------
# Fallbacks
#
# Only for vocabularies that do not resolve. Every value here is sourced from
# something authoritative in this repository or the reporting guide — nothing is
# invented, because a wrong EEA code fails Reportnet3 QC in a way that is much
# harder to diagnose than an empty column. Each is reported as a fallback and
# makes the loader exit non-zero.
# ---------------------------------------------------------------------------

# SPL_06. `aq/spocategory` 500s; `aq/samplingpointcategory` is the correct name and
# does resolve, so this is only a safety net. Values are the guide's own list:
# "Potential categories: traffic, background, industrial, port, airport,
# residential heating, multisource."
SPO_CATEGORY_FALLBACK = _rows(
    ('traffic', 'Traffic', 'traffic'),
    ('background', 'Background', 'background'),
    ('industrial', 'Industrial', 'industrial'),
    ('port', 'Port', 'port'),
    ('airport', 'Airport', 'airport'),
    ('residentialheating', 'Residential heating', 'residentialheating'),
    ('multisource', 'Multisource', 'multisource'),
)

# AUT_05. Guide: "Name of the authority instance: zone, network, nuts0, nuts1,
# nuts2, nuts3, station, SPO... - new code list".
AUTHORITY_INSTANCE_FALLBACK = _rows(
    ('zone', 'Zone', 'zone'),
    ('network', 'Network', 'network'),
    ('nuts0', 'NUTS level 0', 'nuts0'),
    ('nuts1', 'NUTS level 1', 'nuts1'),
    ('nuts2', 'NUTS level 2', 'nuts2'),
    ('nuts3', 'NUTS level 3', 'nuts3'),
    ('station', 'Station', 'station'),
    ('SPO', 'Sampling point', 'SPO'),
)

# AUT_10. Guide: "Status or classification of the authority (e.g., active/inactive)".
AUTHORITY_STATUS_FALLBACK = _rows(
    ('active', 'Active', 'active'),
    ('inactive', 'Inactive', 'inactive'),
)

# AUT_03. `aq/authorityobject` returns HTTP 500 persistently. The guide only says
# "A general object identifier or classification (topic e.g. reporting, assessment
# etc.)" — so this fallback is the weakest of the set and needs confirming with EEA.
# Note the guide's own Authority example sheet uses numeric AuthorityRole values
# ("1", "2"), which contradicts the varchar(50) + vocabulary declaration.
AUTHORITY_ROLE_FALLBACK = _rows(
    ('reporting', 'Reporting', 'reporting'),
    ('assessment', 'Assessment', 'assessment'),
)

# DOC_03. `aq/documentobject` returns HTTP 500. Values from schema.sql's own comment:
# "Document object types for AUTH reporting - AQD, Classificationreport, etc."
DOCUMENT_OBJECT_FALLBACK = _rows(
    ('AQD', 'Air Quality Directive report', 'AQD'),
    ('Classificationreport', 'Classification report', 'Classificationreport'),
)

# DOC_02. Values from schema.sql's comment: "Data table types - samplingprocess,
# model, assessmentregimezone, planscenario", extended with the other v5.02 tables
# that carry a DocumentId attribute.
DATA_TABLE_FALLBACK = _rows(
    ('samplingprocess', 'SamplingProcess', 'SPP'),
    ('model', 'ModelObjectiveEstimation', 'MOE'),
    ('assessmentregimezone', 'AssessmentRegimeZone', 'ARZ'),
    ('planscenario', 'PlanScenario', 'PSC'),
    ('network', 'MeasurementStation / network', 'STA'),
    ('sourceapportionment', 'SourceApportionment', 'SAP'),
    ('pollutionleveladjustment', 'PollutionLevelAdjustment', 'ADJ'),
)

# MOE_06 / SRS_05. Guide: "Encoding method used for model results ('zone',
# 'internal' or 'external')". Note this corrects an earlier assumption of
# inline/external — the AQR3 table is named MOEResultInline but the codelist value
# is 'internal', and 'zone' is a third option for per-zone rather than gridded results.
RESULT_ENCODING_FALLBACK = _rows(
    ('zone', 'Aggregated per zone', 'zone'),
    ('internal', 'Inline grid cells in the CSV', 'internal'),
    ('external', 'Attached GEOTIFF', 'external'),
)

# MOE_07. Guide: "Purpose of the model application (e.g., assessment, adjustment,
# scenario, spatial representativeness)".
MODEL_APPLICATION_FALLBACK = _rows(
    ('assessment', 'Assessment', 'assessment'),
    ('adjustment', 'Adjustment', 'adjustment'),
    ('scenario', 'Scenario', 'scenario'),
    ('representativeness', 'Spatial representativeness', 'representativeness'),
)

# MRI_12 / MRE_09 / SRI_05 / SRE_03. Guide Introduction: the common grid uses
# "recommended resolution steps (10, 100, 1000, 10000 m)".
SPATIAL_RESOLUTION_FALLBACK = _rows(
    ('10', '10 m', '10'),
    ('100', '100 m', '100'),
    ('1000', '1000 m', '1000'),
    ('10000', '10000 m', '10000'),
)

# SRS_04. Guide: "New code list (SPO representativeness area, exceedance extent area)".
SR_APPLICATION_FALLBACK = _rows(
    ('spo_sr', 'Sampling point representativeness area', 'spo_sr'),
    ('exc_sr', 'Exceedance extent area', 'exc_sr'),
)

# OMR_08 / OMR_09. Documented in schema.sql's comments on
# observations.observationvalidity_id and .observationverification_id.
OBSERVATION_VALIDITY_FALLBACK = _rows(
    (-99, 'Not valid due to station maintenance or calibration', '-99'),
    (-1, 'Not valid', '-1'),
    (1, 'Valid', '1'),
    (2, 'Valid, below detection limit', '2'),
    (3, 'Valid, below detection limit and value substituted', '3'),
    (4, 'Valid, ozone CCQM comparison', '4'),
)
OBSERVATION_VERIFICATION_FALLBACK = _rows(
    (1, 'Verified', '1'),
    (2, 'Preliminary verified', '2'),
    (3, 'Not verified', '3'),
)

# ARZ_06. Guide: "Category of the air quality zone (aq zone or nuts) - new code list".
ZONE_CATEGORY_FALLBACK = _rows(
    ('zone', 'Air quality zone', 'zone'),
    ('nuts', 'NUTS region', 'nuts'),
)

# MOE_03 / MRI_04 / CAM_04. From the aggregation processes already hardcoded in
# raven-rn3-db/populate_lookups_v4.py and used by plans_programs_export.py ('P1Y').
# The real vocabulary is much larger (summer-avg, winter-avg, percentiles, …), so
# this is a floor, not a substitute — hence it still trips the non-zero exit.
AGGREGATION_PROCESS_FALLBACK = _rows(
    ('P1D', 'Daily mean', 'P1D'),
    ('P1Y', 'Annual mean', 'P1Y'),
    ('P1Y-dmax', 'Annual maximum of daily means', 'P1Y-dmax'),
    ('P1Y-8hmax', 'Annual maximum of 8-hour means', 'P1Y-8hmax'),
    ('AOT40', 'AOT40', 'AOT40'),
)

# CountryCode, the first column of every AQR3 table. Needed offline because
# settings.country_code_id has a FK to this table — with it empty you cannot set
# the reporting country at all, which blocks the whole export.
#
# These are ISO-3166-1 alpha-2 codes for the EEA reporting countries: stable,
# externally verifiable, and a different kind of claim from guessing at EEA
# codelist semantics. Note the EEA uses GB (not UK) and GR (not EL).
COUNTRY_FALLBACK = _rows(
    ('AD', 'Andorra', 'AD'), ('AL', 'Albania', 'AL'), ('AT', 'Austria', 'AT'),
    ('BA', 'Bosnia and Herzegovina', 'BA'), ('BE', 'Belgium', 'BE'),
    ('BG', 'Bulgaria', 'BG'), ('CH', 'Switzerland', 'CH'), ('CY', 'Cyprus', 'CY'),
    ('CZ', 'Czechia', 'CZ'), ('DE', 'Germany', 'DE'), ('DK', 'Denmark', 'DK'),
    ('EE', 'Estonia', 'EE'), ('ES', 'Spain', 'ES'), ('FI', 'Finland', 'FI'),
    ('FR', 'France', 'FR'), ('GB', 'United Kingdom', 'GB'), ('GE', 'Georgia', 'GE'),
    ('GI', 'Gibraltar', 'GI'), ('GR', 'Greece', 'GR'), ('HR', 'Croatia', 'HR'),
    ('HU', 'Hungary', 'HU'), ('IE', 'Ireland', 'IE'), ('IS', 'Iceland', 'IS'),
    ('IT', 'Italy', 'IT'), ('LI', 'Liechtenstein', 'LI'), ('LT', 'Lithuania', 'LT'),
    ('LU', 'Luxembourg', 'LU'), ('LV', 'Latvia', 'LV'), ('MD', 'Moldova', 'MD'),
    ('ME', 'Montenegro', 'ME'), ('MK', 'North Macedonia', 'MK'), ('MT', 'Malta', 'MT'),
    ('NL', 'Netherlands', 'NL'), ('NO', 'Norway', 'NO'), ('PL', 'Poland', 'PL'),
    ('PT', 'Portugal', 'PT'), ('RO', 'Romania', 'RO'), ('RS', 'Serbia', 'RS'),
    ('SE', 'Sweden', 'SE'), ('SI', 'Slovenia', 'SI'), ('SK', 'Slovakia', 'SK'),
    ('SM', 'San Marino', 'SM'), ('TR', 'Türkiye', 'TR'), ('UA', 'Ukraine', 'UA'),
    ('XK', 'Kosovo', 'XK'),
)


# ---------------------------------------------------------------------------
# The registry
# ---------------------------------------------------------------------------

VOCABULARIES = (
    # -- identity / geography ------------------------------------------------
    Vocabulary('eea_countries', 'common/countries', aqr3='CountryCode (all tables)',
               fallback=COUNTRY_FALLBACK,
               fallback_note='ISO-3166-1 alpha-2 for the EEA reporting countries; needed '
                             'offline because settings.country_code_id has a FK here'),

    # -- Authority (AUT) ----------------------------------------------------
    Vocabulary('eea_authorityobject', 'aq/authorityobject', aqr3='AUT_03 AuthorityRole',
               fallback=AUTHORITY_ROLE_FALLBACK,
               fallback_note='vocabulary returns HTTP 500; values inferred from the guide '
                             'description only - confirm with EEA'),
    Vocabulary('eea_authorityinstance', 'aq/authorityinstance', aqr3='AUT_05 AuthorityInstance',
               fallback=AUTHORITY_INSTANCE_FALLBACK,
               fallback_note='values listed verbatim in the guide description'),
    Vocabulary('eea_authoritystatus', 'aq/authoritystatus', aqr3='AUT_10 AuthorityStatus',
               fallback=AUTHORITY_STATUS_FALLBACK,
               fallback_note='values listed in the guide description'),

    # -- MeasurementStation (STA) ------------------------------------------
    Vocabulary('eea_administrativelevels', 'aq/administrativelevel',
               aqr3='STA_05 NetworkOrganisationalLevel'),
    Vocabulary('eea_timezones', 'aq/timezone', aqr3='STA_06 Timezone'),

    # -- SamplingPoint / location (SPO, SPL) -------------------------------
    Vocabulary('eea_pollutants', 'aq/pollutant', aqr3='PollutantId (most tables)',
               id_from='numeric_uri_suffix'),
    # Meteoparameters share eea_pollutants' id space by design (ids start at 51).
    # notation_from='label': this vocabulary ships an empty skos:notation for every
    # concept but 51, so the URI-suffix fallback would store '51', '52', ... as the
    # notation - and notation wins the COALESCE every display uses. See the module
    # docstring. 1,542 sampling points read as bare integers before this.
    Vocabulary('eea_pollutants', 'aq/meteoparameter', aqr3='PollutantId (meteo parameters)',
               id_from='numeric_uri_suffix', notation_from='label'),
    Vocabulary('eea_areaclassifications', 'aq/areaclassification', aqr3='SPL_05 StationArea'),
    Vocabulary('eea_spocategory', 'aq/samplingpointcategory', aqr3='SPL_06 SamplingPointCategory',
               fallback=SPO_CATEGORY_FALLBACK,
               fallback_note='note the vocabulary is samplingpointcategory, not spocategory '
                             '(which 500s); values from the guide remark'),

    # -- SamplingProcess (SPP) ---------------------------------------------
    Vocabulary('eea_measurementtypes', 'aq/measurementtype', aqr3='SPP_07 MeasurementType'),
    Vocabulary('eea_measurementmethods', 'aq/measurementmethod', aqr3='SPP_08 Method'),
    Vocabulary('eea_measurementequipments', 'aq/measurementequipment', aqr3='SPP_09 Equipment'),
    Vocabulary('eea_analyticaltechnique', 'aq/analyticaltechnique', aqr3='SPP_10 AnalyticalTechnique'),
    Vocabulary('eea_equivalencedemonstrated', 'aq/equivalencedemonstrated',
               aqr3='SPP_11 EquivalenceDemonstrated'),

    # -- Model / objective estimation (MOE, MRI, MRE) ----------------------
    Vocabulary('eea_aggregationprocess', 'aq/aggregationprocess',
               aqr3='MOE_03 / MRI_04 / CAM_04 DataAggregationProcessId',
               fallback=AGGREGATION_PROCESS_FALLBACK,
               fallback_note='partial: the real vocabulary is much larger (percentiles, '
                             'seasonal means) - fetch from EEA before reporting'),
    Vocabulary('eea_resultencoding', 'aq/resultencoding', aqr3='MOE_06 / SRS_05 ResultEncoding',
               fallback=RESULT_ENCODING_FALLBACK,
               fallback_note="guide gives 'zone', 'internal', 'external'"),
    Vocabulary('eea_modelapplication', 'aq/modelapplication', aqr3='MOE_07 MethodApplication',
               fallback=MODEL_APPLICATION_FALLBACK,
               fallback_note='values from the guide description'),
    Vocabulary('eea_spatialresolution', 'aq/spatialresolution',
               aqr3='MRI_12 / MRE_09 / SRI_05 / SRE_03 SpatialResolution',
               fallback=SPATIAL_RESOLUTION_FALLBACK,
               fallback_note='grid steps from the guide Introduction sheet'),

    # -- Observations (OMR) ------------------------------------------------
    Vocabulary('eea_concentrations', 'uom/concentration', aqr3='OMR_07 Unit',
               id_from='uri_suffix'),
    Vocabulary('eea_observationvalidity', 'aq/observationvalidity', aqr3='OMR_08 Validity',
               fallback=OBSERVATION_VALIDITY_FALLBACK,
               fallback_note='documented in schema.sql on observations.observationvalidity_id'),
    Vocabulary('eea_observationverification', 'aq/observationverification',
               aqr3='OMR_09 Verification',
               fallback=OBSERVATION_VERIFICATION_FALLBACK,
               fallback_note='documented in schema.sql on observations.observationverification_id'),
    Vocabulary('eea_times', 'aq/primaryObservation', aqr3='OMR_11 TimeResolution'),

    # -- Zones and assessment regimes (ZGE, ARZ) ---------------------------
    Vocabulary('eea_zonecategory', 'aq/zonecategory', aqr3='ARZ_06 ZoneCategory',
               fallback=ZONE_CATEGORY_FALLBACK,
               fallback_note='values from the guide description (aq zone or nuts)'),
    Vocabulary('eea_zonetypes', 'aq/zonetype', aqr3='ARZ_07 ZoneType'),
    Vocabulary('eea_protectiontargets', 'aq/protectiontarget', aqr3='ARZ_10 ProtectionTarget'),
    # The FK from assessment_regimes.objective_type_id points at eea_objectivetypes,
    # which is what the ARZ export joins. The pre-existing loader filled the
    # similarly-named eea_objecttypes instead, leaving ObjectiveType blank in the CSV.
    # eea_objecttypes is still fed here because the XML export and the objecttypes
    # lookup endpoint reference it.
    Vocabulary('eea_objectivetypes', 'aq/objectivetype', aqr3='ARZ_11 ObjectiveType',
               also_into=('eea_objecttypes',)),
    Vocabulary('eea_reportingmetrics', 'aq/reportingmetric', aqr3='ARZ_12 ReportingMetric'),
    Vocabulary('eea_assessmentthresholdexceedances', 'aq/assessmentthresholdexceedance',
               aqr3='ARZ_13 AssessmentThresholdExceedance'),

    # -- Compliance (CAM) --------------------------------------------------
    Vocabulary('eea_assessmenttypes', 'aq/assessmenttype', aqr3='CAM_07 AssessmentType'),
    Vocabulary('eea_exceedancereason', 'aq/exceedancereason', aqr3='CAM_17 PreliminaryReason'),

    # -- Spatial representativeness (SRS) ----------------------------------
    Vocabulary('eea_srapplication', 'aq/SRapplication', aqr3='SRS_04 SRSApplication',
               fallback=SR_APPLICATION_FALLBACK,
               fallback_note='values from the guide remark'),

    # -- Adjustments (ADJ) -------------------------------------------------
    Vocabulary('eea_adjustmentsourcetype', 'aq/adjustmentsourcetype', aqr3='ADJ_03 AdjustmentSource'),

    # -- Documentation (DOC) -----------------------------------------------
    Vocabulary('eea_datatable', 'aq/datatable', aqr3='DOC_02 DataTable', id_from='uri_suffix',
               fallback=DATA_TABLE_FALLBACK,
               fallback_note='values from the schema.sql table comment'),
    Vocabulary('eea_documentobject', 'aq/documentobject', aqr3='DOC_03 DocumentType',
               fallback=DOCUMENT_OBJECT_FALLBACK,
               fallback_note='vocabulary returns HTTP 500; values from the schema.sql '
                             'table comment - likely incomplete'),

    # -- Environmental objectives ------------------------------------------
    # AQR3 v5.02 is the AAQD 2024/2881 recast, so prefer the recast vocabulary and
    # fall back to the original. CSV because the RDF omits the threshold columns.
    Vocabulary('eea_environmentalobjective', 'aq/environmentalobjective',
               aqr3='assessmentregime_zones.environmental_objective_id',
               fmt='csv', id_from='numeric_uri_suffix',
               prefer=('aq/environmentalobjective2024recast',)),

    # -- Raven-internal / legacy, not AQR3 attributes -----------------------
    Vocabulary('eea_stationclassifications', 'aq/stationclassification'),
    Vocabulary('eea_adjustmenttypes', 'aq/adjustmenttype'),
    Vocabulary('eea_measurementregimevalues', 'aq/measurementregime'),
    Vocabulary('eea_mediavalues', 'common/mediavalue'),
    Vocabulary('eea_processtypevalues', 'aq/processtype'),
    Vocabulary('eea_resultnaturevalues', 'aq/resultnature'),
)


# eea_times carries an extra `timestep` column (seconds). Unknown notations get 1,
# matching the pre-existing loader so aggregation behaviour does not change.
TIMESTEP_SECONDS = {
    'hour': 3600, 'day': 86400, 'week': 604800, 'fortnight': 1209600,
    'month': 2592000, 'quarter': 7776000, 'year': 31536000,
    'var': 1, 'dc': 1, 'n-hour': 1,
}


# Vocabularies the reporting guide references that this loader deliberately does
# not handle. Listed explicitly so the completeness test can tell "out of scope"
# from "forgotten".
OUT_OF_SCOPE = {
    'aq/PNSDinversion': 'OMP (PNSD) is deferred - the guide example is still "to be developed"',
    'aq/contributiontype': 'SAP - raven-plan-program owns the plans and programmes tables',
    'aq/sourcesectors': 'SAP / MEA - raven-plan-program',
    'aq/spatialscale': 'SAP / MEA - raven-plan-program',
    'aq/plancategory': 'CPL - raven-plan-program',
    'aq/scenariocategory': 'PSC / SME - raven-plan-program',
    'aq/measureclassification': 'MEA - raven-plan-program',
    'aq/measuretype': 'MEA - raven-plan-program',
    'aq/measureimplementationstatus': 'MEA - raven-plan-program',
    'aq/reasonifmeasurenotused': 'MEA - raven-plan-program',
}


def by_table():
    """table -> [Vocabulary]. A table can have several sources (eea_pollutants)."""
    out = {}
    for v in VOCABULARIES:
        out.setdefault(v.table, []).append(v)
    return out


def target_tables():
    """Every table this loader writes to, including `also_into` legacy duplicates."""
    tables = set()
    for v in VOCABULARIES:
        tables.add(v.table)
        tables.update(v.also_into)
    return tables
