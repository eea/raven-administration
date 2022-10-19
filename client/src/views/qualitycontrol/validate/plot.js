const Plot = {
  config: (click) => {
    return {
      type: "bar",
      data: [],
      options: {
        onClick: click,
        animation: false,
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          intersect: false,
          mode: "index"
        },
        plugins: {
          legend: { display: false },
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
          bar: {
            hoverBackgroundColor: "#81A1C1"
          }
        }
      }
    };
  },
  dataset: (label, data, colors) => {
    //if(!color)
    let d = { label, data, backgroundColor: colors };
    return d;
  }
};
export default Plot;
