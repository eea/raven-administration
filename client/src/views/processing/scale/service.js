import { Get, Post } from "../../../helpers/request";

const Service = {
  timeseries: async () => Get("/api/processing/scale/timeseries"),
  scalingpoints: async (data) => Post("/api/processing/scale/scaling_points", data),
  insert: async (data) => Post("/api/processing/scale/scaling_points/insert", data),
  update: async (data) => Post("/api/processing/scale/scaling_points/update", data),
  delete: async (data) => Post("/api/processing/scale/scaling_points/delete", data),
  preview: async (data) => Post("/api/processing/scale/scaling_points/preview", data)
};

export default Service;
