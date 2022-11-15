const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "text", label: "Name", prop: "name", placeholder: "str: Name of network", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Media monitored", prop_id: "media_id", prop: "media", required: true, lookup: "media", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Organisation level", prop_id: "organisationlevel_id", prop: "organisationlevel", lookup: "levels", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Authority", prop_id: "authority_id", prop: "authority", required: true, lookup: "authorities", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Timezone", prop_id: "timezone_id", prop: "timezone", required: true, lookup: "timezones", default: null, enableInEdit: true, showInGrid: false },
    { type: "eeaDatetime", label: "Begin", prop: "begin_position", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "eeaDatetime", label: "End", prop: "end_position", required: false, default: null, enableInEdit: true, showInGrid: false }
  ],
  lookups: lookups
});

export default pageOptions;
