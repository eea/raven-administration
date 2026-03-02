const pageOptions = (lookups) => ({
  entityName: "Station",
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "text", label: "EOI code", prop: "eoi_code", placeholder: "str: EOI code", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "Name", prop: "name", placeholder: "str: Name of station", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "National code", prop: "national_code", placeholder: "str: National station code", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Latitude", prop: "latitude", placeholder: "float: Latitude", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Longitude", prop: "longitude", placeholder: "float: Longitude", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Altitude", prop: "altitude", placeholder: "float: Altitude (meters)", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "checkbox", label: "Supersite", prop: "supersite", required: true, default: false, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Area classification", prop: "area_classification", prop_id: "area_classification_id", lookup: "areaclassifications", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Network", prop: "network", prop_id: "network_id", lookup: "networks", required: true, default: null, enableInEdit: true, showInGrid: true }
  ],
  lookups: lookups
});

export default pageOptions;
