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
  // A regime's assessment methods (AQR3 CAM_05), edited row by row through the
  // Assessment data API. Never replaced as a set: v3 did that, and the delete half
  // cascaded away the exceedingmethods rows hanging off each link.
  links: async (regime) => Get(`/api/management/assessmentdata?regime=${encodeURIComponent(regime)}`),
  linkLookups: async () => Get("/api/management/assessmentdata/lookups"),
  linkCandidates: async (regime) => Get(`/api/management/assessmentdata/candidates?regime=${encodeURIComponent(regime)}`),
  linkMany: async (rows) => Post("/api/management/assessmentdata/insert-many", { rows }),
  updateLink: async (data) => Post("/api/management/assessmentdata/update", data),
  deleteLink: async (id) => Post("/api/management/assessmentdata/delete", { ids: [id] }),
};

export default Service;
