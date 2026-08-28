/**
 * Shared vocabulary for the Observation Change History.
 *
 * These maps were duplicated verbatim in verify/ObservationLog.vue and
 * validate/ObservationLogPopup.vue. They now live here so the table cells and the
 * filter rule editor read from the same source: a filter offering "Pre-verified"
 * and a cell rendering "Pre-verified" must never drift apart, which is exactly what
 * two copies of a literal invite.
 */

export const VERIFICATION_LABELS = {
  1: "Verified",
  2: "Pre-verified",
  3: "Not verified",
};

// Keys are looked up with String(v) because -1 and -99 are valid codes and object
// keys are strings.
export const VALIDITY_LABELS = {
  1: "Valid",
  2: "Below detection",
  3: "Below+sub.",
  4: "Ozone CCQM",
  "-1": "Not valid",
  "-99": "Maintenance",
};

export const SOURCE_COLORS = {
  qc_verify: "bg-nord8/20 text-nord10",
  qc_validate: "bg-nord9/20 text-nord10",
  scaling: "bg-nord13/20 text-nord12",
  adacs_import: "bg-nord4/30 text-nord3",
  aqtvl_migration: "bg-nord15/20 text-nord15",
  plugin_nilu_qa: "bg-nord15/20 text-nord15",
};

export const verLabel = (v) => (v != null ? VERIFICATION_LABELS[v] ?? `#${v}` : "—");
export const valLabel = (v) => (v != null ? VALIDITY_LABELS[String(v)] ?? `#${v}` : "—");
export const srcColor = (src) => SOURCE_COLORS[src] ?? "bg-nord4/20 text-nord3";

/** Option lists for the filter rule editor, derived so they cannot drift from the labels above. */
const toOptions = (map) =>
  Object.entries(map).map(([value, label]) => ({ value: Number(value), label }));

export const VERIFICATION_OPTIONS = toOptions(VERIFICATION_LABELS);
export const VALIDITY_OPTIONS = toOptions(VALIDITY_LABELS);
export const SOURCE_OPTIONS = Object.keys(SOURCE_COLORS).map((value) => ({ value, label: value }));

/**
 * The fixed columns of the history table, in render order. Shared with the column
 * picker so a column cannot be shown in one place and unknown in the other.
 * `filterField` names the rule-engine field(s) this column displays; null means the
 * column is display-only.
 */
export const CORE_COLUMNS = [
  { key: "changed_at", label: "Changed at", filterField: "changed_at" },
  { key: "changed_by", label: "By", filterField: "changed_by" },
  { key: "change_source", label: "Source", filterField: "change_source" },
  { key: "period_from", label: "Period from", filterField: null },
  { key: "period_to", label: "Period to", filterField: null },
  { key: "verification", label: "Verif. old→new", filterField: "new_verification" },
  { key: "validity", label: "Validity old→new", filterField: "new_validity" },
  { key: "value", label: "Value old→new", filterField: "new_value" },
];
