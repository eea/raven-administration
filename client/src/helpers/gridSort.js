/**
 * Sorting for ag-Grid columns whose values are numbers stored as strings.
 *
 * Most id columns are varchar in the schema (sampling_points.id is varchar(100)) but hold
 * plain numbers at some installations — 694, 1213, 1214. ag-Grid infers the column type
 * from the data, sees strings, and sorts them lexicographically, so 1213 lands before 694.
 *
 * Deliberately NOT Intl.Collator({ numeric: true }), which would be a one-liner: locale
 * collation de-weights punctuation, and raven-sp-extended/client/index.js documents that
 * doing so buried 'PM Coarse' in the middle of the pollutant list. Non-numeric values here
 * keep plain code-unit order, which is what ag-Grid already gives them.
 */

// Pure non-negative integer — the exact-comparison path below.
const DIGITS = /^\d+$/;
// Signed and/or fractional. Exponent form, hex, Infinity and NaN are excluded on purpose:
// an id column should not have '1e5' reinterpreted as 100000.
const NUMERIC = /^[+-]?(\d+(\.\d+)?|\.\d+)$/;

/**
 * Classifies a value for sorting. Returns { digits } for an exact-comparable integer
 * string, { num } for anything else numeric, or null when the value is not numeric.
 *
 * Booleans, Dates and objects are never numeric — Number(true) === 1 would otherwise
 * reorder every checkbox column in the app.
 */
const asNumeric = (value) => {
  if (typeof value === "number") return Number.isFinite(value) ? { num: value } : null;
  if (typeof value !== "string") return null;

  const trimmed = value.trim();
  if (trimmed === "") return null;
  if (DIGITS.test(trimmed)) return { digits: trimmed };
  if (NUMERIC.test(trimmed)) return { num: Number(trimmed) };
  return null;
};

/**
 * Compares two digit strings exactly, at any length. Number() would lose precision past
 * 2^53 — from 16 digits on — and long ids are exactly where that would bite.
 */
const compareDigits = (a, b) => {
  const x = a.replace(/^0+(?=\d)/, "");
  const y = b.replace(/^0+(?=\d)/, "");
  if (x.length !== y.length) return x.length - y.length;
  return x < y ? -1 : x > y ? 1 : 0;
};

/**
 * ag-Grid's own fallback, reproduced from its _defaultComparator: unwrap big-decimal-like
 * objects, then compare relationally. For strings that is code-unit order, and for Dates
 * and booleans it compares by value rather than by string form.
 */
const relational = (a, b) => {
  const x = typeof a === "object" && a !== null && a.toNumber ? a.toNumber() : a;
  const y = typeof b === "object" && b !== null && b.toNumber ? b.toNumber() : b;
  if (x > y) return 1;
  if (x < y) return -1;
  return 0;
};

/**
 * ag-Grid SortComparatorFn. Ranks by (is-numeric, value), giving a total order: numeric
 * values as one group sorted numerically, then everything else in ag-Grid's existing order.
 *
 * The ranking matters. The obvious rule — "compare numerically when both values look
 * numeric, otherwise as text" — is not transitive: over '2', '10', '1a' it claims
 * 2 < 10, 10 < '1a' and '1a' < 2, a cycle. Array.prototype.sort given an inconsistent
 * comparator produces implementation-defined output, so that rule cannot safely be a
 * grid-wide default. Grouping the numerics has no cycles.
 *
 * Do not invert on isDescending — the grid applies direction itself.
 */
export const numericAwareComparator = (valueA, valueB) => {
  // Null handling copied from ag-Grid's _defaultComparator so blanks stay first ascending.
  if (valueA == null) return valueB == null ? 0 : -1;
  if (valueB == null) return 1;

  const a = asNumeric(valueA);
  const b = asNumeric(valueB);

  if (a && b) {
    if (a.digits !== undefined && b.digits !== undefined) {
      const exact = compareDigits(a.digits, b.digits);
      if (exact !== 0) return exact;
    } else {
      const x = a.digits !== undefined ? Number(a.digits) : a.num;
      const y = b.digits !== undefined ? Number(b.digits) : b.num;
      if (x < y) return -1;
      if (x > y) return 1;
    }
    // Numerically equal but not identical text ('007' vs '7', 7 vs '7'): break the tie on
    // the text, which orders the numeric group by (value, text) — a total order.
    //
    // Using relational() here instead looks natural and is wrong: it compares '00' to 0 by
    // JS coercion (equal) but '00' to '0' as strings (unequal), so '00' == 0 == '0' while
    // '00' > '0'. That is a transitivity break, and an inconsistent comparator makes
    // Array.prototype.sort return implementation-defined output.
    const textA = String(valueA);
    const textB = String(valueB);
    return textA < textB ? -1 : textA > textB ? 1 : 0;
  }

  if (a) return -1; // numeric values group ahead of text
  if (b) return 1;

  return relational(valueA, valueB);
};

export default numericAwareComparator;
