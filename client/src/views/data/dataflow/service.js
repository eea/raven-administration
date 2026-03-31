import { Get, Download } from "../../../helpers/request";
import axios from "axios";

const Service = {
  // Old XML-based dataflows (kept for reference)
  dataflow: async (type, year, timezone, description) => Get(`/api/dataflow?type=${type}&year=${year}&timezone=${timezone}&description=${description}`),
  dataflowE2A: async (lastRequest) => Get(`/api/dataflow/e2a?last_request=${lastRequest}`),
  dataflowReportnet3: async (type, year, timezone, description) => {
    const response = await axios.get(`/api/dataflow/reportnet3/csv?type=${type}&year=${year}&timezone=${timezone}&description=${description}`, { responseType: "arraybuffer" });
    return new Blob([response.data], { type: "application/zip" });
  },
  
  // New CSV Dataflow exports (using Download helper like authorities module)
  getAvailableYears: async () => Get("/api/dataflow/csv/available_years"),
  downloadAuthorities: async () => Download("/api/dataflow/csv/authorities"),
  downloadStations: async () => Download("/api/dataflow/csv/stations"),
  downloadSamplingPoints: async () => Download("/api/dataflow/csv/samplingpoints"),
  downloadProcesses: async () => Download("/api/dataflow/csv/processes"),
  downloadMeasurements: async (year) => Download("/api/dataflow/csv/measurements", { year }),
  downloadZoneGeometry: async () => Download("/api/dataflow/csv/zonegeometry"),
  downloadSpatialRepresentativeness: async () => Download("/api/dataflow/csv/spatialrepresentativeness"),
  downloadSrAreaInline: async () => Download("/api/dataflow/csv/srareainline"),
  downloadAll: async (year) => Download("/api/dataflow/csv/download_all", year ? { year } : {})
};

export default Service;
