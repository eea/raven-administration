import { Get, Post, Upload, DownloadGet } from "../../../helpers/request";

const BASE = "/api/management/pollutionleveladjustment";

const Service = {
  get: async () => Get(BASE),
  lookups: async () => Get(`${BASE}/lookups`),
  insert: async (data) => Post(`${BASE}/insert`, data),
  // The key travels separately from the values: both key parts are editable.
  update: async (key, values) => Post(`${BASE}/update`, { key, values }),
  delete: async (key) => Post(`${BASE}/delete`, key),
  // One adjustment per row, checked like the form; the export is also the template.
  upload: async (data) => Upload(`${BASE}/import`, data),
  download: async () => DownloadGet(`${BASE}/export`),
};

export default Service;
