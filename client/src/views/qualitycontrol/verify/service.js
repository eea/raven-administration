import { Get, Post } from "../../../helpers/request";

const Service = {
  datasets: async (data) => Post("/api/qualitycontrol/verify/datasets", data),
  stations: async () => Get("/api/qualitycontrol/verify/stations"),
  flag: async (data) => Post("/api/qualitycontrol/verify/flag", data)
  // `log` moved to components/observationlog/service.js — the history popup fetches
  // and pages itself now, so the view no longer pre-fetches rows for it.
};

export default Service;
