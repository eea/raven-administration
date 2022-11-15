const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "number", label: "Inlet height", prop: "inlet_height", placeholder: "float: Inlet height", required: true, default: null, enableInEdit: true, showInGrid: true },
    // OPTIONAL
    { type: "number", label: "Building Distance", prop: "building_distance", placeholder: "float: Building Distance", required: false, default: null, enableInEdit: true, showInGrid: true },
    { type: "number", label: "Kerb Distance", prop: "kerb_distance", placeholder: "float: Kerb Distance", required: false, default: null, enableInEdit: true, showInGrid: true }
  ],
  lookups: lookups
});

export default pageOptions;
