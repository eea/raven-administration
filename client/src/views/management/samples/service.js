import { Get, Post, Upload, Download } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/samples"),
  update: async (data) => Post("/api/management/samples/update", data),
  insert: async (data) => Post("/api/management/samples/insert", data),
  delete: async (data) => Post("/api/management/samples/delete", data),
  upload: async (data) => Upload("/api/imports/samples", data),
  download: async () => Download("/api/exports/samples")
};

export default Service;
