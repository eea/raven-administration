import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/misc/settings"),
  update: async (data) => Post("/api/misc/settings/update", data)
};

export default Service;
