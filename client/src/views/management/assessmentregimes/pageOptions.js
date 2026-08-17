const pageOptions = (lookups) => ({
  entityName: "Assessment Regime",
  showRequiredAndoptionalSideBySideInCrud: true,
  properties: [
    // REQUIRED
    { type: "lookup", label: "Pollutant", prop_id: "pollutant_id", prop: "pollutant", lookup: "pollutants", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Zone", prop_id: "zone_id", prop: "zone", lookup: "zones", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Objective Type", prop_id: "objective_type_id", prop: "objective_type", lookup: "objective_types", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Protection Target", prop_id: "protection_target_id", prop: "protection_target", lookup: "protection_targets", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Reporting Metric", prop_id: "reporting_metric_id", prop: "reporting_metric", lookup: "reporting_metrics", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "number", label: "Classification Year", prop: "classification_year", placeholder: "num: e.g. 2024", required: true, default: null, enableInEdit: true, showInGrid: true },

    // OPTIONAL
    // AQR3 ARZ_02. Mandatory format:
    // ARE_<ZoneId>_<PollutantId>_<ObjectiveType>_<ProtectionTarget>_<ReportingMetric>_<ClassificationYear>_<idx>
    // Left empty, the API derives it from the required fields above, so the
    // seven-segment string does not have to be typed correctly by hand.
    { type: "text", label: "Id", prop: "id", placeholder: "str: leave empty to derive from the fields opposite", required: false, default: null, enableInEdit: false, showInGrid: true },
    { type: "lookup", label: "Threshold Exceedance", prop_id: "assessment_threshold_exceedance_id", prop: "assessment_threshold_exceedance", lookup: "threshold_exceedances", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Postponement Year", prop: "postponement_year", placeholder: "num: e.g. 2027", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "checkbox", label: "Fixed Measurement Reduction", prop: "fixed_measurement_reduction", required: false, default: false, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Resident Population", prop: "zone_resident_population", placeholder: "num: people in the zone", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Resident Population Year", prop: "zone_resident_population_year", placeholder: "num: year the population refers to", required: false, default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Classification Document", prop_id: "classification_document_id", prop: "classification_document_id", lookup: "documents", required: false, default: null, enableInEdit: true, showInGrid: false }
  ],
  lookups: lookups
});

export default pageOptions;
