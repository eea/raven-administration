<script setup>
import { useRoute } from "vue-router";
import Service from "./service";

import Chart from "chart.js/auto";
import "chartjs-adapter-luxon";
import Plot from "./plot";

import { format, sub, isAfter, isBefore, startOfWeek } from "date-fns";
import { groupBy, sortBy } from "../../../helpers/utils";
import Eventy from "../../../helpers/eventy";
import IconCalendar from "~icons/ic/round-access-time";

const ev_preset = ref();
const timeseries = ref([]);

const fromtime = ref("");
const totime = ref("");
const selectedIds = ref([]);
const meantype = ref("0");
const coverage = ref(75);
const plotType = ref("line");
const beginAtZero = ref(false);

const showPlot = ref(false);

const route = useRoute();

var chart;

onMounted(async () => {
  fromtime.value = format(sub(new Date(), { days: 14 }), "yyy-MM-dd 00:00");
  totime.value = format(new Date(), "yyy-MM-dd HH:00");
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
    chart.destroy();
    chart = null;
  }

  var meanvalues = await Service.get({
    sampling_point_ids: selectedIds.value,
    from_dt: fromtime.value,
    to_dt: totime.value,
    meantype: meantype.value,
    coverage: coverage.value
  });

  chart = new Chart("chart", Plot.config(beginAtZero.value));

  chart.data = formatValues(meanvalues);
  chart.update();
  Eventy.hideMessage();
};

const changeDates = (s) => {
  const d = new Date();
  if (s == "This week") {
    fromtime.value = format(startOfWeek(d, { weekStartsOn: 1 }), "yyy-MM-dd 00:00");
    totime.value = format(d, "yyy-MM-dd HH:00");
  } else if (s == "Last week") {
    fromtime.value = format(sub(startOfWeek(d, { weekStartsOn: 1 }), { days: 7 }), "yyy-MM-dd 00:00");
    totime.value = format(startOfWeek(d, { weekStartsOn: 1 }), "yyy-MM-dd 00:00");
  } else if (s == "Last month") {
    fromtime.value = format(new Date(d.getFullYear(), d.getMonth() - 1, 1), "yyy-MM-dd 00:00");
    totime.value = format(new Date(d.getFullYear(), new Date().getMonth(), 0), "yyy-MM-dd 00:00");
  } else if (s == "This year") {
    fromtime.value = format(new Date(d.getFullYear(), 0, 1), "yyy-MM-dd 00:00");
    totime.value = format(d, "yyy-MM-dd HH:00");
  } else if (s == "Last year") {
    fromtime.value = format(new Date(d.getFullYear() - 1, 0, 1), "yyy-MM-dd 00:00");
    totime.value = format(new Date(d.getFullYear(), 0, 1), "yyy-MM-dd 00:00");
  }
  ev_preset.value = null;
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
    <contextmenu :evt="ev_preset" :show="!!ev_preset" @click-outside="ev_preset = null" class="">
      <div class="px-2 font-bold">Presets:</div>
      <div class="border-l-2 border-nord14 pl-2 pr-4 py-2 cursor-pointer hover:bg-gray-100" @click="changeDates('This week')">This week</div>
      <div class="border-l-2 border-nord14 pl-2 pr-4 py-2 cursor-pointer hover:bg-gray-100" @click="changeDates('Last week')">Last week</div>
      <div class="border-l-2 border-nord11 pl-2 pr-4 py-2 cursor-pointer hover:bg-gray-100" @click="changeDates('Last month')">Last month</div>
      <div class="border-l-2 border-nord15 pl-2 pr-4 py-2 cursor-pointer hover:bg-gray-100" @click="changeDates('This year')">This year</div>
      <div class="border-l-2 border-nord15 pl-2 pr-4 py-2 cursor-pointer hover:bg-gray-100" @click="changeDates('Last year')">Last year</div>
    </contextmenu>
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
        <div>
          <br />
          <button class="n-button flex gap-2" @click="ev_preset = $event">
            <icon-calendar class="self-center text-nord10 text-lg !p-0" />
            <div class="self-center">Presets</div>
          </button>
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

      <div class="flex gap-2">
        <label class="self-center cursor-pointer font-bold" @click="beginAtZero = !beginAtZero">Start Y-axis at zero:</label>
        <n-checkbox class="self-center" v-model="beginAtZero" />
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
