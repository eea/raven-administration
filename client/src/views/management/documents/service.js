import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/documents"),
  lookups: async () => Get("/api/management/documents/lookups"),
  update: async (data) => Post("/api/management/documents/update", data),
  insert: async (data) => Post("/api/management/documents/insert", data),
  delete: async (data) => Post("/api/management/documents/delete", data)
};

export default Service;
