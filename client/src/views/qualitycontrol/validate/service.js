import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async (data) => Post("/api/qualitycontrol/validate/timevalues", data),
  timeseries: async () => Get("/api/qualitycontrol/validate/timeseries"),
  validate: async (data) => Post("/api/qualitycontrol/validate/flag", data),
  log: async (sampling_point_id, from_dt, to_dt, offset = 0) =>
    Get(`/api/qualitycontrol/log?sampling_point_id=${encodeURIComponent(sampling_point_id)}&from_dt=${encodeURIComponent(from_dt)}&to_dt=${encodeURIComponent(to_dt)}&limit=10&offset=${offset}`)
};

export default Service;
