import { Get, Post, Upload, DownloadGet } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/assessmentdata"),
  insert: async (data) => Post("/api/management/assessmentdata/insert", data),
  update: async (data) => Post("/api/management/assessmentdata/update", data),
  delete: async (data) => Post("/api/management/assessmentdata/delete", data),
  lookups: async () => Get("/api/management/assessmentdata/lookups"),
  // The wizard: every regime of a year x the sampling points inside its zone.
  candidatesYear: async (year) => Get(`/api/management/assessmentdata/candidates-year?year=${year}`),
  insertMany: async (rows) => Post("/api/management/assessmentdata/insert-many", { rows }),
  // One link per row, checked like the form; the export is also the template.
  upload: async (data) => Upload("/api/management/assessmentdata/import", data),
  download: async () => DownloadGet("/api/management/assessmentdata/export")
};

export default Service;
