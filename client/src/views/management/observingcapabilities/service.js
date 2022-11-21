import { Get, Post, Upload, Download } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/observingcapabilities"),
  update: async (data) => Post("/api/management/observingcapabilities/update", data),
  insert: async (data) => Post("/api/management/observingcapabilities/insert", data),
  delete: async (data) => Post("/api/management/observingcapabilities/delete", data),
  upload: async (data) => Upload("/api/imports/observing_capabilities", data),
  download: async () => Download("/api/exports/observing_capabilities"),

  sampling_points: async () => Get("/api/management/lookups/samplingpoints"),
  samples: async () => Get("/api/management/lookups/samples"),
  processes: async () => Get("/api/management/lookups/processes"),
  result_nature_values: async () => Get("/api/management/lookups/resultnaturevalues"),
  processtype_values: async () => Get("/api/management/lookups/processtypevalues")
};

export default Service;
