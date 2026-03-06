const pageOptions = (lookups) => ({
  entityName: "Network",
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "text", label: "Name", prop: "name", placeholder: "str: Name of network", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Administration level", prop: "administration_level", prop_id: "administration_level_id", lookup: "levels", required: true, default: null, enableInEdit: true, showInGrid: true }
  ],
  lookups: lookups
});

export default pageOptions;
