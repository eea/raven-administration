import { Get, Post, Upload , DownloadGet } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/stations"),
  lookups: async () => Get("/api/management/stations/lookups"),
  update: async (data) => Post("/api/management/stations/update", data),
  insert: async (data) => Post("/api/management/stations/insert", data),
  delete: async (data) => Post("/api/management/stations/delete", data),
  upload: async (data) => Upload("/api/imports/stations", data),
  download: async () => DownloadGet("/api/exports/stations")
};

export default Service;
