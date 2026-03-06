import { Get, Post } from "../../../helpers/request";

const Service = {
  years: async () => Get("/api/management/assessmentregimezones/years"),
  get: async (data) => Post("/api/management/assessmentregimezones", data),
  updateRows: async (data) => Post("/api/management/assessmentregimezones/update-rows", data),
  getExceedanceOptions: async () => Get("/api/management/assessmentregimezones/exceedance-options"),
  getDocumentOptions: async () => Get("/api/management/assessmentregimezones/document-options")
};

export default Service;
