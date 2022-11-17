import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/attainments"),
  update: async (data) => Post("/api/management/attainments/update", data),
  insert: async (data) => Post("/api/management/attainments/insert", data),
  delete: async (data) => Post("/api/management/attainments/delete", data),

  assessment_regimes: async () => Get("/api/management/lookups/assessmentregimes")
};

export default Service;
