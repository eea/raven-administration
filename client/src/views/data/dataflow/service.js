import { Get, Post, Download, DownloadWithHeaders } from "../../../helpers/request";

const Service = {
  // The export list comes from the AQR3 registry on the server, so adding a
  // reporting table needs no frontend change.
  tables: async () => Get("/api/dataflow/csv/tables"),
  getAvailableYears: async () => Get("/api/dataflow/csv/available_years"),

  downloadTable: async (code, year) =>
    Download(`/api/dataflow/csv/${code}`, year ? { year } : {}),

  // Returns the response, not just the file: X-AQR3-Empty lists the tables that
  // exported as a header row only.
  downloadAll: async (year) =>
    DownloadWithHeaders("/api/dataflow/csv/download_all", year ? { year } : {}),

  // CAM is derived rather than entered, so it has to be refreshed before export.
  recalculateCompliance: async (year) =>
    Post("/api/dataflow/compliance/recalculate", { year })
};

export default Service;
