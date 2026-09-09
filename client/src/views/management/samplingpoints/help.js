// Hover documentation for the AQR3 attributes a sampling point carries.
//
// One module rather than text inline in each dialog: hotspot, supersite, the
// category, the coordinates and the four distances are all editable in two places
// -- the Crud form on this page, which sets the sampling point's default, and the
// per-period override in SamplingPointLocations.vue. spec.py:247 exports
// COALESCE(spl.<field>, sp.<field>), so the override wins; describing the same
// attribute differently in the two dialogs would be worse than not describing it.
//
// The wording comes from the guide's own Content and Remark columns -- the
// `Attributes` sheet of AQR3Schema_v502/R3_v502_AQ_Reporting_guide_v2 - June2026.xlsx,
// extracted to tests/fixtures/aqr3_v502_attributes.json -- with the Raven-specific
// consequence appended where there is one. unit/test_samplingpoints_help.py checks
// that the code each entry cites is really the attribute that field exports.
//
// Fields with no AQR3 attribute (Private, Public API, Time Resolution, Unit, Logger
// Id, Daily Check) have no entry: an info icon that only restates the label is worse
// than no icon.
//
// One entry per line, spread into a property declaration as `...HELP.hotspot`.

// ELI permalink, so it survives the OJ page being reorganised.
const AAQD = "https://eur-lex.europa.eu/eli/dir/2024/2881/oj/eng";

export const HELP = {
  // SPO -- the sampling point itself
  id: { help: "AQR3 SPO_02 AssessmentMethodId. The sampling point's identifier, chosen here. Everything else in the submission references it — SamplingPointLocation, SamplingProcess and ComplianceAssessmentMethod all key on it — so it cannot be changed once reported. A point is closed by ending its process, and reopened by adding a new one." },
  station: { help: "AQR3 SPO_05 StationEoICode. The station this point belongs to. The EoI code must always be present and cannot be modified; a station goes inactive when all of its sampling points are." },
  pollutant: { help: "AQR3 SPO_04 PollutantId. The pollutant measured, from the EEA pollutant vocabulary. One pollutant per sampling point — a second pollutant needs a second point." },
  sampling_point_reference_id: { help: "AQR3 SPO_03 SamplingPointReferenceId. Reference code following the SPO reference rules, unique within the reporting country. It can serve as a code list of its own." },

  // SPL -- the location characteristics, which are per period
  from_time: { help: "AQR3 SPL_03 LocationBegin. Start of this location's characteristics, and part of the AQR3 key. Left empty, SamplingPointLocation.csv reports a blank mandatory column. Per-period overrides live in the Locations dialog." },
  to_time: { help: "AQR3 SPL_04 LocationEnd. End of this location's characteristics. Empty means the location is still current." },
  station_area: { help: "AQR3 SPL_05 StationArea. Classification of the station's surroundings — urban, suburban, rural and so on. The guide warns that changing it means closing the sampling points and declaring a new station." },
  sampling_point_category: { help: "AQR3 SPL_06 SamplingPointCategory. Why the sampling point was placed. The guide lists traffic, background, industrial, port, airport, residential heating and multisource.\nEEA's provisional QC pairs this with Hotspot: a background site is expected not to be a hotspot." },
  hotspot: { help: "AQR3 SPL_07 Hotspot. Whether this sampling point sits at an air pollution hotspot — in the directive's sense, a location in the zone with the highest concentrations the population is exposed to, over a period significant against the averaging period of the limit value.\nSet here it is the sampling point's default; Locations can override it for a period, and the export prefers the override.\nDirective (EU) 2024/2881, Art. 4(27) — click to open.", helpHref: AAQD },
  supersite: { help: "AQR3 SPL_08 Supersite. Whether the site is classified as a “super site” for advanced monitoring." },
  latitude: { help: "AQR3 SPL_09 Latitude. Decimal degrees. The export quantises to four decimals, the scale AQR3 declares." },
  longitude: { help: "AQR3 SPL_10 Longitude. Decimal degrees. The export quantises to four decimals, the scale AQR3 declares." },
  altitude: { help: "AQR3 SPL_11 Altitude. Metres above sea level." },
  inlet_height: { help: "AQR3 SPL_12 InletHeight. Height of the sampling inlet above ground, in metres." },
  building_distance: { help: "AQR3 SPL_13 BuildingDistance. Horizontal distance from the inlet to the nearest building, in metres." },
  kerb_distance: { help: "AQR3 SPL_14 KerbDistance. Horizontal distance from the inlet to the nearest road kerb, in metres." },
  emission_source_distance: { help: "AQR3 SPL_15 EmissionSourceDistance. Horizontal distance from the main emission source, in metres." }
};

export default HELP;
