const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "text", label: "Code", prop: "code", placeholder: "str: A unique code", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "Name", prop: "name", placeholder: "str: Name of zone", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "number", label: "Area (km²)", prop: "area", placeholder: "float: Area in km2", required: true, default: null, enableInEdit: true, showInGrid: true },
    
    { type: "lookup", label: "Type", prop_id: "zone_type_id", prop: "zone_type", lookup: "zone_types", required: false, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Category", prop_id: "zone_category_id", prop: "zone_category", lookup: "zone_categories", required: false, default: null, enableInEdit: true, showInGrid: true },

    { type: "custom", label: "Geometry (GeoJSON)", prop: "geojson", showInGrid: false, hideInPicker: true, required: true, enableInEdit: true }
  ],
  lookups: lookups
});

export default pageOptions;
