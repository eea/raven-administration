import { Get, Post, Upload, DownloadGet } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/documents"),
  lookups: async () => Get("/api/management/documents/lookups"),
  update: async (data) => Post("/api/management/documents/update", data),
  insert: async (data) => Post("/api/management/documents/insert", data),
  delete: async (data) => Post("/api/management/documents/delete", data),
  upload: async (data) => Upload("/api/imports/documents", data),
  download: async () => DownloadGet("/api/exports/documents")
};

export default Service;
