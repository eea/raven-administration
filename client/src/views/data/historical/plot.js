import autocolors from "chartjs-plugin-autocolors";
const Plot = {
  config: (axes, beginAtZero = false) => {
    return {
      type: "line",
      data: [],
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
        scales: Plot.multiscales(axes, beginAtZero),
        datasets: {
          line: {
            pointRadius: 1,
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
    //if(!color)
    let d = { label, data, type, yAxisID: axis };
    return d;
  }
};
export default Plot;
