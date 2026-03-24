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

const Plot = {
  config: (axes, beginAtZero = false, chartType = "line") => {
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
            titleColor: "#2E3440"
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
        scales: Plot.multiscales(axes, beginAtZero),
        datasets: {
          line: {
            pointRadius: 1,
            pointHoverRadius: 3,
            borderWidth: 2
          }
        }
      }
    };
  },
  multiscales: (axes, beginAtZero) => {
    var s = {};
    s.x = {
      type: "time",
      offset: true,
      adapters: {
        date: { zone: "UTC" }
      },
      time: {
        tooltipFormat: "yyyy-MM-dd HH",
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
      s[y] = {
        position: i == 0 ? "left" : "right",
        display: true,
        title: { display: true, text: y },
        beginAtZero: beginAtZero
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
