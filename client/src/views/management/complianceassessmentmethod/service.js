import { Get, Post } from "../../../helpers/request";

const BASE = "/api/management/complianceassessmentmethod";

const Service = {
  // Rows exist per reporting year, so a year is always part of the request.
  get: async (year) => Get(`${BASE}?year=${year}`),
  lookups: async () => Get(`${BASE}/lookups`),
  // The key travels separately from the values, but only to address the row: it is
  // derived from the assessment regime and method and is not editable.
  update: async (key, values) => Post(`${BASE}/update`, { key, values }),
  // The same recalculation as Dataflow's button, under the management claim.
  recalculate: async (year) => Post(`${BASE}/recalculate`, { year }),
};

export default Service;
