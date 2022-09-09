import { Get, Post } from "../../../helpers/request";

const Service = {
  dataflow: async (type, year, timezone, description) => Get(`/api/dataflow?type=${type}&year=${year}&timezone=${timezone}&description=${description}`),
  dataflowE2A: async (lastRequest) => Get(`/api/dataflow/e2a?last_request=${lastRequest}`)
};

export default Service;
