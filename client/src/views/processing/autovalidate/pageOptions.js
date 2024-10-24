const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED
    { type: "lookup", label: "Pollutant/Meteo", prop_id: "pollutant_id", prop: "pollutant", lookup: "pollutants", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "number", label: "Minimum", prop: "min", placeholder: "float: Minimum valid value", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "number", label: "Maximum", prop: "max", placeholder: "float: Maximum valid value", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "number", label: "Repeat", prop: "rep", placeholder: "int: Maximum number of repeats", required: true, default: null, enableInEdit: true, showInGrid: true }
  ],
  lookups: lookups
});

export default pageOptions;
