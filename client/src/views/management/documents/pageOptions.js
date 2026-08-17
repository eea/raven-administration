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
      },
      // OPTIONAL
      {
        // AQR3 DOC_05. The filename of the PDF uploaded to Reportnet3 alongside
        // the CSVs — raven records the reference, not the file.
        type: "text",
        label: "Attachment",
        prop: "documentattachment",
        placeholder: "str: filename of the PDF uploaded to Reportnet3, e.g. plan_2024.pdf",
        required: false,
        default: null,
        enableInEdit: true,
        showInGrid: true
      },
      {
        // AQR3 DOC_06. The alternative to attaching the PDF to the Reportnet3
        // envelope: where the document is already published.
        type: "text",
        label: "Original URL",
        prop: "document_original_url",
        placeholder: "str: where the document is published (max 100 chars)",
        required: false,
        default: null,
        enableInEdit: true,
        showInGrid: true
      }
    ],
    lookups: lookups
  };
};

export default pageOptions;
