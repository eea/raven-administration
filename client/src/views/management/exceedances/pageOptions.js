const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: true,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },

    { type: "lookup", label: "Attainment", prop_id: "attainment_id", prop: "attainment", lookup: "attainments", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Element", prop_id: "exceedance_description_id", prop: "exceedance_description", required: true, lookup: "exceedance_descriptions", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Exceedance type", prop_id: "exceedance_type_id", prop: "exceedance_type", required: true, lookup: "exceedance_types", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Area classification", prop_id: "area_classification_id", prop: "area_classification", required: true, lookup: "area_classifications", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Adjustment type", prop_id: "adjustment_type_id", prop: "adjustment_type", required: true, lookup: "adjustment_types", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Reason", prop_id: "reason_id", prop: "reason", required: true, lookup: "reasons", default: null, enableInEdit: true, showInGrid: true },

    { type: "number", label: "Value", prop: "exceedance_value", placeholder: "int if type numberExceednace else float", required: true, default: null, enableInEdit: true, showInGrid: true },

    { type: "checkbox", label: "Has exceedance", prop: "has_exceedance", required: true, default: false, enableInEdit: true, showInGrid: true },

    // OPTIONAL
    { type: "number", label: "Population year", prop: "population_year", placeholder: "int: Population year", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Exposed population", prop: "exposed_population", placeholder: "int: Exposed population", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Surface area", prop: "surface_area", placeholder: "float: Surface area [in m2]", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Vegetation area", prop: "vegetation_area", placeholder: "float: Vegetation area [in m2]", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Other reason", prop: "other_reason", placeholder: "str: Other reason", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Adjustment source", prop_id: "adjustment_source_id", prop: "adjustment_source", required: false, lookup: "adjustment_source_types", default: null, enableInEdit: true, showInGrid: false },

    //OTHER
    {
      type: "gridOnly",
      label: "Sampling points",
      showInGrid: true,
      val_func: (row) => row.spo_count,
      cls_func: (row) => (row.spo_count == 0 ? "text-nord11" : "text-nord10")
    }

    // CUSTOM
    // { type: "custom", label: "Methods", prop: "data", default: [], enableInEdit: true, showInGrid: false }
  ],
  lookups: lookups
});

export default pageOptions;
