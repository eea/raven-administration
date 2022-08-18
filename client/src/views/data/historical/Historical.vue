<script setup>
import { useRoute } from "vue-router";
import Service from "./service";

import ApexCharts from "apexcharts";
import Apex from "./apex";
import { groupBy, sortBy } from "../../../helpers/utils";

const timeseries = ref([]);

const fromtime = ref("2020-01-01 00:00");
const totime = ref("2021-01-01 00:00");
const selectedIds = ref([]);
const meantype = ref("0");
const coverage = ref(75);
const showAsBar = ref(true);

const route = useRoute();

var chart;

onMounted(async () => {
  timeseries.value = await Service.timeseries();
  await route.query; // bug in multiselect. if options are not yet drawn, v-model is not showing
  if (route.query.ids) selectedIds.value = route.query.ids.split(";");
  if (route.query.from) totime.value = route.query.from;
  if (route.query.to) totime.value = route.query.to;
  if (route.query.ids || route.query.from || route.query.to) plotData();
});

const plotData = async () => {
  if (chart) chart.updateSeries([]);

  var meanvalues = await Service.get({
    sampling_point_ids: selectedIds.value,
    from_dt: fromtime.value,
    to_dt: totime.value,
    meantype: meantype.value,
    coverage: coverage.value,
  });

  // console.log("PLOT", meanvalues);

  const series = formatValues(meanvalues);
  if (!chart) {
    chart = new ApexCharts(document.querySelector("#chart"), Apex.options([]));
    chart.render();
  }
  chart.updateSeries(series);
};

const formatValues = (meanvalues) => {
  var grouped_values = groupBy(meanvalues, (p) => p.sampling_point_id);
  const series = [];
  grouped_values.forEach((p) => {
    const values = sortBy(p[1], ["datetime"]);
    const data = values.map((o) => {
      return { x: o.datetime, y: o.value };
    });
    let serie = { name: p[1][0].station + " - " + p[1][0].component, data };

    series.push(serie);
  });
  return series;
};
</script>

<template>
  <common-layout>
    <tool-bar title="Historical data" :show-download="true" :show-add="false" :show-filter="false" />
    <div class="border border-nord4 bg-gray-50 p-2 flex flex-col gap-3">
      <div class="flex gap-2">
        <div>
          <div class="font-bold">From</div>
          <n-datetime v-model="fromtime" class="" />
        </div>
        <div>
          <div class="font-bold">To</div>
          <n-datetime v-model="totime" class="" />
        </div>
      </div>

      <div class="flex gap-2">
        <div>
          <div class="font-bold">Aggregation</div>
          <n-select class="!w-36" v-model="meantype">
            <n-option value="0" label="Original" />
            <n-option value="1" label="Hour" />
            <n-option value="2" label="Day" />
          </n-select>
        </div>
        <div>
          <div class="font-bold">Coverage %</div>
          <input class="n-input !w-36" type="number" v-model="coverage" />
        </div>
      </div>

      <div>
        <div class="font-bold">Timeseries</div>
        <n-multiselect class="!w-full" v-model="selectedIds" :searchable="true">
          <n-option v-for="t in timeseries" :value="t.value" :label="t.label" />
        </n-multiselect>
      </div>

      <div class="mt-2">
        <button class="n-button" @click="plotData">Plot data</button>
      </div>
    </div>

    <div class="bg-gray-50 border border-gray-200 p-4 mt-4" id="chart"></div>
  </common-layout>
</template>

<style></style>
