import { Get, Post, Upload , DownloadGet } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/samplingpoints"),
  update: async (data) => Post("/api/management/samplingpoints/update", data),
  insert: async (data) => Post("/api/management/samplingpoints/insert", data),
  delete: async (data) => Post("/api/management/samplingpoints/delete", data),
  upload: async (data) => Upload("/api/imports/sampling_points", data),
  download: async () => DownloadGet("/api/exports/sampling_points"),

  lookups: async () => Get("/api/management/samplingpoints/lookups")
};

export default Service;
