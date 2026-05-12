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
              tooltipFormat: "dd MMM yyyy HH:mm",
              displayFormats: {
                hour: "HH:mm",
                day: "dd MMM",
                week: "dd MMM",
                month: "MMM yyyy",
                year: "yyyy"
              }
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
