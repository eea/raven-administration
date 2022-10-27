import { Get, Post } from "../../../helpers/request";

const Service = {
  users: async () => Get("/api/access/users"),
  groups: async () => Get("/api/access/groups"),
  insert: async (data) => Post("/api/access/users/insert", data),
  update: async (data) => Post("/api/access/users/update", data),
  delete: async (data) => Post("/api/access/users/delete", data)
};

export default Service;
