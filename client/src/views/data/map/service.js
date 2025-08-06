import { Get } from "../../../helpers/request";

const Service = {
  get: async (aqi_type) => Get(`/api/data/map?aqi_type=${aqi_type}`),
  legend: async () => Get(`/api/data/map/legend`)
};

export default Service;
