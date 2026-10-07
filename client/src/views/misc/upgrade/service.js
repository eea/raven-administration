import { Get, Post } from "../../../helpers/request";

const Service = {
  tasks: async () => Get("/api/management/upgrade/tasks"),
  repairRegimeId: async (id) => Post("/api/management/assessmentregimes/repair-id", { id })
};

export default Service;
