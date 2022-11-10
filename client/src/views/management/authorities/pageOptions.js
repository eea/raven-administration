const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, showInEdit: false, showInGrid: true },
    { type: "text", label: "Name", prop: "name", placeholder: "str: Name of authority", required: true, default: null, showInEdit: true, showInGrid: true },
    { type: "text", label: "Organisation", prop: "organisation", placeholder: "str: Name of organisation", required: true, default: null, showInEdit: true, showInGrid: true },
    { type: "text", label: "Locator", prop: "locator", placeholder: "str: Location of authority", required: true, default: null, showInEdit: true, showInGrid: true },
    { type: "number", label: "Postcode", prop: "postcode", placeholder: "int: Postal code of authority", required: true, default: null, showInEdit: true, showInGrid: true },
    { type: "text", label: "Email", prop: "email", placeholder: "str: Email of authority", required: true, default: null, showInEdit: true, showInGrid: true },
    { type: "text", label: "Address", prop: "address", placeholder: "str: Address of authority", required: true, default: null, showInEdit: true, showInGrid: true },
    { type: "text", label: "Phone", prop: "phone", placeholder: "str: Phone of authority", required: true, default: null, showInEdit: true, showInGrid: true },
    { type: "text", label: "Website", prop: "website", placeholder: "str: Website of authority", required: true, default: null, showInEdit: true, showInGrid: true },
    { type: "checkbox", label: "Is main authority", prop: "is_responsible_reporter", required: true, default: false, showInEdit: true, showInGrid: true }
  ],
  lookups: lookups
});

export default pageOptions;
