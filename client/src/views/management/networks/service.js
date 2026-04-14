import { Get, Post, Upload , DownloadGet } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/networks"),
  lookups: async () => Get("/api/management/networks/lookups"),
  update: async (data) => Post("/api/management/networks/update", data),
  insert: async (data) => Post("/api/management/networks/insert", data),
  delete: async (data) => Post("/api/management/networks/delete", data),
  upload: async (data) => Upload("/api/imports/networks", data),
  download: async () => DownloadGet("/api/exports/networks")
};

export default Service;
