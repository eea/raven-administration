import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/misc/aqi"),
  pollutants: async () => Get("/api/management/lookups/aqipollutants"),
  timesteps: async () => Get("/api/management/lookups/timesteps"),
  save: async (data) => Post("/api/misc/aqi/save", data)
};

export default Service;
