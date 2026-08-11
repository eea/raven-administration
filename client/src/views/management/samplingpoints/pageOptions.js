const pageOptions = (lookups) => ({
  entityName: "Sampling Point",
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "lookup", label: "Station", prop_id: "station_id", prop: "station", lookup: "stations", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Pollutant", prop_id: "pollutant_id", prop: "pollutant", required: true, lookup: "pollutants", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Time Resolution", prop_id: "time_resolution_id", prop: "time_resolution", required: true, lookup: "time_resolutions", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Unit", prop_id: "unit_id", prop: "unit", required: true, lookup: "units", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Category", prop_id: "sampling_point_category_id", prop: "sampling_point_category", lookup: "sampling_point_categories", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "checkbox", label: "Private", prop: "private", required: true, default: false, enableInEdit: true, showInGrid: true },
    { type: "checkbox", label: "Public API", prop: "use_in_public_api", required: true, default: false, enableInEdit: true, showInGrid: true },
    { type: "number", label: "Inlet Height", prop: "inlet_height", placeholder: "num: Inlet height in metres", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Building Distance", prop: "building_distance", placeholder: "num: Building distance in metres", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Kerb Distance", prop: "kerb_distance", placeholder: "num: Kerb distance in metres", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Emission Source Distance", prop: "emission_source_distance", placeholder: "num: Emission source distance in metres", required: true, default: null, enableInEdit: true, showInGrid: false },

    // OPTIONAL
    { type: "text", label: "Reference Id", prop: "sampling_point_reference_id", placeholder: "str: SPOref_<StationEoICode>_<PollutantId>_<idx>", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "checkbox", label: "Hotspot", prop: "hotspot", required: false, default: false, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Logger Id", prop: "logger_id", placeholder: "str: Logger id for push functionality", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "checkbox", label: "Daily Check", prop: "daily_check", required: false, default: false, enableInEdit: true, showInGrid: false }
  ],
  lookups: lookups
});

export default pageOptions;
