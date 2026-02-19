import { Get, Post, Download } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/processing/calculate"),
  update: async (data) => Post("/api/processing/calculate/update", data),
  insert: async (data) => Post("/api/processing/calculate/insert", data),
  delete: async (data) => Post("/api/processing/calculate/delete", data),
  download: async () => Download("/api/processing/calculate/download"),
  timeseries: async () => Get("/api/processing/calculate/timeseries")
};

export default Service;
