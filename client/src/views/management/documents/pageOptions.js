// AQR3 DOC_04. Shared with DocumentCrud.vue, which builds the Id's first part.
export const ID_HELP =
  "AQR3 DOC_04 DocumentId. The guide leaves the format free but recommends DOC + document type + data table; " +
  "the first part is built from Data Table and Type, and you type the rest. Must be unique and cannot be changed later. " +
  "Reference it from the station, process, model, regime, adjustment or plan the document belongs to: " +
  "EEA flags documents nothing references for deletion.";

const pageOptions = (lookups) => {
  return {
    entityName: "Document",
    properties: [
      {
        type: "text",
        label: "Id",
        prop: "id",
        help: ID_HELP,
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
        // AQR3 DOC_05. The filename of the PDF. Uploading the PDF to Raven sets
        // it to the file's name, and puts the public URL in Original URL.
        type: "text",
        label: "Attachment",
        prop: "documentattachment",
        placeholder: "str: PDF filename, e.g. plan_2024.pdf (max 100 chars)",
        required: false,
        default: null,
        enableInEdit: true,
        showInGrid: true
      },
      {
        // AQR3 DOC_06. Where the document is published: a URL the user has, or
        // the permanent public URL Raven gives a PDF uploaded to it.
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
