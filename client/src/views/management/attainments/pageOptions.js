const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "text", label: "Name", prop: "name", placeholder: "str: Name of attainment", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Assessment regime", prop_id: "assessment_regime_id", prop: "assessment_regime", required: true, lookup: "assessment_regimes", default: null, enableInEdit: true, showInGrid: true },

    // OPTIONAL
    { type: "text", label: "Comment", prop: "comment", placeholder: "str: Comment", required: false, default: null, enableInEdit: true, showInGrid: true },

    //OTHER
    {
      type: "gridOnly",
      label: "Exceedance descriptions",
      showInGrid: true,
      val_func: (row) => row.ed_count,
      cls_func: (row) => (row.ed_count == 0 ? "text-nord11" : "text-nord10")
    }
  ],
  lookups: lookups
});

export default pageOptions;
