const secondsToXAxis = (seconds) => {
  if (!seconds || seconds <= 0) return {};
  if (seconds < 3600)  return { unit: "minute", tooltipFormat: "yyyy-MM-dd HH:mm" };
  if (seconds < 86400) return { unit: "hour",   tooltipFormat: "yyyy-MM-dd HH:mm" };
  if (seconds < 604800) return { unit: "day",   tooltipFormat: "yyyy-MM-dd" };
  if (seconds < 2592000) return { unit: "week", tooltipFormat: "yyyy-MM-dd" };
  return                        { unit: "month", tooltipFormat: "yyyy-MM" };
};

const Plot = {
  config: (click, finestTimestepSeconds = null) => {
    const xAxis = secondsToXAxis(finestTimestepSeconds);
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
            titleColor: "#2E3440",
            callbacks: {
              label: (item) => {
                const actual = item.raw?.obj?.value;
                return actual != null ? ` ${actual}` : null;
              }
            }
          }
        },

        scales: {
          x: {
            type: "time",
            offset: true,
            ticks: {
              major: { enabled: true },
              font: (ctx) => {
                const boldedTicks = ctx.tick?.major ? "bold" : "";
                return { weight: boldedTicks };
              },
              maxRotation: 0,
              minRotation: 0,
              autoSkip: true,
              maxTicksLimit: 20
            },
            time: {
              tooltipFormat: xAxis.tooltipFormat ?? "yyyy-MM-dd HH:mm",
              ...(xAxis.unit ? { unit: xAxis.unit } : {}),
              displayFormats: {
                millisecond: "HH:mm:ss",
                second:      "HH:mm:ss",
                minute:      "yyyy-MM-dd HH:mm",
                hour:        "yyyy-MM-dd HH",
                day:         "yyyy-MM-dd",
                week:        "yyyy-MM-dd",
                month:       "yyyy-MM",
                quarter:     "yyyy-MM",
                year:        "yyyy"
              }
            },
            title: { display: false }
          },
          y: {
            title: { display: false, text: "value" }
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
    let d = { label, data, backgroundColor: colors };
    return d;
  }
};
export default Plot;
