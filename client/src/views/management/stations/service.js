import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/stations"),
  update: async (data) => Post("/api/management/stations/update", data),
  insert: async (data) => Post("/api/management/stations/insert", data),
  delete: async (data) => Post("/api/management/stations/delete", data),
  // authorities: async () => Get("/api/management/stations/authorities"),
  // levels: async () => Get("/api/management/stations/levels"),
  media: async () => Get("/api/management/stations/media")
  // timezones: async () => Get("/api/management/stations/timezones")
};

export default Service;
