import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/aqi"),
  pollutants: async () => Get("/api/management/lookups/aqipollutants"),
  timesteps: async () => Get("/api/management/lookups/timesteps"),
  save: async (data) => Post("/api/management/aqi/save", data)
};

export default Service;
