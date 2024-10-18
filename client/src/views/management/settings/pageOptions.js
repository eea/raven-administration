const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "text", label: "Namespace", prop: "namespace", placeholder: "str: Namespace to be used in dataflow", required: true, default: null, enableInEdit: true, showInGrid: true },
    // { type: "text", label: "Uom", prop: "uom_m", placeholder: "str: EEA vocabulary for meter", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "Observation prefix", prop: "observation_prefix", placeholder: "str: Dataflow prefix for observations", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "Language code", prop: "language_code", placeholder: "str: Language to be used in dataflow", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "Country", prop: "country", placeholder: "str: Country to be used in dataflow", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "Country code", prop: "country_code", placeholder: "str: Country code to be used in dataflow", required: true, default: null, enableInEdit: true, showInGrid: true }
  ],
  lookups: lookups
});

export default pageOptions;
