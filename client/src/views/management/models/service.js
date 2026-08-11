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
    Upload(`/api/management/models/${modelId}/results`, form)
};

export default Service;
