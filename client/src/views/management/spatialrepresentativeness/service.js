import { Get, Post, Upload, DownloadGet } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/spatialrepresentativeness"),
  lookups: async () => Get("/api/management/spatialrepresentativeness/lookups"),
  insert: async (data) => Post("/api/management/spatialrepresentativeness/insert", data),
  update: async (data) => Post("/api/management/spatialrepresentativeness/update", data),
  delete: async (data) => Post("/api/management/spatialrepresentativeness/delete", data),
  parseFile: async (form) => Upload("/api/management/spatialrepresentativeness/parse", form),
  getById: async (srsApplicationId) =>
    Get(`/api/management/spatialrepresentativeness/${encodeURIComponent(srsApplicationId)}`),
  // The applications only: an area's grid cells come from a spatial file in the form.
  upload: async (data) => Upload("/api/management/spatialrepresentativeness/import", data),
  download: async () => DownloadGet("/api/management/spatialrepresentativeness/export")
};

export default Service;
