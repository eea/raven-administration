import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/preaggregation"),
  update: async () => Get("/api/management/preaggregation/update")
};

export default Service;
