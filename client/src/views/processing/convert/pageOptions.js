const pageOptions = (lookups) => ({
  properties: [
    // Display-only fields
    { type: "gridOnly", label: "Station", prop: "station", showInGrid: true },
    { type: "gridOnly", label: "Pollutant/Meteo", prop: "pollutant", showInGrid: true },
    { type: "gridOnly", label: "Timestep", prop: "timestep", showInGrid: true },

    // { type: "text", label: "Id", prop: "id", required: true, default: null, enableInEdit: false, showInGrid: false },
    { type: "lookup", label: "Timeseries", prop_id: "sampling_point_id", prop: "sampling_point_id", lookup: "timeseries", required: true, default: null, enableInEdit: false, showInGrid: false },
    { type: "lookup", label: "From unit", prop_id: "source_id", prop: "source", lookup: "units", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "To unit", prop_id: "target_id", prop: "target", lookup: "units", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "number", label: "Factor", prop: "factor", placeholder: "Factor to convert unit", required: true, default: null, enableInEdit: true, showInGrid: true }
  ],
  lookups: lookups
});

export default pageOptions;
