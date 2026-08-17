import { Get, Post, Upload } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/models"),
  insert: async (data) => Post("/api/management/models/insert", data),
  update: async (data) => Post("/api/management/models/update", data),
  delete: async (data) => Post("/api/management/models/delete", data),

  lookups: async () => Get("/api/management/models/lookups"),

  // Gridded results (AQR3 MOEResultInline): a GeoTIFF for one timestep, snapped
  // onto the EEA INSPIRE grid in EPSG:3035.
  uploadResults: async (modelId, form) =>
    Upload(`/api/management/models/${modelId}/results`, form),

  // External gridded results (AQR3 MOEResultExternal): one row per timestep,
  // naming a GeoTIFF the country uploads to Reportnet3 itself.
  externalList: async (modelId) => Get(`/api/management/models/${modelId}/external-results`),
  externalInsert: async (modelId, data) =>
    Post(`/api/management/models/${modelId}/external-results/insert`, data),
  // The key travels separately: start_time and the aggregation process are both
  // part of the AQR3 key and editable.
  externalUpdate: async (modelId, key, values) =>
    Post(`/api/management/models/${modelId}/external-results/update`, { key, values }),
  externalDelete: async (modelId, key) =>
    Post(`/api/management/models/${modelId}/external-results/delete`, key)
};

export default Service;
