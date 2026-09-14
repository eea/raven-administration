// Assessment data: which assessment methods assess which assessment regime.
//
// Not an AQR3 table of its own, but the junction ComplianceAssessmentMethod is derived
// from -- core/data/plans_programs_export.py walks it to find the methods assessing each
// regime. Until this page existed a fresh Raven v4 install could create zones, sampling
// points and assessment regimes and still export an empty CAM, because nothing could
// record the link. It was written only by the v3 -> v4 migrator.
//
// CAM_05 AssessmentMethodId is either a sampling point or a model (MOD_/OBE_), so
// exactly one of the two lookups is filled in. The database generates the single
// assessmentlocal_id column from whichever it is, and the API rejects both or neither.
//
// Valid From / Valid To bound the period the method assessed the regime. Both blank
// means unbounded, which is what every link written before 4.502.24 carries. When a
// method stops assessing a regime, set Valid To rather than deleting the row: a deleted
// link takes its compliance rows with it on the next recalculation, including those for
// years already submitted.
const pageOptions = (lookups) => ({
  entityName: "Assessment Data",
  showRequiredAndoptionalSideBySideInCrud: true,
  properties: [
    // -- Required ---------------------------------------------------------------
    { type: "lookup", label: "Assessment Regime", prop_id: "assessment_regime_id", prop: "assessment_regime_id", lookup: "regimes", placeholder: "the zone, pollutant and objective this method assesses compliance for", required: true, default: null, enableInEdit: true, defaultHidden: true },
    { type: "lookup", label: "Assessment Type", prop_id: "assessmenttype", prop: "assessment_type", lookup: "assessment_types", placeholder: "AQR3 CAM_07 - how the air was assessed by this method", required: true, default: null, enableInEdit: true, showInGrid: true },

    // -- Exactly one of these two ------------------------------------------------
    { type: "lookup", label: "Sampling Point", prop_id: "sampling_point_id", prop: "sampling_point_id", lookup: "sampling_points", placeholder: "AQR3 CAM_05 by measurement - leave empty if a model assesses this regime", required: false, default: null, enableInEdit: true, defaultHidden: true },
    { type: "lookup", label: "Model / OBE", prop_id: "model_id", prop: "model_id", lookup: "models", placeholder: "AQR3 CAM_05 by modelling or objective estimation - leave empty if a sampling point assesses this regime", required: false, default: null, enableInEdit: true, defaultHidden: true },

    // -- Optional ---------------------------------------------------------------
    { type: "eeaDatetime", label: "Valid From", prop: "from_time", placeholder: "when this method started assessing this regime - blank means always", required: false, default: null, enableInEdit: true, showInGrid: true },
    { type: "eeaDatetime", label: "Valid To", prop: "to_time", placeholder: "when it stopped - blank means still current. Set this rather than deleting the row", required: false, default: null, enableInEdit: true, showInGrid: true },
    { type: "textarea", label: "Description", prop: "assessmentmethodedescription", placeholder: "free text, for anything the codes cannot say", required: false, default: null, enableInEdit: true, defaultHidden: true },

    // -- Resolved for display, never edited --------------------------------------
    { type: "gridOnly", label: "Zone", prop: "zone_name", showInGrid: true, val_func: (r) => r.zone_name ?? "—" },
    { type: "gridOnly", label: "Pollutant", prop: "regime_pollutant", showInGrid: true, val_func: (r) => r.regime_pollutant ?? "—" },
    { type: "gridOnly", label: "Objective", prop: "objective_type", showInGrid: true, val_func: (r) => `${r.objective_type ?? "—"}/${r.reporting_metric ?? "—"}` },
    { type: "gridOnly", label: "Assessment Method", prop: "assessment_method", showInGrid: true, val_func: (r) => r.assessment_method ?? r.assessmentlocal_id ?? "—" },
    { type: "gridOnly", label: "Kind", prop: "assessment_method_kind", showInGrid: true, val_func: (r) => r.assessment_method_kind ?? "—" },
    { type: "text", label: "Id", prop: "id", required: false, default: null, enableInEdit: false, defaultHidden: true }
  ],
  lookups
});

export default pageOptions;
