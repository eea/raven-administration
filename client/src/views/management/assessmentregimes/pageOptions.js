const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "text", label: "Name", prop: "name", placeholder: "str: Name of regime", required: true, default: null, enableInEdit: true, showInGrid: false },

    { type: "lookup", label: "Zone", prop_id: "zone_id", prop: "zone", lookup: "zones", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "lookup", label: "Pollutant", prop_id: "pollutant_id", prop: "pollutant", required: true, lookup: "pollutants", default: null, enableInEdit: false, showInGrid: true },
    { type: "lookup", label: "Object Type", prop_id: "object_type_id", prop: "object_type", required: true, lookup: "object_types", default: null, enableInEdit: false, showInGrid: true },
    { type: "lookup", label: "Reporting Metric", prop_id: "reporting_metric_id", prop: "reporting_metric", required: true, lookup: "reporting_metrics", default: null, enableInEdit: false, showInGrid: true },
    { type: "lookup", label: "Protection Target", prop_id: "protection_target_id", prop: "protection_target", required: true, lookup: "protection_targets", default: null, enableInEdit: false, showInGrid: true },
    { type: "lookup", label: "Exceedance", prop_id: "exceedance_id", prop: "exceedance", required: true, lookup: "exceedances", default: null, enableInEdit: true, showInGrid: true },

    { type: "number", label: "Year", prop: "year", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "Report", prop: "report", required: true, default: false, enableInEdit: true, showInGrid: false },

    // OTHER
    {
      type: "gridOnly",
      label: "Sampling points",
      prop: "spo_count",
      default: 0,
      showInGrid: true,
      cls_func: (row) => (row.ref_count == 0 ? "text-nord11" : "text-nord10")
    }
  ],
  lookups: lookups
});

export default pageOptions;
