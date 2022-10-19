import autocolors from "chartjs-plugin-autocolors";
const Plot = {
  config: (data = []) => {
    return {
      type: "line",
      data: data,
      plugins: [autocolors],
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
        },
        datasets: {
          line: {
            pointRadius: 0,
            borderWidth: 2
          }
        }
      }
    };
  },
  dataset: (label, data, color, type = "line") => {
    //if(!color)
    let d = { label, data, type };
    return d;
  }
};
export default Plot;
