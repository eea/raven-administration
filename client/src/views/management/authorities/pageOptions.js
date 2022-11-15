const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "text", label: "Name", prop: "name", placeholder: "str: Name of authority", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "Organisation", prop: "organisation", placeholder: "str: Name of organisation", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "Locator", prop: "locator", placeholder: "str: Location of authority", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Postcode", prop: "postcode", placeholder: "int: Postal code of authority", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Email", prop: "email", placeholder: "str: Email of authority", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Address", prop: "address", placeholder: "str: Address of authority", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Phone", prop: "phone", placeholder: "str: Phone of authority", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "text", label: "Website", prop: "website", placeholder: "str: Website of authority", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "checkbox", label: "Is main authority", prop: "is_responsible_reporter", required: true, default: false, enableInEdit: true, showInGrid: true },
    // OTHER
    {
      type: "gridOnly",
      label: "Referenced by",
      prop: "ref_count",
      default: 0,
      showInGrid: true,
      cls_func: (row) => (row.ref_count == 0 ? "text-nord11" : "text-nord10")
    }
  ],
  lookups: lookups
});

export default pageOptions;
