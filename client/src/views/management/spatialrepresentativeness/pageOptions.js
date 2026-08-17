const pageOptions = (lookups) => {
  return {
    entityName: "Spatial Representativeness",
    properties: [
      {
        type: "text",
        label: "Id",
        prop: "id",
        required: true,
        default: null,
        enableInEdit: false,
        showInGrid: true
      },
      {
        type: "text",
        label: "Application Id",
        prop: "srs_application_id",
        required: true,
        default: null,
        enableInEdit: true,
        showInGrid: true
      },
      {
        type: "lookup",
        label: "Application",
        prop_id: "srs_application",
        prop: "srs_application",
        lookup: "applications",
        required: true,
        default: null,
        enableInEdit: true,
        showInGrid: true
      },
      {
        type: "lookup",
        label: "Spatial Resolution",
        prop_id: "spatial_resolution",
        prop: "spatial_resolution",
        lookup: "spatialresolutions",
        required: true,
        default: null,
        enableInEdit: true,
        showInGrid: true
      },
      {
        // AQR3 SRS_05 — inline grid cells vs an external GeoTIFF.
        type: "lookup",
        label: "Result Encoding",
        prop_id: "result_encoding_id",
        prop: "result_encoding",
        lookup: "resultencodings",
        required: false,
        default: null,
        enableInEdit: true,
        showInGrid: true
      },
      {
        // AQR3 SRS_06 — the sampling point or model this area represents. No
        // vocabulary, so the lookup unions both tables.
        type: "lookup",
        label: "Assessment Method",
        prop_id: "representativeness_assessment_method_id",
        prop: "representativeness_assessment_method_id",
        lookup: "assessmentmethods",
        required: false,
        default: null,
        enableInEdit: true,
        showInGrid: true
      },
      {
        // A computed COUNT, so it belongs in the grid and not in the form.
        // Was "numeric", which Crud does not recognise — it happened to render
        // nothing in edit mode and so looked correct.
        type: "gridOnly",
        label: "Points",
        prop: "point_count",
        required: false,
        default: null,
        enableInEdit: false,
        showInGrid: true
      }
    ],
    lookups: lookups
  };
};

export default pageOptions;
