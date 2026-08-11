const pageOptions = (lookups) => ({
  entityName: "Network",
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "text", label: "Name", prop: "name", placeholder: "str: Name of network", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Organisational Level", prop: "network_organisational_level", prop_id: "network_organisational_level_id", lookup: "levels", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Timezone", prop: "timezone", prop_id: "timezone_id", lookup: "timezones", required: true, default: null, enableInEdit: true, showInGrid: true },

    // OPTIONAL
    { type: "lookup", label: "Document", prop: "network_document", prop_id: "network_document_id", lookup: "network_documents", required: false, default: null, enableInEdit: true, showInGrid: false }
  ],
  lookups: lookups
});

export default pageOptions;
