import { Get, Post, Upload, Download } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/exceedances"),
  update: async (data) => Post("/api/management/exceedances/update", data),
  insert: async (data) => Post("/api/management/exceedances/insert", data),
  delete: async (data) => Post("/api/management/exceedances/delete", data),
  upload: async (data) => Upload("/api/imports/exceedances", data),
  download: async () => Download("/api/exports/exceedances"),

  attainments: async () => Get("/api/management/lookups/attainments"),
  exceedance_descriptions: async () => Get("/api/management/lookups/exceedancedescriptions"),
  exceedance_types: async () => Get("/api/management/lookups/exceedancetypes"),
  area_classifications: async () => Get("/api/management/lookups/areaclassifications"),
  adjustment_types: async () => Get("/api/management/lookups/adjustmenttypes"),
  adjustment_source_types: async () => Get("/api/management/lookups/adjustmentsourcetypes"),
  reasons: async () => Get("/api/management/lookups/reasons"),
  sampling_points: async () => Get("/api/management/exceedances/samplingpoints")
};

export default Service;
