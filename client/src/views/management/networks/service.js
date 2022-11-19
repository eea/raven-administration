import { Get, Post, File } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/networks"),
  update: async (data) => Post("/api/management/networks/update", data),
  insert: async (data) => Post("/api/management/networks/insert", data),
  delete: async (data) => Post("/api/management/networks/delete", data),
  upload: async (data) => File("/api/imports/networks", data),

  authorities: async () => Get("/api/management/lookups/authorities"),
  levels: async () => Get("/api/management/lookups/levels"),
  media: async () => Get("/api/management/lookups/media"),
  timezones: async () => Get("/api/management/lookups/timezones")
};

export default Service;
