import { Get, Post } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/observingcapabilities"),
  update: async (data) => Post("/api/management/observingcapabilities/update", data),
  insert: async (data) => Post("/api/management/observingcapabilities/insert", data),
  delete: async (data) => Post("/api/management/observingcapabilities/delete", data)
};

export default Service;
