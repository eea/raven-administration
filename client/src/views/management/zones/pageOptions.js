const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "text", label: "Code", prop: "code", placeholder: "str: A unique code", required: true, default: null, enableInEdit: false, showInGrid: true },

    { type: "text", label: "Name", prop: "name", placeholder: "str: Name of zone", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "number", label: "Year", prop: "year", placeholder: "int: The year zone is added", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "number", label: "Area", prop: "area", placeholder: "float: Area in km2", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "number", label: "Population", prop: "population", placeholder: "int: Population of zone", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "number", label: "Population year", prop: "population_year", placeholder: "int: The year of population count", required: true, default: null, enableInEdit: true, showInGrid: true },

    { type: "lookup", label: "Type", prop_id: "zone_type_id", prop: "zone_type", lookup: "zone_types", required: true, default: null, enableInEdit: true, showInGrid: true },

    { type: "lookup", label: "Authority", prop_id: "authority_id", prop: "authority", required: true, lookup: "authorities", default: null, enableInEdit: true, showInGrid: true },

    { type: "custom", label: "Preview", prop: "geojson", showInGrid: false, hideInPicker: true, required: true, enableInEdit: true }
  ],
  lookups: lookups
});

export default pageOptions;
