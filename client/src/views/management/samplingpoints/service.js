import { Get, Post, Upload, Download } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/samplingpoints"),
  update: async (data) => Post("/api/management/samplingpoints/update", data),
  insert: async (data) => Post("/api/management/samplingpoints/insert", data),
  delete: async (data) => Post("/api/management/samplingpoints/delete", data),
  upload: async (data) => Upload("/api/imports/sampling_points", data),
  download: async () => Download("/api/exports/sampling_points"),

  media: async () => Get("/api/management/lookups/media"),
  stations: async () => Get("/api/management/lookups/stations"),
  pollutants: async () => Get("/api/management/lookups/pollutants"),
  timesteps: async () => Get("/api/management/lookups/timesteps"),
  assessmenttypes: async () => Get("/api/management/lookups/assessmenttypes"),
  stationclassifications: async () => Get("/api/management/lookups/stationclassifications"),
  concentrations: async () => Get("/api/management/lookups/concentrations"),
  measurementregimes: async () => Get("/api/management/lookups/measurementregimes")
};

export default Service;
