const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, showInEdit: false, showInGrid: true },
    { type: "lookup", label: "Sampling point", prop_id: "sampling_point_id", prop: "sampling_point_id", lookup: "sampling_points", required: true, default: null, showInEdit: true, showInGrid: true },

    { type: "lookup", label: "Process", prop_id: "process_id", prop: "process_id", required: true, lookup: "processes", default: null, showInEdit: true, showInGrid: true },
    { type: "lookup", label: "Sample", prop_id: "sample_id", prop: "sample_id", required: true, lookup: "samples", default: null, showInEdit: true, showInGrid: true },
    { type: "lookup", label: "Result nature", prop_id: "result_nature_id", prop: "result_nature", required: true, lookup: "result_nature_values", default: null, showInEdit: true, showInGrid: false },
    { type: "lookup", label: "Process type", prop_id: "process_type_id", prop: "process_type", required: true, lookup: "processtype_values", default: null, showInEdit: true, showInGrid: false },
    { type: "eeaDatetime", label: "Begin", prop: "begin_position", required: true, default: null, showInEdit: true, showInGrid: true },

    // OPTIONAL
    { type: "eeaDatetime", label: "End", prop: "end_position", required: false, default: null, showInEdit: true, showInGrid: false }
  ],
  lookups: lookups
});

export default pageOptions;
