const pageOptions = (lookups) => ({
  entityName: "Model",
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: MOD_<name> or OBE_<name>", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "lookup", label: "Aggregation Process", prop_id: "data_aggregation_process_id", prop: "data_aggregation_process_id", lookup: "aggregation_processes", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Pollutant", prop_id: "pollutant_id", prop: "pollutant", lookup: "pollutants", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Result Encoding", prop_id: "result_encoding_id", prop: "result_encoding", lookup: "result_encodings", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Method Application", prop_id: "method_application_id", prop: "method_application", lookup: "method_applications", required: true, default: null, enableInEdit: true, showInGrid: true },

    // OPTIONAL
    { type: "text", label: "Name", prop: "assessment_method_name", placeholder: "str: Descriptive name of the model or OBE", required: false, default: null, enableInEdit: true, showInGrid: true },
    { type: "number", label: "Generic MQI", prop: "generic_mqi", placeholder: "num: Modelling quality indicator", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Data Quality Document", prop_id: "data_quality_document_id", prop: "data_quality_document_id", lookup: "documents", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Method Document", prop_id: "method_document_id", prop: "method_document_id", lookup: "documents", required: false, default: null, enableInEdit: true, showInGrid: false }
  ],
  lookups: lookups
});

export default pageOptions;
