import { Get } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/data/latest")
};

export default Service;
