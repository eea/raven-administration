import { Get, Post, File } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/stations"),
  update: async (data) => Post("/api/management/stations/update", data),
  insert: async (data) => Post("/api/management/stations/insert", data),
  delete: async (data) => Post("/api/management/stations/delete", data),
  upload: async (data) => File("/api/imports/stations", data),

  media: async () => Get("/api/management/lookups/media"),
  networks: async () => Get("/api/management/lookups/networks"),
  areaclassifications: async () => Get("/api/management/lookups/areaclassifications"),
  measurementregimes: async () => Get("/api/management/lookups/measurementregimes")
};

export default Service;
