const pageOptions = (lookups) => ({
  entityName: "Process",
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "lookup", label: "Sampling Point", prop_id: "sampling_point_id", prop: "sampling_point", required: true, lookup: "sampling_points", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Data Quality Document", prop_id: "data_quality_document_id", prop: "data_quality_document", required: true, lookup: "data_quality_documents", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Equivalence Demonstration Document", prop_id: "equivalence_demonstration_document_id", prop: "equivalence_demonstration_document", required: true, lookup: "equivalence_demonstration_documents", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Process Document", prop_id: "process_document_id", prop: "process_document", required: true, lookup: "process_documents", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Measurement Type", prop_id: "measurement_type_id", prop: "measurement_type", required: true, lookup: "measurement_types", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Method", prop_id: "method_id", prop: "method", required: true, lookup: "methods", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Equipment", prop_id: "equipment_id", prop: "equipment", required: true, lookup: "equipments", default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Analytical Technique", prop_id: "analytical_technique_id", prop: "analytical_technique", required: true, lookup: "analytical_techniques", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Equivalence Demonstrated", prop_id: "equivalence_demonstrated_id", prop: "equivalence_demonstrated", required: true, lookup: "equivalence_demonstrated", default: null, enableInEdit: true, showInGrid: false },

    // OPTIONAL
    { type: "text", label: "Equipment Identifier", prop: "equipment_identifier", placeholder: "str: Equipment identifier (optional)", required: false, default: null, enableInEdit: true, showInGrid: true },
    // The format hint lives in the placeholder, which Crud.vue actually renders.
    // `pattern`/`title` were set here previously but nothing binds them and there
    // is no format validation, so they promised behaviour that never happened.
    { type: "text", label: "Activity Begin", prop: "process_activity_begin", placeholder: "YYYY-MM-DD HH:MM:SS (e.g. 2020-01-01 00:00:00)", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "Activity End", prop: "process_activity_end", placeholder: "YYYY-MM-DD HH:MM:SS (e.g. 2025-12-31 00:00:00) - optional", required: false, default: null, enableInEdit: true, showInGrid: true }
  ],
  lookups: lookups
});

export default pageOptions;
