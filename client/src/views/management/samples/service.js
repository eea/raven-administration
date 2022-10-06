import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/samples"),
  update: async (data) => Post("/api/management/samples/update", data),
  insert: async (data) => Post("/api/management/samples/insert", data),
  delete: async (data) => Post("/api/management/samples/delete", data)
};

export default Service;
