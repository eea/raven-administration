import { Get, Post, Upload , DownloadGet } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/authorities"),
  lookups: async () => Get("/api/management/authorities/lookups"),
  // The key travels separately from the values: all three key parts are editable.
  update: async (key, values) => Post("/api/management/authorities/update", { key, values }),
  insert: async (data) => Post("/api/management/authorities/insert", data),
  delete: async (data) => Post("/api/management/authorities/delete", data),
  upload: async (data) => Upload("/api/imports/authorities", data),
  download: async () => DownloadGet("/api/exports/authorities")
};

export default Service;
