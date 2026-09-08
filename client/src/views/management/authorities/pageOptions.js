// AQR3 AUT Authority. The bodies responsible for air quality reporting and
// assessment, and what each is responsible for.
//
// AQR3 keys a row on (CountryCode, AuthorityInstanceId, AuthorityRole, Email).
// CountryCode is instance-wide -- settings.country_code_id -- so the remaining three
// identify a row here. All three are editable, hence keyProps: Manager sends the
// original key alongside the new values so changing one moves the row rather than
// leaving the original behind.
const pageOptions = (lookups) => ({
  entityName: "Authority",
  keyProps: ["id", "authority_role_id", "email"],
  showRequiredAndoptionalSideBySideInCrud: true,
  properties: [
    // REQUIRED -- the three key parts, plus the name of the body the row is about.
    { type: "text", label: "Instance Id", prop: "id", placeholder: "str: AUT_02 - a country code, NUTS code, zone id or network id", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Role", prop_id: "authority_role_id", prop: "authority_role", lookup: "objects", placeholder: "AUT_03 - what this authority is responsible for", required: true, default: null, enableInEdit: true, showInGrid: true },
    // Part of the key: it is what separates two organisations holding the same role
    // for the same instance -- a country reports both the authority that submits and,
    // separately, its national reference laboratory.
    { type: "text", label: "Email", prop: "email", placeholder: "str: AUT_04 - contact email", required: true, default: null, enableInEdit: true, showInGrid: true },
    // "Name", not "Organisation": AUT_06 is AuthorityName in the guide, and the label
    // predated that rename. Every label here drops the Authority prefix, as AUT_09
    // PersonName below is just "Person".
    { type: "text", label: "Name", prop: "authority_name", placeholder: "str: AUT_06 AuthorityName - the institute or organisation", required: true, default: null, enableInEdit: true, showInGrid: true },

    // OPTIONAL
    { type: "lookup", label: "Instance", prop_id: "authority_instance_id", prop: "authority_instance", lookup: "instances", placeholder: "AUT_05 - what kind of id the Instance Id is", required: false, default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "Person", prop: "person_name", placeholder: "str: AUT_09 PersonName - contact person", required: false, default: null, enableInEdit: true, showInGrid: true },
    // defaultHidden, not showInGrid: false. showInGrid: false leaves a column out of
    // the column picker altogether, so there is no way to show it at all; defaultHidden
    // lists it there unticked, which is what an occasional detail wants -- reachable
    // without spending grid width on it by default.
    { type: "text", label: "URL", prop: "authority_url", placeholder: "str: AUT_07 AuthorityURL - website", required: false, default: null, enableInEdit: true, defaultHidden: true },
    { type: "text", label: "Address", prop: "authority_address", placeholder: "str: AUT_08 AuthorityAddress - physical address", required: false, default: null, enableInEdit: true, defaultHidden: true },
    { type: "lookup", label: "Status", prop_id: "authority_status_id", prop: "authority_status", lookup: "statuses", placeholder: "AUT_10 - active or inactive", required: false, default: null, enableInEdit: true, showInGrid: true }
  ],
  lookups: lookups
});

export default pageOptions;
