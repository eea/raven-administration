<script setup>
import { useRoute } from "vue-router";
import Chart from "chart.js/auto";
import "chartjs-adapter-luxon";
import Plot from "./plot";
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

  const config1 = Plot.config(formatValues1());
  const config2 = Plot.config(formatValues2());

  chart1 = new Chart("chart1", config1);
  chart2 = new Chart("chart2", config2);
};

const formatValues1 = () => {
  const series = [];
  const values = scalingpoints.value.slice(-10);
  const data = values.map((o) => {
    return { x: o.datetime.replace(" ", "T"), y: o.zero_point };
  });

  series.push(Plot.dataset("0-point", data, "#A3BE8C"));
  return { datasets: series };
};

const formatValues2 = () => {
  const series = [];
  const values = scalingpoints.value.slice(-10);
  const data_span = values.map((o) => {
    return { x: o.datetime.replace(" ", "T"), y: o.span_value };
  });
  series.push(Plot.dataset("Span", data_span, "#D08770"));

  const data_gas = scalingpoints.value.map((o) => {
    return { x: o.datetime.replace(" ", "T"), y: o.gas_concentration };
  });

  series.push(Plot.dataset("Gas", data_gas, "#B48EAD"));
  return { datasets: series };
};

const cmp_scalingpoints = computed(() => {
  return scalingpoints.value.reverse();
});

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
      <container class="w-1/2 h-72"><canvas id="chart1"></canvas></container>
      <container class="w-1/2 h-72"><canvas id="chart2"></canvas></container>
    </div>

    <div class="mt-4" v-if="showPlotAndTable">
      <table id="convertionsId" class="n-table">
        <tr>
          <th>Timestamp</th>
          <th>0-point</th>
          <th>Span</th>
          <th>Gas concentration</th>
        </tr>
        <tr v-for="row in cmp_scalingpoints" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}">
          <td class="space-x-4">{{ row.timestamp }}</td>
          <td>{{ row.zero_point }}</td>
          <td>{{ row.span_value }}</td>
          <td>{{ row.gas_concentration }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>

<style></style>
