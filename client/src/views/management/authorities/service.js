import { Get, Post, Upload, Download } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/authorities"),
  update: async (data) => Post("/api/management/authorities/update", data),
  insert: async (data) => Post("/api/management/authorities/insert", data),
  delete: async (data) => Post("/api/management/authorities/delete", data),
  upload: async (data) => Upload("/api/imports/authorities", data),
  download: async () => Download("/api/exports/authorities")
};

export default Service;
