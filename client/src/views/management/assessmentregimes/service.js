import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/assessmentregimes"),
  insert: async (data) => Post("/api/management/assessmentregimes/insert", data),
  update: async (data) => Post("/api/management/assessmentregimes/update", data),
  delete: async (data) => Post("/api/management/assessmentregimes/delete", data),
  lookups: async () => Get("/api/management/assessmentregimes/lookups"),
  // Bulk fill, inherited from the retired assessmentregimezones grid.
  candidates: async (year) => Get(`/api/management/assessmentregimes/candidates?year=${year}`),
  generate: async (data) => Post("/api/management/assessmentregimes/generate", data),
};

export default Service;
