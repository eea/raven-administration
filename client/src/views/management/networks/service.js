import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/networks"),
  update: async (data) => Post("/api/management/networks/update", data),
  insert: async (data) => Post("/api/management/networks/insert", data),
  delete: async (data) => Post("/api/management/networks/delete", data),
  authorities: async () => Get("/api/management/networks/authorities"),
  levels: async () => Get("/api/management/networks/levels"),
  media: async () => Get("/api/management/networks/media"),
  timezones: async () => Get("/api/management/networks/timezones")
};

export default Service;
