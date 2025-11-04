const nullFormatter = (params) => (params.value == null ? "-" : params.value);

export const columns = [
  { field: "network", headerName: "Network", flex: 1 },
  { field: "eoi", headerName: "EOI", flex: 1 },
  { field: "station", headerName: "Station", flex: 1 },
  { field: "spo", headerName: "SPO", flex: 1 },
  { field: "pollutant", headerName: "Pollutant", flex: 1 },
  { field: "aggregation_process", headerName: "Aggregation Process", flex: 1 },
  { field: "year", headerName: "Year", flex: 1 },
  { field: "value", headerName: "Level", flex: 1, valueFormatter: nullFormatter },
  { field: "coverage", headerName: "Coverage", flex: 1, valueFormatter: nullFormatter }
];
