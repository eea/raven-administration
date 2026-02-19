const pageOptions = (lookups) => ({
  entityName: "Group",
  csvName: "groups",
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    { type: "text", label: "Id", prop: "id", required: false, default: null, showInGrid: true, width: 80 },
    { type: "text", label: "Name", prop: "name", required: true, default: "", showInGrid: true, flex: 1 },
    { type: "checkbox", label: "Management", prop: "management", required: false, default: false, showInGrid: true, width: 120 },
    { type: "checkbox", label: "Data", prop: "data", required: false, default: false, showInGrid: true, width: 100 },
    { type: "checkbox", label: "EEA dataflow", prop: "exporting", required: false, default: false, showInGrid: true, width: 120 },
    { type: "checkbox", label: "Processing", prop: "processing", required: false, default: false, showInGrid: true, width: 120 },
    { type: "checkbox", label: "Quality control", prop: "qualitycontrol", required: false, default: false, showInGrid: true, width: 140 },
    { type: "checkbox", label: "Users", prop: "users", required: false, default: false, showInGrid: true, width: 100 },
    { type: "checkbox", label: "All networks", prop: "allnetworks", required: false, default: false, showInGrid: true, width: 120 },
    {
      type: "gridOnly",
      label: "Referenced by",
      prop: "user_count",
      showInGrid: true,
      width: 140,
      val_func: (row) => `${row.user_count} user(s)`,
      cls_func: (row) => (row.user_count == 0 ? "text-nord11" : "text-nord10")
    }
  ],
  lookups: lookups
});

export default pageOptions;
