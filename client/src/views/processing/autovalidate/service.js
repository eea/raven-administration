import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/processing/autovalidate"),
  update: async (data) => Post("/api/processing/autovalidate/update", data),
  insert: async (data) => Post("/api/processing/autovalidate/insert", data),
  delete: async (data) => Post("/api/processing/autovalidate/delete", data),
  pollutants: async () => Get("/api/processing/autovalidate/pollutants")
};

export default Service;
