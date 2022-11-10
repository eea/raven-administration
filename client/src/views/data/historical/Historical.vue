<script setup>
import { useRoute } from "vue-router";
import Service from "./service";

import Chart from "chart.js/auto";
import "chartjs-adapter-luxon";
import Plot from "./plot";

import { format, sub, isAfter, isBefore } from "date-fns";
import { groupBy, sortBy } from "../../../helpers/utils";
import Eventy from "../../../helpers/eventy";

const timeseries = ref([]);

const fromtime = ref("");
const totime = ref("");
const selectedIds = ref([]);
const meantype = ref("0");
const coverage = ref(75);
const plotType = ref("line");

const showPlot = ref(false);

const route = useRoute();

var chart;

onMounted(async () => {
  fromtime.value = format(sub(new Date(), { days: 14 }), "yyy-MM-dd 00:00");
  timeseries.value = await Service.timeseries();

  if (route.query.ids) selectedIds.value = route.query.ids.split(";");
  if (route.query.from) fromtime.value = route.query.from;
  if (route.query.to) totime.value = route.query.to;
  if (route.query.ids || route.query.from || route.query.to) plotData();
});

const plotData = async () => {
  showPlot.value = true;
  Eventy.showMessage("Plotting data. Please wait", "loading");
  if (chart) {
    chart.data = [];
    chart.update();
  }

  var meanvalues = await Service.get({
    sampling_point_ids: selectedIds.value,
    from_dt: fromtime.value,
    to_dt: totime.value,
    meantype: meantype.value,
    coverage: coverage.value
  });

  if (!chart) {
    chart = new Chart("chart", Plot.config());
  }

  chart.data = formatValues(meanvalues);
  chart.update();
  Eventy.hideMessage();
};

const formatValues = (meanvalues) => {
  var grouped_values = groupBy(meanvalues, (p) => p.sampling_point_id);
  const series = [];
  grouped_values.forEach((p) => {
    const values = sortBy(p[1], ["datetime"]);
    const data = values.map((o) => {
      return { x: o.datetime.replace(" ", "T"), y: o.value };
    });
    let serie = Plot.dataset(p[1][0].station + " - " + p[1][0].component, data, "#A3BE8C", plotType.value);
    series.push(serie);
  });
  return { datasets: series };
};

const cmp_timeseries = computed(() => {
  return timeseries.value.filter((t) => {
    if (!t.fromtime && !t.totime) return true;
    return isAfter(new Date(t.totime), new Date(fromtime.value)) && isBefore(new Date(t.fromtime), new Date(totime.value));
  });
});
</script>

<template>
  <common-layout>
    <tool-bar title="Historical data" :show-column-picker="false" :show-add="false" :show-filter="false" />

    <container>
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
          <n-select class="!w-48" v-model="meantype">
            <n-option value="0" label="Original" />
            <n-option value="1" label="Hour" />
            <n-option value="2" label="Day" />
            <n-option value="5" label="Moving 24 hour" />
            <n-option value="3" label="Moving eigth hour" />
            <n-option value="6" label="Moving eigth hour max" />
            <n-option value="7" label="Month" />
            <n-option value="4" label="Year" />
            <n-option value="8" label="Winter year" />
            <n-option value="11" label="Winter season" />
            <n-option value="12" label="Summer year" />
            <n-option value="9" label="AOT40 Vegetion" />
            <n-option value="10" label="AOT40 forest protection" />
            <n-option value="999" label="Period" />
          </n-select>
        </div>
        <div>
          <div class="font-bold">Coverage %</div>
          <input class="n-input !w-36" type="number" v-model="coverage" />
        </div>
        <div>
          <div class="font-bold">Plot type</div>
          <n-select class="!w-36" v-model="plotType">
            <n-option value="line" label="Line" />
            <n-option value="bar" label="Bar" />
          </n-select>
        </div>
      </div>

      <div>
        <div class="font-bold">Timeseries</div>
        <n-multiselect class="!w-full" v-model="selectedIds" :searchable="cmp_timeseries.length > 0">
          <n-option v-for="t in cmp_timeseries" :key="t.value" :value="t.value" :label="t.label" />
          <n-option v-if="cmp_timeseries.length == 0" :value="0" label="No timeseries found for time period" class="!pointer-events-none" />
        </n-multiselect>
      </div>

      <div class="mt-2">
        <button class="n-button" @click="plotData" :disabled="selectedIds.length == 0">Plot data</button>
      </div>
    </container>

    <container v-show="showPlot" class="mt-4 !p-4 h-96 w-full"><canvas id="chart"></canvas></container>
  </common-layout>
</template>

<style></style>
