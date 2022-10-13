export default Apex = {
  options: (series) => {
    return {
      chart: {
        type: "line",
        height: 300,
        toolbar: false,
        animations: {
          enabled: false,
          animateGradually: {
            enabled: false
          },
          dynamicAnimation: {
            enabled: false
          }
        }
      },
      series: series,
      xaxis: {
        type: "datetime",
        format: undefined,
        formatter: undefined,
        datetimeUTC: false,
        datetimeFormatter: {
          year: "yyyy",
          month: "MMM 'yy",
          day: "dd MMM",
          hour: "HH"
        }
      },
      legend: { show: true, showForSingleSeries: true },
      stroke: {
        show: true,
        curve: "straight",
        lineCap: "butt",
        width: 2,
        dashArray: 0
      },
      dataLabels: {
        enabled: false
      },
      tooltip: {
        x: { format: "dd MMM HH" }
      },
      marker: { size: 0 }
    };
  }
};
