import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async (data) => Post("/api/data/statistics/values", data),
  years: async () => Get("/api/data/statistics/years"),
  pollutants_and_aggregationprocess: async () => Get("/api/data/statistics/pollutants_and_aggregationprocess")
};

export default Service;
