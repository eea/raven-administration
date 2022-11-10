const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, showInEdit: false, showInGrid: true },
    { type: "text", label: "Name", prop: "name", placeholder: "str: Name of authority", required: true, default: null, showInEdit: true, showInGrid: true },
    { type: "lookup", label: "Media monitored", prop_id: "media_id", prop: "media", required: true, lookup: "media", default: null, showInEdit: true, showInGrid: true },
    { type: "lookup", label: "Organisation level", prop_id: "organisationlevel_id", prop: "organisationlevel", lookup: "levels", required: true, default: null, showInEdit: true, showInGrid: true },
    { type: "lookup", label: "Authority", prop_id: "authority_id", prop: "authority", required: true, lookup: "authorities", default: null, showInEdit: true, showInGrid: true },
    { type: "lookup", label: "Timezone", prop_id: "timezone_id", prop: "timezone", required: true, lookup: "timezones", default: null, showInEdit: true, showInGrid: true },
    { type: "text", label: "Begin", prop: "begin_position", placeholder: "str: YYYY-MM-DDTHH:mm:ssZ", required: true, default: null, showInEdit: true, showInGrid: true },
    { type: "text", label: "End", prop: "end_position", placeholder: "str: YYYY-MM-DDTHH:mm:ssZ", required: false, default: null, showInEdit: true, showInGrid: false }
  ],
  lookups: lookups
});

export default pageOptions;
