import { Get, Post, Upload , DownloadGet } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/processes"),
  update: async (data) => Post("/api/management/processes/update", data),
  insert: async (data) => Post("/api/management/processes/insert", data),
  delete: async (data) => Post("/api/management/processes/delete", data),
  upload: async (data) => Upload("/api/imports/processes", data),
  download: async () => DownloadGet("/api/exports/processes"),

  lookups: async () => Get("/api/management/processes/lookups")
};

export default Service;
