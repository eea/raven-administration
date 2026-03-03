export const columns = [
  {
    headerName: "Air Quality Station Name",
    field: "station",
    filter: "agTextColumnFilter",
    sortable: true,
    pinned: "left",
    width: 200
  },
  {
    headerName: "Air Quality Network",
    field: "network",
    filter: "agTextColumnFilter",
    sortable: true,
    width: 180
  },
  {
    headerName: "Air Quality Station Code",
    field: "eoi",
    filter: "agTextColumnFilter",
    sortable: true,
    width: 200
  },
  {
    headerName: "Year",
    field: "year",
    filter: "agNumberColumnFilter",
    sortable: true,
    width: 90
  },
  {
    headerName: "Sampling Point Id",
    field: "sampling_point_code",
    filter: "agTextColumnFilter",
    sortable: true,
    width: 180
  },
  {
    headerName: "Air Pollutant",
    field: "pollutant",
    filter: "agTextColumnFilter",
    sortable: true,
    width: 120
  },
  {
    headerName: "Protection Target",
    field: "objecttype",
    filter: "agTextColumnFilter",
    sortable: true,
    width: 140,
    valueFormatter: (params) => {
      const labels = {
        LV: "Health",
        ALT: "Health",
        INT: "Health",
        TV: "Health",
        LTO: "Health",
        CL: "Vegetation"
      };
      return labels[params.value] || "Health";
    }
  },
  {
    headerName: "Objective Type",
    field: "objective",
    filter: "agTextColumnFilter",
    sortable: true,
    width: 180
  },
  {
    headerName: "Reporting Metric",
    field: "statistic",
    filter: "agTextColumnFilter",
    sortable: true,
    width: 160
  },
  {
    headerName: "Air Pollution Level",
    field: "measured_value",
    filter: "agNumberColumnFilter",
    sortable: true,
    width: 150,
    valueFormatter: (params) => {
      if (params.value === undefined || params.value === null) {
        return "-";
      }
      return typeof params.value === "number" ? params.value.toFixed(2) : params.value;
    }
  },
  {
    headerName: "Data Coverage",
    field: "coverage",
    filter: "agNumberColumnFilter",
    sortable: true,
    width: 130,
    valueFormatter: (params) => {
      if (params.value === undefined || params.value === null) {
        return "-";
      }
      return params.value + "%";
    }
  },
  {
    headerName: "Is Exceedance",
    field: "exceeded",
    filter: "agTextColumnFilter",
    sortable: true,
    width: 130,
    cellRenderer: (params) => {
      if (params.value === true) {
        return '<span class="px-2 py-1 rounded text-xs bg-nord11/20 border border-nord11  font-semibold">Yes</span>';
      } else {
        return '<span class="px-2 py-1 rounded text-xs bg-nord14/20 border border-nord14  font-semibold">No</span>';
      }
    }
  }
];
