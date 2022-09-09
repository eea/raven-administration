import { Get, Post } from "../../../helpers/request";

const Service = {
  timezones: async () => Get("/api/data/dataflow/timezones"),
  dataflow: async () => Post("/api/data/dataflow/")
};

export default Service;
