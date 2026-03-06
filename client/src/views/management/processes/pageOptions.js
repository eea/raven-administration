const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "lookup", label: "Sampling Point", prop_id: "sampling_point_id", prop: "sampling_point", required: true, lookup: "sampling_points", default: null, enableInEdit: true, showInGrid: true },
    { 
      type: "text", 
      label: "Activity begin", 
      prop: "activity_begin", 
      placeholder: "YYYY-MM-DD HH:MM:SS (e.g., 2020-01-01 00:00:00)", 
      required: true, 
      default: null, 
      enableInEdit: true, 
      showInGrid: true,
      pattern: "^\\d{4}-\\d{2}-\\d{2}( \\d{2}:\\d{2}:\\d{2})?$",
      title: "Enter date in format YYYY-MM-DD or YYYY-MM-DD HH:MM:SS"
    },
    { type: "lookup", label: "Data quality document", prop_id: "data_quality_document_id", prop: "data_quality_document", required: true, lookup: "data_quality_documents", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Equivalence demonstration document", prop_id: "equivalence_demonstration_document_id", prop: "equivalence_demonstration_document", required: true, lookup: "equivalence_demonstration_documents", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Process document", prop_id: "process_document_id", prop: "process_document", required: true, lookup: "process_documents", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Measurement type", prop_id: "measurement_type_id", prop: "measurement_type", required: true, lookup: "measurement_types", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Method", prop_id: "method_id", prop: "method", required: true, lookup: "methods", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Equipment", prop_id: "equipment_id", prop: "equipment", required: true, lookup: "equipments", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Analytical technique", prop_id: "analytical_technique_id", prop: "analytical_technique", required: true, lookup: "analytical_techniques", default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Equivalence demonstrated", prop_id: "equivalence_demonstrated_id", prop: "equivalence_demonstrated", required: true, lookup: "equivalence_demonstrated", default: null, enableInEdit: true, showInGrid: false },

    // OPTIONAL
    { 
      type: "text", 
      label: "Activity end", 
      prop: "activity_end", 
      placeholder: "YYYY-MM-DD HH:MM:SS (e.g., 2025-12-31 00:00:00) - Optional", 
      required: false, 
      default: null, 
      enableInEdit: true, 
      showInGrid: true,
      pattern: "^\\d{4}-\\d{2}-\\d{2}( \\d{2}:\\d{2}:\\d{2})?$",
      title: "Enter date in format YYYY-MM-DD or YYYY-MM-DD HH:MM:SS"
    }
  ],
  lookups: lookups
});

export default pageOptions;
