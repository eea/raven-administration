import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/samplingpoints"),
  update: async (data) => Post("/api/management/samplingpoints/update", data),
  insert: async (data) => Post("/api/management/samplingpoints/insert", data),
  delete: async (data) => Post("/api/management/samplingpoints/delete", data)
};

export default Service;
