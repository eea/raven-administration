import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/assessmentregimes"),
  insert: async (data) => Post("/api/management/assessmentregimes/insert", data),
  update: async (data) => Post("/api/management/assessmentregimes/update", data),
  delete: async (data) => Post("/api/management/assessmentregimes/delete", data),
  lookups: async () => Get("/api/management/assessmentregimes/lookups"),
};

export default Service;
