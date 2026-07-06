import { Get, Post } from "../../helpers/request";

const Service = {
  list: async () => Get("/api/data/favorites"),
  insert: async (data) => Post("/api/data/favorites/insert", data),
  update: async (data) => Post("/api/data/favorites/update", data),
  delete: async (data) => Post("/api/data/favorites/delete", data)
};

export default Service;
