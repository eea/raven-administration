import { Get, Post, Download } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/processing/convert"),
  update: async (data) => Post("/api/processing/convert/update", data),
  insert: async (data) => Post("/api/processing/convert/insert", data),
  delete: async (data) => Post("/api/processing/convert/delete", data),
  download: async () => Download("/api/processing/convert/download"),
  units: async () => Get("/api/processing/convert/units"),
  timeseries: async () => Get("/api/processing/convert/timeseries")
};

export default Service;
