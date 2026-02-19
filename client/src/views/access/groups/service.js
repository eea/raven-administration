import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/access/groups"),
  networks: async () => Get("/api/access/networks"),
  insert: async (data) => Post("/api/access/groups/insert", data),
  update: async (data) => Post("/api/access/groups/update", data),
  delete: async (data) => {
    // Manager sends { ids: [...] }, but backend expects { id: ... }
    const id = Array.isArray(data.ids) ? data.ids[0] : data.id;
    return Post("/api/access/groups/delete", { id });
  }
};

export default Service;
