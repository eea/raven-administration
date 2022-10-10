import { Get, Post } from "../../../helpers/request";

const Service = {
  timeseries: async () => Get("/api/processing/scale/timeseries")
};

export default Service;
