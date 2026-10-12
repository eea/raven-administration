// One row per SRS application, named as in the AQR3 v5.02 guide. SRS_02 SRSId names the
// area (and is what CAM_16 links to); SRS_03 SRSApplicationId names one use of it --
// SPO representativeness or exceedance extent (SRS_04) -- and is the key the grid cells
// (SRI) and the GeoTIFF (SRE) belong to. An area may have one application of each.
const pageOptions = (lookups) => {
  return {
    entityName: "Spatial Representativeness",
    keyProps: ["srs_application_id"],
    properties: [
      {
        // AQR3 SRS_02. Shared by the area's applications.
        type: "text",
        label: "SRS Id",
        prop: "srs_id",
        placeholder: "str(50): the area, e.g. SRS_NO0001",
        required: true,
        default: null,
        enableInEdit: true,
        showInGrid: true
      },
      {
        // AQR3 SRS_04: spo_sr | exc_sr.
        type: "lookup",
        label: "SRS Application",
        prop_id: "srs_application",
        prop: "srs_application",
        lookup: "applications",
        required: true,
        default: "spo_sr",
        enableInEdit: true,
        showInGrid: true
      },
      {
        // AQR3 SRS_03. Filled in from the two above until typed in; fixed once saved,
        // because the cells and the GeoTIFF row hang off it.
        type: "text",
        label: "SRS Application Id",
        prop: "srs_application_id",
        placeholder: "str(50): <SRS Id>_spo or <SRS Id>_exc",
        help: "Filled in from the SRS Id and the application; change it if you need another.",
        required: true,
        default: null,
        enableInEdit: false,
        showInGrid: true
      },
      {
        // AQR3 SRS_05: inline grid cells (SRI) or an external GeoTIFF (SRE).
        type: "lookup",
        label: "Result Encoding",
        prop_id: "result_encoding_id",
        prop: "result_encoding",
        lookup: "resultencodings",
        required: true,
        default: "inline",
        enableInEdit: true,
        showInGrid: true
      },
      {
        // AQR3 SRI_05 / SRE_03.
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
        // AQR3 SRS_06: the model/OBE that defined the area. A sampling point reaches an
        // SR through CAM_16 instead.
        type: "lookup",
        label: "Representativeness Assessment Method",
        prop_id: "representativeness_assessment_method_id",
        prop: "representativeness_assessment_method_id",
        lookup: "assessmentmethods",
        required: false,
        default: null,
        enableInEdit: true,
        showInGrid: true
      },
      {
        // AQR3 SRE_04. Only for an external area, which it then is.
        type: "text",
        label: "GeoTIFF Attachment",
        prop: "geotiff_attachment",
        placeholder: "str: file name uploaded to Reportnet3, e.g. srs_NO0001.tif",
        encoding: "external",
        required: true,
        default: null,
        enableInEdit: true,
        showInGrid: true
      },
      {
        // A computed COUNT, so it belongs in the grid and not in the form.
        type: "gridOnly",
        label: "Cells",
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
