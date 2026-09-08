// AQR3 SPP SamplingProcess. The equipment configuration and operating period behind a
// sampling point's measurements.
//
// "Sampling Process", not "Process": AQR3 v5.02 has no Processes table -- the entity is
// SamplingProcess (the guide's own sheet spells it "SamplingProcesss"). `processes` is
// raven's local table name, as schema.sql notes on the table itself.
//
// Required here means not null in schema.sql. Everything else is genuinely optional --
// the vocabularies and the three documents are all nullable columns, and demanding them
// meant a process could not be created until three separate document records existed.
const pageOptions = (lookups) => ({
  entityName: "Sampling Process",
  // The AQR3 SPP key minus CountryCode, which is instance-wide. SPP_02 states that the
  // same ProcessId is re-used for one equipment configuration across several sampling
  // points, so `id` alone does not identify a row -- Manager posts all three parts as
  // the key and the API moves the row rather than rewriting its namesakes.
  keyProps: ["id", "sampling_point_id", "process_activity_begin"],
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED -- the three not-null columns.
    { type: "text", label: "Id", prop: "id", placeholder: "str: SPP_02 ProcessId - a unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    // SPP_03 AssessmentMethodId, and part of the AQR3 key. The SPP export inner joins
    // sampling_points, so a process without one is dropped from the submission entirely.
    // Shown in the picker rather than the grid: the value is a bare id, and Station and
    // Pollutant below say the same thing legibly.
    { type: "lookup", label: "Sampling Point", prop_id: "sampling_point_id", prop: "sampling_point", required: true, lookup: "sampling_points", default: null, enableInEdit: true, defaultHidden: true },
    { type: "eeaDatetime", label: "Activity Begin", prop: "process_activity_begin", required: true, default: null, enableInEdit: true, showInGrid: true },

    // DERIVED -- the sampling point's own attributes, joined in by the list endpoint.
    // gridOnly keeps them out of the form: they belong to the sampling point and are
    // edited there. Pollutant in particular is SPP_06, which AQR3 also reads from the
    // sampling point rather than from the process.
    { type: "gridOnly", label: "Station", prop: "station", showInGrid: true, val_func: (r) => r.station ?? "—" },
    { type: "gridOnly", label: "Pollutant", prop: "pollutant", showInGrid: true, val_func: (r) => r.pollutant ?? "—" },
    { type: "gridOnly", label: "Time Resolution", prop: "time_resolution", defaultHidden: true, val_func: (r) => r.time_resolution ?? "—" },
    { type: "gridOnly", label: "Unit", prop: "unit", defaultHidden: true, val_func: (r) => r.unit ?? "—" },

    // OPTIONAL -- nullable in schema.sql, so a blank field is a legal row.
    { type: "eeaDatetime", label: "Activity End", prop: "process_activity_end", required: false, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Measurement Type", prop_id: "measurement_type_id", prop: "measurement_type", required: false, lookup: "measurement_types", default: null, enableInEdit: true, defaultHidden: true },
    { type: "lookup", label: "Method", prop_id: "method_id", prop: "method", required: false, lookup: "methods", default: null, enableInEdit: true, defaultHidden: true },
    { type: "lookup", label: "Equipment", prop_id: "equipment_id", prop: "equipment", required: false, lookup: "equipments", default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "Equipment Identifier", prop: "equipment_identifier", placeholder: "str: serial or asset tag of the physical analyser (raven-internal)", required: false, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Analytical Technique", prop_id: "analytical_technique_id", prop: "analytical_technique", required: false, lookup: "analytical_techniques", default: null, enableInEdit: true, defaultHidden: true },
    { type: "lookup", label: "Equivalence Demonstrated", prop_id: "equivalence_demonstrated_id", prop: "equivalence_demonstrated", required: false, lookup: "equivalence_demonstrated", default: null, enableInEdit: true, defaultHidden: true },
    { type: "lookup", label: "Data Quality Document", prop_id: "data_quality_document_id", prop: "data_quality_document", required: false, lookup: "data_quality_documents", default: null, enableInEdit: true, defaultHidden: true },
    { type: "lookup", label: "Equivalence Demonstration Document", prop_id: "equivalence_demonstration_document_id", prop: "equivalence_demonstration_document", required: false, lookup: "equivalence_demonstration_documents", default: null, enableInEdit: true, defaultHidden: true },
    { type: "lookup", label: "Process Document", prop_id: "process_document_id", prop: "process_document", required: false, lookup: "process_documents", default: null, enableInEdit: true, defaultHidden: true }
  ],
  lookups: lookups
});

export default pageOptions;
