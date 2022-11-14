const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, showInEdit: false, showInGrid: true },
    { type: "text", label: "Name", prop: "name", placeholder: "str: Name of authority", required: true, default: null, showInEdit: true, showInGrid: true },
    { type: "lookup", label: "Media monitored", prop_id: "media_id", prop: "media", required: true, lookup: "media", default: null, showInEdit: true, showInGrid: false },
    { type: "lookup", label: "Organisation level", prop_id: "organisationlevel_id", prop: "organisationlevel", lookup: "levels", required: true, default: null, showInEdit: true, showInGrid: true },
    { type: "lookup", label: "Authority", prop_id: "authority_id", prop: "authority", required: true, lookup: "authorities", default: null, showInEdit: true, showInGrid: true },
    { type: "lookup", label: "Timezone", prop_id: "timezone_id", prop: "timezone", required: true, lookup: "timezones", default: null, showInEdit: true, showInGrid: false },
    { type: "eeaDatetime", label: "Begin", prop: "begin_position", required: true, default: null, showInEdit: true, showInGrid: false },
    { type: "eeaDatetime", label: "End", prop: "end_position", required: false, default: null, showInEdit: true, showInGrid: false },

    // OTHER
    {
      type: "gridOnly",
      label: "Referenced by",
      prop: "ref_count",
      default: 0,
      showInGrid: true,
      cls_func: (row) => (row.ref_count == 0 ? "text-nord11" : "text-nord10")
    }
  ],
  lookups: lookups
});

export default pageOptions;
