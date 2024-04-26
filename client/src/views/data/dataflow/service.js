import { Get, Post } from "../../../helpers/request";
import axios from "axios";

const Service = {
  dataflow: async (type, year, timezone, description) => Get(`/api/dataflow?type=${type}&year=${year}&timezone=${timezone}&description=${description}`),
  dataflowE2A: async (lastRequest) => Get(`/api/dataflow/e2a?last_request=${lastRequest}`),
  dataflowReportnet3: async (type, year, timezone, description) => {
    const response = await axios.get(`/api/dataflow/reportnet3/csv?type=${type}&year=${year}&timezone=${timezone}&description=${description}`, { responseType: "arraybuffer" });
    return new Blob([response.data], { type: "application/zip" });
  },
  showReportnet3: async () => Get(`/api/dataflow/showreportnet3`)
};

export default Service;
