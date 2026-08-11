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
        type: "numeric",
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
