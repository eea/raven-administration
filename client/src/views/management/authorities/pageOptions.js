const pageOptions = (lookups) => ({
  entityName: "Authority",
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: e.g. a ZoneId, NUTS code or network id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "text", label: "Person Name", prop: "person_name", placeholder: "str: Contact person name", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "Email", prop: "email", placeholder: "str: Contact email", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "Name", prop: "authority_name", placeholder: "str: Name of the institute or organisation", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "URL", prop: "authority_url", placeholder: "str: Website URL", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Address", prop: "authority_address", placeholder: "str: Physical address", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Instance", prop: "authority_instance", prop_id: "authority_instance_id", lookup: "instances", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Role", prop: "authority_role", prop_id: "authority_role_id", lookup: "objects", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Status", prop: "authority_status", prop_id: "authority_status_id", lookup: "statuses", required: true, default: null, enableInEdit: true, showInGrid: true }
  ],
  lookups: lookups
});

export default pageOptions;
