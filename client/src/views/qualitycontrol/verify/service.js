import { Get, Post } from "../../../helpers/request";

const Service = {
  datasets: async (data) => Post("/api/qualitycontrol/verify/datasets", data),
  stations: async () => Get("/api/qualitycontrol/verify/stations"),
  flag: async (data) => Post("/api/qualitycontrol/verify/flag", data),
  log: async (sampling_point_id, from_dt, to_dt) =>
    Get(`/api/qualitycontrol/log?sampling_point_id=${encodeURIComponent(sampling_point_id)}&from_dt=${encodeURIComponent(from_dt)}&to_dt=${encodeURIComponent(to_dt)}`)
};

export default Service;
