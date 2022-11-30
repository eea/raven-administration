import { Get, Post, Upload, Download } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/assessmentregimes"),
  update: async (data) => Post("/api/management/assessmentregime/update", data),
  insert: async (data) => Post("/api/management/assessmentregime/insert", data),
  delete: async (data) => Post("/api/management/assessmentregime/delete", data),
  upload: async (data) => Upload("/api/imports/assessmentregime", data),
  download: async () => Download("/api/exports/assessmentregime"),

  zones: async () => Get("/api/management/lookups/zones"),
  pollutants: async () => Get("/api/management/lookups/pollutants"),
  assessment_types: async () => Get("/api/management/lookups/assessmenttypes"),
  object_types: async () => Get("/api/management/lookups/objecttypes"),
  reporting_metrics: async () => Get("/api/management/lookups/reportingmetrics"),
  protection_targets: async () => Get("/api/management/lookups/protectiontargets"),
  exceedances: async () => Get("/api/management/lookups/assessmentexceedances"),
  sampling_points: async () => Get("/api/management/assessmentregime/samplingpoints")
};

export default Service;
