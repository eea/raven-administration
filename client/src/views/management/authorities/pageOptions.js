const pageOptions = (lookups) => ({
  entityName: "Authority",
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "text", label: "Person name", prop: "person_name", placeholder: "str: Contact person name", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "Email", prop: "email", placeholder: "str: Contact email", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "Organisation name", prop: "organisation_name", placeholder: "str: Name of organisation", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "Organisation URL", prop: "organisation_url", placeholder: "str: Website URL", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Organisation address", prop: "organisation_address", placeholder: "str: Physical address", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Instance", prop: "instance", prop_id: "instance_id", lookup: "instances", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Object", prop: "object", prop_id: "object_id", lookup: "objects", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Status", prop: "status", prop_id: "status_id", lookup: "statuses", required: true, default: null, enableInEdit: true, showInGrid: true }
  ],
  lookups: lookups
});

export default pageOptions;
