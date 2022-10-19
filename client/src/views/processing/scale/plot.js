const Plot = {
  config: (data = []) => {
    return {
      type: "line",
      data: data,
      options: {
        animation: false,
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          intersect: false,
          mode: "index"
        },
        plugins: {
          tooltip: {
            backgroundColor: "#fff",
            borderColor: "#D8DEE9",
            borderWidth: 1,
            bodyColor: "#2E3440",
            titleColor: "#2E3440"
          }
        },
        scales: {
          x: {
            type: "time",
            time: {
              // Luxon format string
              tooltipFormat: "DD T"
            },
            title: {
              display: false,
              text: "Date"
            }
          },
          y: {
            title: {
              display: false,
              text: "value"
            }
          }
        }
      }
    };
  },
  dataset: (label, data, color) => {
    //if(!color)
    return { label, data, backgroundColor: color, borderColor: color, cubicInterpolationMode: "monotone", borderWidth: 2 };
  }
};
export default Plot;
