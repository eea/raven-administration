import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/assessmentdata"),
  insert: async (data) => Post("/api/management/assessmentdata/insert", data),
  update: async (data) => Post("/api/management/assessmentdata/update", data),
  delete: async (data) => Post("/api/management/assessmentdata/delete", data),
  lookups: async () => Get("/api/management/assessmentdata/lookups")
};

export default Service;
