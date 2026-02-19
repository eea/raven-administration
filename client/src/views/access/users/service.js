import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/access/users"),
  groups: async () => Get("/api/access/groups"),
  insert: async (data) => Post("/api/access/users/insert", data),
  update: async (data) => Post("/api/access/users/update", data),
  delete: async (data) => {
    // Manager sends { ids: [...] }, but backend expects { id: ... }
    const id = Array.isArray(data.ids) ? data.ids[0] : data.id;
    return Post("/api/access/users/delete", { id });
  }
};

export default Service;
