import { Get, Post, File } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/authorities"),
  update: async (data) => Post("/api/management/authorities/update", data),
  insert: async (data) => Post("/api/management/authorities/insert", data),
  delete: async (data) => Post("/api/management/authorities/delete", data),
  upload: async (data) => File("/api/imports/authorities", data)
};

export default Service;
