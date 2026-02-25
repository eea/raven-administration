const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: true,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "lookup", label: "Sampling Point", prop_id: "sampling_point_id", prop: "sampling_point", required: true, lookup: "sampling_points", default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "Activity begin", prop: "activity_begin", placeholder: "str: Activity begin (e.g., 2020-01-01)", required: true, default: null, enableInEdit: true, showInGrid: true },

    // OPTIONAL
    { type: "text", label: "Activity end", prop: "activity_end", placeholder: "str: Activity end (e.g., 2025-12-31)", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Data quality report ID", prop: "data_quality_report_id", placeholder: "str: Data quality report ID", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Equivalence demonstration report ID", prop: "equivalence_demonstration_report_id", placeholder: "str: Equivalence demonstration report ID", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Process documentation ID", prop: "process_documentation_id", placeholder: "str: Process documentation ID", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Measurement type", prop_id: "measurement_type_id", prop: "measurement_type", required: false, lookup: "measurement_types", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Method", prop_id: "method_id", prop: "method", required: false, lookup: "methods", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Equipment", prop_id: "equipment_id", prop: "equipment", required: false, lookup: "equipments", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Analytical technique", prop_id: "analytical_technique_id", prop: "analytical_technique", required: false, lookup: "analytical_techniques", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Equivalence demonstrated", prop_id: "equivalence_demonstrated_id", prop: "equivalence_demonstrated", required: false, lookup: "equivalence_demonstrated", default: null, enableInEdit: true, showInGrid: false }
  ],
  lookups: lookups
});

export default pageOptions;
