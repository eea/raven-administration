import { Get, Post, Upload, Download } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/zones"),
  update: async (data) => Post("/api/management/zones/update", data),
  delete: async (data) => Post("/api/management/zones/delete", data),
  upload: async (data) => Upload("/api/imports/zones", data),
  download: async () => Download("/api/exports/zones"),

  authorities: async () => Get("/api/management/lookups/authorities"),
  zone_types: async () => Get("/api/management/lookups/zones_types")
};

export default Service;
