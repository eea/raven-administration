export default Apex = {
    options: (series) => {
        return {
            chart: {
                type: 'line',
                height: 400,
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
                    year: 'yyyy',
                    month: "MMM 'yy",
                    day: 'dd MMM',
                    hour: 'HH:mm',
                }
            },
            colors: ['#A3BE8C', '#D08770', '#B48EAD', '#BF616A', '#EBCB8B', '#88C0D0', '#5E81AC'],
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
                x: { format: "dd MMM HH:mm" }, 
            },
            marker: { size: 0 }
        }
    }
}