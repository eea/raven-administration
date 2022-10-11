import { Get, Post } from "../../../helpers/request";

const Service = {
  timeseries: async () => Get("/api/processing/scale/timeseries"),
  scalingpoints: async (data) => Post("/api/processing/scale/scaling_points", data)
};

export default Service;
