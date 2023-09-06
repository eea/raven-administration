import { Get } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/data/map")
};

export default Service;
