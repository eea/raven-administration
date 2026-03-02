import { Get, Post, Upload, Download } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/networks"),
  lookups: async () => Get("/api/management/networks/lookups"),
  update: async (data) => Post("/api/management/networks/update", data),
  insert: async (data) => Post("/api/management/networks/insert", data),
  delete: async (data) => Post("/api/management/networks/delete", data),
  upload: async (data) => Upload("/api/imports/networks", data),
  download: async () => Download("/api/exports/networks")
};

export default Service;
