import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/settings"),
  update: async (data) => Post("/api/management/settings/update", data)
};

export default Service;
