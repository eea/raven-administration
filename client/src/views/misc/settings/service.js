import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/misc/settings"),
  lookups: async () => Get("/api/misc/settings/lookups"),
  save: async (data) => Post("/api/misc/settings/save", data)
};

export default Service;
