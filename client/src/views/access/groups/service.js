import { Get, Post } from "../../../helpers/request";

const Service = {
  groups: async () => Get("/api/access/groups"),
  networks: async () => Get("/api/access/networks"),
  insert: async (data) => Post("/api/access/groups/insert", data),
  update: async (data) => Post("/api/access/groups/update", data),
  delete: async (data) => Post("/api/access/groups/delete", data)
};

export default Service;
