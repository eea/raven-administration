import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/misc/notifications"),
  missing_values: async () => Get("/api/misc/notifications/missing_values"),
  sampling_points: async () => Get("/api/misc/notifications/sampling_points"),
  save: async (data) => Post("/api/misc/notifications/save", data),
  delete: async (data) => Post("/api/misc/notifications/delete", data),
  logs: async () => Get("/api/misc/notifications/logs")
};

export default Service;
