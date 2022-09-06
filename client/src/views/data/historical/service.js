import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async (data) => Post("/api/data/historical", data),
  timeseries: async () => Get("/api/data/historical/timeseries")
};

export default Service;
