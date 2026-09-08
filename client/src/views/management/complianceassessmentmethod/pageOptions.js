// AQR3 CAM ComplianceAssessmentMethod. The yearly compliance situation per assessment
// regime and assessment method.
//
// Rows are DERIVED: core/reporting/aqr3/compliance.py builds them from the assessment
// regimes and the sampling points linked to them, and Recalculate compliance on the
// Dataflow page rebuilds them. So there is no add and no delete -- AQR3's way to
// retract a row is the Deletion flag (CAM_18), which is editable here.
//
// What is editable is the part the evaluation does not produce yet: the measured
// figures. A recalculation keeps what is entered here only while it has no value of
// its own; once the exceedance evaluation computes a figure, the computed one wins.
// AQR3 requires a pollution level for every assessment method, so a blank CAM_10 is
// an incomplete submission.
//
// The four key columns identify the row and are not editable -- changing one would
// describe a different compliance situation rather than correct this one -- so they
// are enableInEdit: false. keyProps still lists them: Manager addresses the row by
// them on update.
const YES_NO_UNKNOWN = [
  { value: null, label: "— unknown —" },
  { value: true, label: "Yes" },
  { value: false, label: "No" }
];

const triState = (v) => (v === null || v === undefined ? "—" : v ? "Yes" : "No");

const pageOptions = (lookups) => ({
  entityName: "Compliance Assessment Method",
  keyProps: ["reporting_year", "assessment_regime_id", "data_aggregation_process_id",
             "assessment_method_id"],
  showRequiredAndoptionalSideBySideInCrud: true,
  // A retracted row stays visible but reads as struck out, the way the old page showed it.
  getRowStyle: (params) => (params.data?.deletion ? { opacity: 0.5 } : null),
  properties: [
    // -- Derived. Shown, never edited. ------------------------------------------
    { type: "text", label: "Reporting Year", prop: "reporting_year", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "text", label: "Assessment Regime Id", prop: "assessment_regime_id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "text", label: "Data Aggregation Process Id", prop: "data_aggregation_process_id", required: true, default: null, enableInEdit: false, defaultHidden: true },
    { type: "text", label: "Assessment Method Id", prop: "assessment_method_id", required: true, default: null, enableInEdit: false, showInGrid: true },
    // CAM_05 is a sampling_points.id or a models.id -- schema.sql:1646, "deliberately
    // not a FK, since it spans both". Resolved here so the grid does not show a bare
    // code where every neighbouring column shows a label.
    { type: "gridOnly", label: "Assessment Method", prop: "assessment_method", showInGrid: true, val_func: (r) => r.assessment_method ?? r.assessment_method_id },
    { type: "gridOnly", label: "Zone", prop: "zone_name", showInGrid: true, val_func: (r) => r.zone_name ?? r.zone_id ?? "—" },
    { type: "gridOnly", label: "Data Aggregation Process", prop: "data_aggregation_process", showInGrid: true, val_func: (r) => r.data_aggregation_process ?? r.data_aggregation_process_id },
    { type: "gridOnly", label: "Pollutant", prop: "pollutant", showInGrid: true, val_func: (r) => r.pollutant ?? r.pollutant_id },
    { type: "gridOnly", label: "Assessment Type", prop: "assessment_type", showInGrid: true, val_func: (r) => r.assessment_type ?? "—" },
    { type: "gridOnly", label: "Attainment Id", prop: "attainment_id", showInGrid: true, val_func: (r) => r.attainment_id ?? "—" },
    { type: "gridOnly", label: "Objective Type", prop: "objective_type", defaultHidden: true, val_func: (r) => r.objective_type ?? "—" },
    { type: "gridOnly", label: "Reporting Metric", prop: "reporting_metric", defaultHidden: true, val_func: (r) => r.reporting_metric ?? "—" },
    { type: "gridOnly", label: "SRS Id", prop: "srs_id", defaultHidden: true, val_func: (r) => r.srs_id ?? "—" },
    { type: "gridOnly", label: "Calculated At", prop: "calculated_at", defaultHidden: true, val_func: (r) => r.calculated_at ?? "—" },

    // -- Entered here. All optional: a row starts empty and is filled in as the
    //    figures become known. ---------------------------------------------------
    { type: "lookup", label: "Is Exceedance", prop_id: "is_exceedance", prop: "is_exceedance", lookup: "yes_no", placeholder: "CAM_08", required: false, default: null, enableInEdit: true, showInGrid: true, val_func: (r) => triState(r.is_exceedance) },
    { type: "number", label: "Data Coverage (%)", prop: "data_coverage", placeholder: "num: CAM_09 - e.g. 85.78", required: false, default: null, enableInEdit: true, showInGrid: true },
    { type: "number", label: "Pollution Level", prop: "pollution_level", placeholder: "num: CAM_10 - required by AQR3 on every row", required: false, default: null, enableInEdit: true, showInGrid: true },
    { type: "number", label: "Pollution Level Adjusted", prop: "pollution_level_adjusted", placeholder: "num: CAM_11 - after the ADJ deductions", required: false, default: null, enableInEdit: true, showInGrid: true },
    { type: "number", label: "Relative Uncertainty Limit (%)", prop: "relative_uncertainty_limit", placeholder: "num: CAM_12 - required for sampling-point methods", required: false, default: null, enableInEdit: true, defaultHidden: true },
    { type: "number", label: "Assessment MQI", prop: "assessment_mqi", placeholder: "num: CAM_13 - modelling quality indicator, models only", required: false, default: null, enableInEdit: true, defaultHidden: true },
    { type: "checkbox", label: "Correction Flag", prop: "correction_flag", placeholder: "CAM_14", required: false, default: false, enableInEdit: true, defaultHidden: true },
    { type: "lookup", label: "Preliminary Reason", prop_id: "preliminary_reason_id", prop: "preliminary_reason", lookup: "reasons", placeholder: "CAM_17", required: false, default: null, enableInEdit: true, showInGrid: true },
    { type: "checkbox", label: "Deletion", prop: "deletion", placeholder: "CAM_18 - retract this row", required: false, default: false, enableInEdit: true, showInGrid: true }
  ],
  lookups: { ...lookups, yes_no: YES_NO_UNKNOWN }
});

export default pageOptions;
