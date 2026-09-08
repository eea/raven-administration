import { Get, Post, Upload , DownloadGet } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/processes"),
  // The key travels separately from the values: all three key parts are editable.
  update: async (key, values) => Post("/api/management/processes/update", { key, values }),
  insert: async (data) => Post("/api/management/processes/insert", data),
  delete: async (key) => Post("/api/management/processes/delete", key),
  upload: async (data) => Upload("/api/imports/processes", data),
  download: async () => DownloadGet("/api/exports/processes"),

  lookups: async () => Get("/api/management/processes/lookups")
};

export default Service;
