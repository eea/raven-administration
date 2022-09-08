import { Get, Post } from "../../../helpers/request";

const Service = {
  datasets: async (data) => Post("/api/qualitycontrol/verify/datasets", data),
  stations: async () => Get("/api/qualitycontrol/verify/stations"),
  flag: async (data) => Post("/api/qualitycontrol/verify/flag", data)
};

export default Service;
