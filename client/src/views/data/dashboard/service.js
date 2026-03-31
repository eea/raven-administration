import { Get, Post } from "../../../helpers/request";

const Service = {
  timeseries: async () => Get("/api/data/historical/timeseries"),
  get:        async (data) => Post("/api/data/historical", data),
};

export default Service;
