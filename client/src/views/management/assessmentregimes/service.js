import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/assessmentregimes"),
  update: async (data) => Post("/api/management/assessmentregime/update", data),
  insert: async (data) => Post("/api/management/assessmentregime/insert", data),
  delete: async (data) => Post("/api/management/assessmentregime/delete", data)
};

export default Service;
