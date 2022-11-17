const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "text", label: "Name", prop: "name", placeholder: "str: Name of regime", required: true, default: null, enableInEdit: true, showInGrid: false },

    { type: "lookup", label: "Zone", prop_id: "zone_id", prop: "zone", lookup: "zones", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "lookup", label: "Pollutant", prop_id: "pollutant_id", prop: "pollutant", required: true, lookup: "pollutants", default: null, enableInEdit: false, showInGrid: true },
    { type: "lookup", label: "Object type", prop_id: "object_type_id", prop: "object_type", required: true, lookup: "object_types", default: null, enableInEdit: false, showInGrid: true },
    { type: "lookup", label: "Reporting metric", prop_id: "reporting_metric_id", prop: "reporting_metric", required: true, lookup: "reporting_metrics", default: null, enableInEdit: false, showInGrid: true },
    { type: "lookup", label: "Protection target", prop_id: "protection_target_id", prop: "protection_target", required: true, lookup: "protection_targets", default: null, enableInEdit: false, showInGrid: true },
    { type: "lookup", label: "Exceedance", prop_id: "exceedance_id", prop: "exceedance", required: true, lookup: "exceedances", default: null, enableInEdit: true, showInGrid: true },

    { type: "number", label: "Year", prop: "year", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "Report", prop: "report", required: true, default: null, enableInEdit: true, showInGrid: false },

    { type: "checkbox", label: "Include", prop: "include", required: true, default: false, enableInEdit: true, showInGrid: false },

    //OTHER
    {
      type: "gridOnly",
      label: "Sampling points",
      showInGrid: true,
      val_func: (row) => row.spo_count,
      cls_func: (row) => (row.spo_count == 0 ? "text-nord11" : "text-nord10")
    },

    // CUSTOM
    { type: "custom", label: "Sampling points", prop: "data", lookup: "sampling_points", required: true, default: [], enableInEdit: true, showInGrid: false }
  ],
  lookups: lookups
});

export default pageOptions;
