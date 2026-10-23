import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/misc/preaggregation"),
  update: async () => Get("/api/misc/preaggregation/update"),
  status: async () => Get("/api/misc/preaggregation/status")
};

export default Service;
