import { Get, Post, Upload , DownloadGet } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/samplingpoints"),
  update: async (data) => Post("/api/management/samplingpoints/update", data),
  insert: async (data) => Post("/api/management/samplingpoints/insert", data),
  delete: async (data) => Post("/api/management/samplingpoints/delete", data),
  upload: async (data) => Upload("/api/imports/sampling_points", data),
  download: async () => DownloadGet("/api/exports/sampling_points"),

  lookups: async () => Get("/api/management/samplingpoints/lookups"),

  logList: async (samplingPointId, type = null) => {
    const params = new URLSearchParams({ sampling_point_id: samplingPointId });
    if (type) params.append("type", type);
    return Get(`/api/management/samplingpoints/log?${params}`);
  },
  logInsert: async (data) => Post("/api/management/samplingpoints/log/insert", data),
  logDailyCheckState: async (ids) => Get(`/api/management/samplingpoints/log/daily_check_state?ids=${ids.join(",")}`),
};

export default Service;
