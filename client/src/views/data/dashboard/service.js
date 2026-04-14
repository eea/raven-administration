import { Get, Post } from "../../../helpers/request";

const Service = {
  samplingPoints: async () => Get("/api/data/dashboard/sampling_points"),
  get:            async (data) => Post("/api/data/dashboard", data),
};

export default Service;
