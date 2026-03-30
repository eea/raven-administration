const pageOptions = (lookups) => {
  return {
    properties: [
      {
        type: "text",
        label: "SR Id",
        prop: "id",
        required: true,
        default: null,
        enableInEdit: false,
        showInGrid: true
      },
      {
        type: "text",
        label: "SR Application Id",
        prop: "sr_application_id",
        required: true,
        default: null,
        enableInEdit: true,
        showInGrid: true
      },
      {
        type: "lookup",
        label: "Application",
        prop_id: "application",
        prop: "application",
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
