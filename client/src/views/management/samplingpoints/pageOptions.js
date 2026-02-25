const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: true,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "lookup", label: "Station", prop_id: "station_id", prop: "station", lookup: "stations", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Pollutant", prop_id: "pollutant_id", prop: "pollutant", required: true, lookup: "pollutants", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Time resolution", prop_id: "time_resolution_id", prop: "time_resolution", required: true, lookup: "time_resolutions", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Unit", prop_id: "unit_id", prop: "unit", required: true, lookup: "units", default: null, enableInEdit: true, showInGrid: true },
    { type: "checkbox", label: "Private", prop: "private", required: true, default: false, enableInEdit: true, showInGrid: true },
    { type: "checkbox", label: "Public api", prop: "use_in_public_api", required: true, default: false, enableInEdit: true, showInGrid: true },

    // OPTIONAL
    { type: "number", label: "Inlet height", prop: "inlet_height", placeholder: "num: Inlet height", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Building distance", prop: "building_distance", placeholder: "num: Building distance", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Kerb distance", prop: "kerb_distance", placeholder: "num: Kerb distance", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Emission source distance", prop: "emission_source_distance", placeholder: "num: Emission source distance", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Logger id", prop: "logger_id", placeholder: "str: Logger id for push functionality", required: false, default: null, enableInEdit: true, showInGrid: false }
  ],
  lookups: lookups
});

export default pageOptions;
