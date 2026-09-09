import { HELP } from "./help.js";

const pageOptions = (lookups) => ({
  entityName: "Sampling Point",
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", ...HELP.id, required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "lookup", label: "Station", prop_id: "station_id", prop: "station", lookup: "stations", ...HELP.station, required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Pollutant", prop_id: "pollutant_id", prop: "pollutant", ...HELP.pollutant, required: true, lookup: "pollutants", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Time Resolution", prop_id: "time_resolution_id", prop: "time_resolution", required: true, lookup: "time_resolutions", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Unit", prop_id: "unit_id", prop: "unit", required: true, lookup: "units", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Category", prop_id: "sampling_point_category_id", prop: "sampling_point_category", lookup: "sampling_point_categories", ...HELP.sampling_point_category, required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "checkbox", label: "Private", prop: "private", required: true, default: false, enableInEdit: true, showInGrid: true },
    { type: "checkbox", label: "Public API", prop: "use_in_public_api", required: true, default: false, enableInEdit: true, showInGrid: true },
    { type: "number", label: "Inlet Height", prop: "inlet_height", placeholder: "num: Inlet height in metres", ...HELP.inlet_height, required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Building Distance", prop: "building_distance", placeholder: "num: Building distance in metres", ...HELP.building_distance, required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Kerb Distance", prop: "kerb_distance", placeholder: "num: Kerb distance in metres", ...HELP.kerb_distance, required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Emission Source Distance", prop: "emission_source_distance", placeholder: "num: Emission source distance in metres", ...HELP.emission_source_distance, required: true, default: null, enableInEdit: true, showInGrid: false },

    // OPTIONAL
    { type: "text", label: "Reference Id", prop: "sampling_point_reference_id", placeholder: "str: SPOref_<StationEoICode>_<PollutantId>_<idx>", ...HELP.sampling_point_reference_id, required: false, default: null, enableInEdit: true, showInGrid: false },
    // Active period. from_time is the default AQR3 SPL_03 LocationBegin, which is
    // part of the AQR3 key — left empty, SamplingPointLocation.csv reports a blank
    // mandatory column. Per-period overrides live in the Locations dialog.
    { type: "eeaDatetime", label: "Active From", prop: "from_time", ...HELP.from_time, required: false, default: null, enableInEdit: true, showInGrid: true },
    { type: "eeaDatetime", label: "Active To", prop: "to_time", ...HELP.to_time, required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "checkbox", label: "Hotspot", prop: "hotspot", ...HELP.hotspot, required: false, default: false, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Logger Id", prop: "logger_id", placeholder: "str: Logger id for push functionality", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "checkbox", label: "Daily Check", prop: "daily_check", required: false, default: false, enableInEdit: true, showInGrid: false }
  ],
  lookups: lookups
});

export default pageOptions;
