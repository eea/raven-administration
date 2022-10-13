<script setup>
import { useRoute } from "vue-router";
import ApexCharts from "apexcharts";

import Apex from "./apex";
import Service from "./service";

const timeserieId = ref("");
const timeseries = ref([]);
const scalingpoints = ref([]);
const showPlotAndTable = ref(false);

var chart1;
var chart2;

const route = useRoute();

onMounted(async () => {
  await loadData();
  if (route.query.id) {
    timeserieId.value = route.query.id;
    onShowScalingpoints();
  }
});

const loadData = async () => {
  timeseries.value = await Service.timeseries();
};

const onShowScalingpoints = async () => {
  showPlotAndTable.value = true;
  scalingpoints.value = await Service.scalingpoints({ sampling_point_id: timeserieId.value });
  console.log("scalingpoints", scalingpoints.value);

  const series1 = formatValues1();
  const series2 = formatValues2();
  if (!chart1) {
    chart1 = new ApexCharts(document.querySelector("#chart1"), Apex.options([]));
    chart1.render();
  }
  chart1.updateSeries(series1);

  if (!chart2) {
    chart2 = new ApexCharts(document.querySelector("#chart2"), Apex.options([]));
    chart2.render();
  }
  chart2.updateSeries(series2);
};

const formatValues1 = () => {
  const series = [];
  const values = scalingpoints.value.slice(0, 10);
  const data = values.map((o) => {
    return { x: o.datetime, y: o.zero_point };
  });
  series.push({ name: "0-point", data, color: "#A3BE8C" });
  return series;
};

const formatValues2 = () => {
  const series = [];
  const values = scalingpoints.value.slice(0, 10);
  const data_span = values.map((o) => {
    return { x: o.datetime, y: o.span_value };
  });
  series.push({ name: "Span", data: data_span, color: "#D08770" });

  const data_gas = scalingpoints.value.map((o) => {
    return { x: o.datetime, y: o.gas_concentration };
  });
  series.push({ name: "Gas", data: data_gas, color: "#B48EAD" });
  return series;
};

const cls_timeseries = (hasscalingpoint) => {
  if (hasscalingpoint) return "border-l-2 border-nord7";
  return "";
};
</script>

<template>
  <common-layout>
    <tool-bar title="Scale" :show-filter="false" :show-add="false" :show-download="false" />

    <container>
      <div class="flex gap-3">
        <div class="flex-1">
          <div class="font-bold">Timeserie</div>
          <n-select class="!w-full" v-model="timeserieId" :searchable="true">
            <n-option v-for="opt in timeseries" :value="opt.value" :label="opt.label" :class="cls_timeseries(opt.hasscalingpoint)" />
          </n-select>
        </div>
        <div>
          <div>&nbsp;</div>
          <button class="n-button" :disabled="timeserieId.length == 0" @click="onShowScalingpoints">Show scaling points</button>
        </div>
      </div>
    </container>

    <div class="flex gap-2 mt-4 w-full" v-show="showPlotAndTable">
      <container class="!p-4" id="chart1"></container>
      <container class="!p-4" id="chart2"></container>
    </div>

    <div class="mt-4" v-if="showPlotAndTable">
      <table id="convertionsId" class="n-table">
        <tr>
          <th>Timestamp</th>
          <th>Gas concentration</th>
          <th>0-point</th>
          <th>Span</th>
        </tr>
        <tr v-for="row in scalingpoints" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}">
          <td class="space-x-4">{{ row.timestamp }}</td>
          <td>{{ row.gas_concentration }}</td>
          <td>{{ row.span_value }}</td>
          <td>{{ row.zero_point }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>

<style></style>
