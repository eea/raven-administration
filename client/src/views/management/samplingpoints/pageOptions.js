const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: true,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },

    { type: "lookup", label: "Station", prop_id: "station_id", prop: "station", lookup: "stations", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Pollutant/Meteo", prop_id: "pollutant_id", prop: "pollutant", required: true, lookup: "pollutants", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Timestep", prop_id: "timestep_id", prop: "timestep", required: true, lookup: "timesteps", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Concentration", prop_id: "concentration_id", prop: "concentration", required: true, lookup: "concentrations", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Station classification", prop_id: "station_classification_id", prop: "station_classification", required: true, lookup: "stationclassifications", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Media monitored", prop_id: "media_id", prop: "media", required: true, lookup: "media", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Measurement regime", prop_id: "measurement_regime_id", prop: "measurement_regime", required: true, lookup: "measurementregimes", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Assessment types", prop_id: "assessment_type_id", prop: "assessment_type", required: true, lookup: "assessmenttypes", default: null, enableInEdit: true, showInGrid: false },

    { type: "eeaDatetime", label: "Begin", prop: "begin_position", required: true, default: null, enableInEdit: true, showInGrid: false },

    { type: "checkbox", label: "Mobile", prop: "mobile", required: true, default: false, enableInEdit: true, showInGrid: false },
    { type: "checkbox", label: "Private", prop: "private", required: true, default: false, enableInEdit: true, showInGrid: true },
    { type: "checkbox", label: "Public api", prop: "use_in_public_api", required: true, default: false, enableInEdit: true, showInGrid: true },

    // OPTIONAL
    { type: "text", label: "Logger id", prop: "logger_id", placeholder: "str: Logger id for push functionality", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Main emission sources", prop: "main_emission_sources", placeholder: "str: Main Emission Sources", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Change aei stations", prop: "change_aei_stations", placeholder: "str: Change aei stations", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Distance source", prop: "distance_source", placeholder: "str:  Distance source", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Industrial emissions", prop: "industrial_emissions", placeholder: "str:  Industrial emissions", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Heating emissions", prop: "heating_emissions", placeholder: "str:  Heating emissions", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Traffic emissions", prop: "traffic_emissions", placeholder: "str:  Traffic emissions", required: false, default: null, enableInEdit: true, showInGrid: false },

    { type: "eeaDatetime", label: "End", prop: "end_position", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "checkbox", label: "Used aqd", prop: "used_aqd", required: false, default: false, enableInEdit: true, showInGrid: false }
  ],
  lookups: lookups
});

export default pageOptions;
