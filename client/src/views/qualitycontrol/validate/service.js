import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async (data) => Post("/api/qualitycontrol/validate/timevalues", data),
  timeseries: async () => Get("/api/qualitycontrol/validate/timeseries"),
  validate: async (data) => Post("/api/qualitycontrol/validate/flag", data)
  // `log` moved to components/observationlog/service.js, where the page size is a
  // prop rather than a hardcoded limit=10.
};

export default Service;
