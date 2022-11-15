const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: true,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "lookup", label: "Measurement type", prop_id: "measurement_type_id", prop: "measurement_type", required: true, lookup: "measurement_types", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Measurement method", prop_id: "measurement_method_id", prop: "measurement_method", required: true, lookup: "measurement_methods", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Equiv demonstration", prop_id: "equiv_demonstration_id", prop: "equiv_demonstration", required: true, lookup: "equiv_demonstrations", default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Detection limit", prop: "detection_limit", placeholder: "float: Detection limit", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Detection limit unit", prop_id: "detection_limit_uom_id", prop: "detection_limit_uom", required: true, lookup: "concentrations", default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Duration number", prop: "duration_number", placeholder: "int: Duration number", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Duration number timestep", prop_id: "duration_unit_id", prop: "duration_unit", required: true, lookup: "timesteps", default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Cadence number", prop: "cadence_number", placeholder: "int: Cadence number", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Cadence number timestep", prop_id: "cadence_unit_id", prop: "cadence_unit", required: true, lookup: "timesteps", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Authority", prop_id: "authority_id", prop: "authority", required: true, lookup: "authorities", default: null, enableInEdit: true, showInGrid: false },

    // OPTIONAL
    { type: "lookup", label: "Measurement equipment", prop_id: "measurement_equipment_id", prop: "measurement_equipment", required: false, lookup: "measurement_equipments", default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Other measurement equipment", prop: "other_measurement_equipment", placeholder: "text: Other measurement equipment", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Other measurement method", prop: "other_measurement_method", placeholder: "str: Other measurement method", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Sampling method", prop: "sampling_method", placeholder: "text: Sampling method", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Other sampling method", prop: "other_sampling_method", placeholder: "text: Other sampling method", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Analytical Tech", prop: "analytical_tech", placeholder: "text: Analytical Tech", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Other analytical tech", prop: "other_analytical_tech", placeholder: "text: Other analytical tech", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Sampling equipment", prop: "sampling_equipment", placeholder: "text: Sampling equipment", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Other sampling equipment", prop: "other_sampling_equipment", placeholder: "text: Other sampling equipment", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Equiv Demonstration Report", prop: "equiv_demonstration_report", placeholder: "text: Equiv Demonstration Report", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Uncertainty estimate", prop: "uncertainty_estimate", placeholder: "float: Uncertainty estimate", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Documentation", prop: "documentation", placeholder: "text: Documentation", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "QA Report", prop: "qa_report", placeholder: "text: QA Report", required: false, default: null, enableInEdit: true, showInGrid: false },

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
