import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/zones"),
  update: async (data) => Post("/api/management/zones/update", data),
  insert: async (data) => Post("/api/management/zones/insert", data),
  delete: async (data) => Post("/api/management/zones/delete", data),
  authorities: async () => Get("/api/management/zones/authorities"),
  types: async () => Get("/api/management/zones/types")
};

export default Service;
