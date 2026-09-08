// AQR3 ADJ PollutionLevelAdjustment. Deductions from measured pollution levels for
// causes outside a country's control -- natural sources and winter salting or sanding.
//
// A deduction can change whether a zone passes or fails, so a row records the
// attainment it applies to, the cause, the model that quantified it and the report
// that justifies it. AQR3 requires a different assessment method for each adjustment
// source, so the deduction for each can be reported separately in the MOEResult
// tables; the API rejects a method already used for another source on the same
// attainment.
//
// Both key parts are editable, hence keyProps -- an UPDATE keyed on the new values
// would match nothing and leave the original row in place.
const pageOptions = (lookups) => ({
  entityName: "Adjustment",
  keyProps: ["attainment_id", "adjustment_source_id"],
  showRequiredAndoptionalSideBySideInCrud: true,
  properties: [
    // REQUIRED -- the two key parts.
    // ADJ_02 must match an attainment that the compliance calculation produced, so the
    // lookup is empty until Recalculate compliance has run on the Dataflow page.
    { type: "lookup", label: "Attainment", prop_id: "attainment_id", prop: "attainment_id", lookup: "attainments", placeholder: "ADJ_02 - the attainment situation this deduction applies to", required: true, default: null, enableInEdit: true, showInGrid: true },
    // The 16 permitted causes: sea spray, Saharan dust, wildfires, volcanic and
    // seismic activity, high-wind resuspension, each inside/outside the state.
    { type: "lookup", label: "Adjustment Source", prop_id: "adjustment_source_id", prop: "adjustment_source", lookup: "adjustment_sources", placeholder: "ADJ_03 - the cause of the deduction", required: true, default: null, enableInEdit: true, showInGrid: true },

    // OPTIONAL
    { type: "lookup", label: "Assessment Method", prop_id: "adjustment_assessment_method_id", prop: "adjustment_assessment_method_id", lookup: "methods", placeholder: "ADJ_04 - the model/OBE that quantified the deduction", required: false, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Justifying Document", prop_id: "adjustment_document_id", prop: "adjustment_document_id", lookup: "documents", placeholder: "ADJ_05 - the report that justifies the deduction", required: false, default: null, enableInEdit: true, showInGrid: true }
  ],
  lookups: lookups
});

export default pageOptions;
