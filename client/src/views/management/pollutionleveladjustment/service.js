import { Get, Post } from "../../../helpers/request";

const BASE = "/api/management/pollutionleveladjustment";

const Service = {
  get: async () => Get(BASE),
  lookups: async () => Get(`${BASE}/lookups`),
  insert: async (data) => Post(`${BASE}/insert`, data),
  // The key travels separately from the values: both key parts are editable.
  update: async (key, values) => Post(`${BASE}/update`, { key, values }),
  delete: async (key) => Post(`${BASE}/delete`, key),
};

export default Service;
