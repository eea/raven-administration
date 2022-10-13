export default Apex = {
  options: (series, onDatapointSelection) => {
    return {
      chart: {
        type: "bar",
        height: 200,
        toolbar: {
          show: true,
          tools: {
            download: false,
            selection: true,
            zoom: true,
            zoomin: false,
            zoomout: false,
            pan: true
          },
          autoSelected: "pan"
        },
        animations: {
          enabled: false,
          animateGradually: {
            enabled: false
          },
          dynamicAnimation: {
            enabled: false
          }
        },
        events: {
          dataPointSelection: onDatapointSelection
        }
      },
      states: {
        active: {
          allowMultipleDataPointsSelection: false
        }
      },
      legend: {
        show: false
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
          hour: "HH:mm"
        },
        labels: {
          style: {
            cssClass: "text-xs "
          }
        }
      },
      //colors: ["#A3BE8C", "#D08770", "#B48EAD", "#BF616A", "#EBCB8B", "#88C0D0", "#5E81AC"],
      stroke: {
        show: false,
        curve: "straight",
        lineCap: "butt",
        width: 2,
        dashArray: 0
      },
      dataLabels: {
        enabled: false
      },
      tooltip: {
        x: { format: "dd MMM HH:mm" }
      },
      marker: { size: 0 }
    };
  }
};
