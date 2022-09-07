import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async (data) => Post("/api/qualitycontrol/validate/timevalues", data),
  timeseries: async () => Get("/api/qualitycontrol/validate/timeseries"),
  validate: async (data) => Post("/api/qualitycontrol/validate/flag", data)
};

export default Service;
