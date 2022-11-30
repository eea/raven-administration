import { Get, Post, Upload, Download } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/attainments"),
  update: async (data) => Post("/api/management/attainments/update", data),
  insert: async (data) => Post("/api/management/attainments/insert", data),
  delete: async (data) => Post("/api/management/attainments/delete", data),
  upload: async (data) => Upload("/api/imports/attainments", data),
  download: async () => Download("/api/exports/attainments"),

  assessment_regimes: async () => Get("/api/management/lookups/assessmentregimes")
};

export default Service;
