import { Get, Post, Upload } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/spatialrepresentativeness"),
  lookups: async () => Get("/api/management/spatialrepresentativeness/lookups"),
  insert: async (data) => Post("/api/management/spatialrepresentativeness/insert", data),
  update: async (data) => Post("/api/management/spatialrepresentativeness/update", data),
  delete: async (data) => Post("/api/management/spatialrepresentativeness/delete", data),
  parseFile: async (form) => Upload("/api/management/spatialrepresentativeness/parse", form),
  getById: async (id) => Get(`/api/management/spatialrepresentativeness/${id}`)
};

export default Service;
