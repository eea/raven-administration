import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/authorities"),
  update: async (data) => Post("/api/management/authorities/update", data),
  insert: async (data) => Post("/api/management/authorities/insert", data),
  delete: async (data) => Post("/api/management/authorities/delete", data)
};

export default Service;
