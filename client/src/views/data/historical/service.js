import { Get, Post, Download } from "../../../helpers/request";

const Service = {
  get: async (data) => Post("/api/data/historical", data),
  timeseries: async () => Get("/api/data/historical/timeseries"),
  download: async (data) => Download("/api/exports/observations", data)
};

export default Service;
