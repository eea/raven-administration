import { Get, Post } from "../../../helpers/request";

const Service = {
  evaluate: async (data) => Post("/api/data/exceedances/evaluate", data),
  years: async () => Get("/api/data/exceedances/years"),
  samplingPoints: async (pollutant) => Get(`/api/data/exceedances/sampling_points${pollutant ? '?pollutant=' + pollutant : ''}`),
  directives: async () => Get("/api/data/exceedances/directives"),
  pollutants: async (directive) => Get(`/api/data/exceedances/pollutants?directive=${directive}`)
};

export default Service;
