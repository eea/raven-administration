import { Get, Post, Upload , DownloadGet } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/zones"),
  insert: async (data) => Post("/api/management/zones/add", data),
  update: async (data) => Post("/api/management/zones/update", data),
  delete: async (data) => Post("/api/management/zones/delete", data),
  upload: async (data) => Upload("/api/imports/zones", data),
  download: async () => DownloadGet("/api/exports/zones"),

  zone_types: async () => Get("/api/management/lookups/zones_types"),
  zone_categories: async () => Get("/api/management/lookups/zones_categories")
};

export default Service;
