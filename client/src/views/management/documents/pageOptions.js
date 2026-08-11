const pageOptions = (lookups) => {
  return {
    entityName: "Document",
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
        type: "lookup",
        label: "Data Table",
        prop_id: "datatable_id",
        prop: "datatable_label",
        lookup: "datatables",
        required: true,
        default: null,
        enableInEdit: true,
        showInGrid: true
      },
      {
        type: "lookup",
        label: "Type",
        prop_id: "documentobject_id",
        prop: "documentobject_label",
        lookup: "documentobjects",
        required: true,
        default: null,
        enableInEdit: true,
        showInGrid: true
      }
    ],
    lookups: lookups
  };
};

export default pageOptions;
