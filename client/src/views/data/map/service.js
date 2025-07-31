import { Get } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/data/map"),
  legend: async () => Get("/api/data/map/legend")
};

export default Service;
