const palette = [
  "#BF616A", // nord11 - red       (~0°)
  "#29A0B1", // cyan               (~190°)
  "#D08770", // nord12 - orange    (~20°)
  "#5E81AC", // nord10 - deep blue (~215°)
  "#EBCB8B", // nord13 - yellow    (~45°)
  "#7060A8", // indigo             (~260°)
  "#A3BE8C", // nord14 - green     (~100°)
  "#B48EAD", // nord15 - purple    (~300°)
  "#8FBCBB", // nord7  - teal      (~175°)
  "#D47FA6", // dusty rose         (~330°)
];

const hexToRgba = (hex, alpha) => {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

// Maps the finest SP timestep (seconds) to Chart.js x-axis unit and tooltip format.
const secondsToXAxis = (seconds) => {
  if (!seconds || seconds <= 0) return {};
  if (seconds < 3600)  return { unit: "minute", tooltipFormat: "yyyy-MM-dd HH:mm" };
  if (seconds < 86400) return { unit: "hour",   tooltipFormat: "yyyy-MM-dd HH:mm" };
  if (seconds < 604800) return { unit: "day",   tooltipFormat: "yyyy-MM-dd" };
  if (seconds < 2592000) return { unit: "week", tooltipFormat: "yyyy-MM-dd" };
  return                        { unit: "month", tooltipFormat: "yyyy-MM" };
};

const Plot = {
  config: (axes, beginAtZero = false, chartType = "line", finestTimestepSeconds = null) => {
    return {
      type: chartType,
      data: [],
      options: {
        animation: false,
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          intersect: false,
          mode: "index",
          axis: "x"
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#fff",
            borderColor: "#D8DEE9",
            borderWidth: 1,
            bodyColor: "#2E3440",
            titleColor: "#2E3440",
            filter: (item) => item.raw?.y != null
          },
          zoom: {
            zoom: {
              wheel: { enabled: true },
              pinch: { enabled: true },
              mode: "x",
              onZoomComplete({ chart }) {
                chart.update("none");
              }
            },
            pan: {
              enabled: true,
              mode: "x"
            }
          }
        },
        scales: Plot.multiscales(axes, beginAtZero, finestTimestepSeconds),
        datasets: {
          line: {
            pointRadius: 1,
            pointHoverRadius: 3,
            borderWidth: 2
          },
          bar: {
            borderWidth: 1
          }
        }
      }
    };
  },
  multiscales: (axes, beginAtZero, finestTimestepSeconds = null) => {
    var s = {};
    const xAxis = secondsToXAxis(finestTimestepSeconds);
    s.x = {
      type: "time",
      offset: true,
      adapters: {
        date: { zone: "UTC" }
      },
      time: {
        tooltipFormat: xAxis.tooltipFormat ?? "yyyy-MM-dd HH:mm",
        ...(xAxis.unit ? { unit: xAxis.unit } : {}),
        displayFormats: {
          millisecond: "HH:mm:ss",
          second: "HH:mm:ss",
          minute: "yyyy-MM-dd HH:mm",
          hour: "yyyy-MM-dd HH",
          day: "yyyy-MM-dd",
          week: "yyyy-MM-dd",
          month: "yyyy-MM",
          quarter: "yyyy-MM",
          year: "yyyy"
        }
      },
      ticks: {
        major: {
          enabled: true
        },
        autoSkip: true,
        maxTicksLimit: 20,
        maxRotation: 0,
        minRotation: 0,
        font: (ctx) => {
          const boldedTicks = ctx.tick?.major ? "bold" : "";
          return { weight: boldedTicks };
        }
      },
      title: {
        display: true
      }
    };
    axes.forEach((y, i) => {
      // beginAtZero may be a plain boolean or a per-axis map { [axisId]: boolean }
      const baz = typeof beginAtZero === "object" ? (beginAtZero[y] ?? true) : beginAtZero;
      s[y] = {
        position: i == 0 ? "left" : "right",
        display: true,
        title: { display: true, text: y },
        beginAtZero: baz
      };
    });
    return s;
  },
  dataset: (label, data, color, type = "line", axis = "y") => {
    let d = { label, data, type, yAxisID: axis, borderColor: color, backgroundColor: color };
    return d;
  }
};
export { palette, hexToRgba };
export default Plot;
