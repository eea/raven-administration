<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import Service from "./service";

import Chart from "chart.js/auto";
import "chartjs-adapter-luxon";
import zoomPlugin from "chartjs-plugin-zoom";
import Plot from "./plot";

import { format, sub, isAfter, isBefore, startOfWeek } from "date-fns";
import { groupBy } from "../../../helpers/utils";
import Eventy from "../../../helpers/eventy";
import IconCalendar from "~icons/ic/round-access-time";

import CommonLayout from "../../../components/CommonLayout.vue";
import CMenu from "../../../components/CMenu.vue";
import ToolBar from "../../../components/ToolBar.vue";
import Container from "../../../components/Container.vue";
import DatetimePicker from "../../../components/DatetimePicker.vue";
import DataTable from "../../../components/DataTable.vue";

Chart.register(zoomPlugin);

const menuRef = ref();
const timeseries = ref([]);
const timeseriesGridApi = ref();

const fromtime = ref(startOfWeek(new Date(), { weekStartsOn: 1 }));
const totime = ref(new Date());
const selectedIds = ref([]);
const meantype = ref("0");
const activeMeantype = ref("0");
const coverage = ref(75);
const plotType = ref("line");
const beginAtZero = ref(false);
const verifiedOnly = ref(false);
const useInvalidValues = ref(false);

const showPlot = ref(false);

const route = useRoute();
const gridData = ref([]);

var chart;

onMounted(async () => {
  timeseries.value = await Service.timeseries();

  if (route.query.ids) selectedIds.value = route.query.ids.split(";");
  if (route.query.from) fromtime.value = new Date(route.query.from);
  if (route.query.to) totime.value = new Date(route.query.to);
  if (route.query.ids || route.query.from || route.query.to) plotData();
});

// Watch for chart display option changes and update chart without refetching data
watch([beginAtZero, plotType], () => {
  if (chart && gridData.value.length > 0) {
    updateChart();
  }
});

const updateChart = () => {
  if (!chart || !gridData.value.length) return;

  chart.destroy();

  var axes = getAxes(gridData.value);
  let config = Plot.config(axes, beginAtZero.value);
  chart = new Chart("chart", config);

  chart.data = formatValues(gridData.value, axes);
  chart.update();
};

const plotData = async () => {
  showPlot.value = true;
  Eventy.showMessage("Plotting data. Please wait", "loading");
  if (chart) {
    chart.destroy();
    chart = null;
  }

  gridData.value = [];

  gridData.value = await Service.get({
    sampling_point_ids: selectedIds.value,
    from_dt: format(fromtime.value, "yyyy-MM-dd HH:00"),
    to_dt: format(totime.value, "yyyy-MM-dd HH:00"),
    meantype: meantype.value,
    coverage: coverage.value,
    verifiedOnly: verifiedOnly.value,
    useInvalidValues: useInvalidValues.value
  });

  activeMeantype.value = meantype.value;

  var axes = getAxes(gridData.value);
  let config = Plot.config(axes, beginAtZero.value);
  chart = new Chart("chart", config);

  chart.data = formatValues(gridData.value, axes);
  chart.update();

  Eventy.hideMessage();
};

const onDownload = async () => {
  Eventy.showMessage("Downloading data. Please wait", "loading");
  await Service.download({
    sampling_point_ids: selectedIds.value,
    from_dt: format(fromtime.value, "yyyy-MM-dd HH:00"),
    to_dt: format(totime.value, "yyyy-MM-dd HH:00"),
    meantype: meantype.value,
    coverage: coverage.value,
    verifiedOnly: verifiedOnly.value,
    useInvalidValues: useInvalidValues.value
  });
  Eventy.hideMessage();
};
const changeDates = (s) => {
  const d = new Date();
  if (s == "This week") {
    fromtime.value = startOfWeek(d, { weekStartsOn: 1 });
    totime.value = d;
  } else if (s == "Last week") {
    fromtime.value = sub(startOfWeek(d, { weekStartsOn: 1 }), { days: 7 });
    totime.value = startOfWeek(d, { weekStartsOn: 1 });
  } else if (s == "This month") {
    fromtime.value = new Date(d.getFullYear(), d.getMonth(), 1);
    totime.value = d;
  } else if (s == "Last month") {
    fromtime.value = new Date(d.getFullYear(), d.getMonth() - 1, 1);
    totime.value = new Date(d.getFullYear(), new Date().getMonth(), 0);
  } else if (s == "This year") {
    fromtime.value = new Date(d.getFullYear(), 0, 1);
    totime.value = d;
  } else if (s == "Last year") {
    fromtime.value = new Date(d.getFullYear() - 1, 0, 1);
    totime.value = new Date(d.getFullYear(), 0, 1);
  }
};

const formatValues = (meanvalues, axes) => {
  var grouped_values = groupBy(meanvalues, (p) => p.sampling_point_id);
  const series = [];
  grouped_values.forEach((p) => {
    const values = p[1].sort((a, b) => new Date(a.datetime) - new Date(b.datetime));
    const data = values.map((o) => {
      return { x: o.datetime.replace(" ", "T"), y: o.value };
    });
    var axis = axes.find((a) => a == values[0].unit);
    const first = p[1][0];
    const equipmentPart = [first.equipment, first.equipment_identifier].filter(Boolean).join(" / ");
    const label = [first.station, first.component, first.unit, equipmentPart].filter(Boolean).join(" - ");
    let serie = Plot.dataset(label, data, "#A3BE8C", plotType.value, axis);
    series.push(serie);
  });
  return { datasets: series };
};

const getAxes = (meanvalues) => {
  return groupBy(meanvalues, (p) => p.unit).map((p) => p[0]);
};

const onResetZoom = () => {
  if (chart) chart.resetZoom();
};

const cmp_timeseries = computed(() => {
  return timeseries.value.filter((t) => {
    if (!t.fromtime && !t.totime) return true;
    return isAfter(new Date(t.totime), fromtime.value) && isBefore(new Date(t.fromtime), totime.value);
  });
});

const onMenuClick = ({ action }) => {
  changeDates(action);
};

const onPresetClick = (e) => {
  menuRef.value?.showMenu({}, e);
};

const timeseriesColumns = [
  { field: "station", headerName: "Station", flex: 1, filter: true },
  { field: "pollutant", headerName: "Pollutant", flex: 1, filter: true },
  { field: "timestep", headerName: "Timestep", flex: 1, filter: true },
  { field: "unit", headerName: "Unit", flex: 1, filter: true },
  { field: "equipment", headerName: "Equipment", flex: 1, filter: true },
  { field: "equipment_identifier", headerName: "Eq. Identifier", flex: 1, filter: true }
];

const gridDataColumns = computed(() => {
  const isRawOrOriginal = activeMeantype.value === "1000" || activeMeantype.value === "0";
  return [
    { field: "network", headerName: "Network", flex: 1, filter: true },
    { field: "station", headerName: "Station", flex: 1, filter: true },
    { field: "component", headerName: "Pollutant", flex: 0.5, filter: true },
    { headerName: "Timestep", flex: 0.5, filter: true, valueGetter: (params) => (params.data?.meantype === 0 || params.data?.meantype === 1000) ? params.data?.timestep : params.data?.meantype_string },
    { field: "equipment", headerName: "Equipment", flex: 1, filter: true },
    { field: "equipment_identifier", headerName: "Eq. Identifier", flex: 1, filter: true },
    { field: "datetime_begin", headerName: "From", flex: 1, filter: true, hide: !isRawOrOriginal },
    { field: "datetime", headerName: isRawOrOriginal ? "To" : "Datetime", flex: 1, filter: true, sort: "desc" },
    { field: "actual_value", headerName: "Value", flex: 0.5, filter: true },
    { field: "coverage", headerName: "Coverage", flex: 0.5, filter: true },
    { field: "valid", headerName: "Valid", flex: 0.5, cellRenderer: (params) => (params.value ? "✓" : "✗"), cellStyle: (params) => ({ color: params.value ? "#a3be8c" : "#bf616a", fontWeight: "bold", textAlign: "center" }) }
  ];
});

const getRowStyle = (params) => {
  if (!params.data) return {};
  return params.data.valid === false ? { background: "rgba(191, 97, 106, 0.1)" } : {};
};

const onTimeseriesGridReady = (params) => {
  timeseriesGridApi.value = params.api;
  // Set initial selection if selectedIds is populated (from query params)
  if (selectedIds.value.length > 0) {
    params.api.forEachNode((node) => {
      if (selectedIds.value.includes(node.data.sampling_point_id)) {
        node.setSelected(true);
      }
    });
  }
};

const onTimeseriesSelectionChanged = (rows) => {
  selectedIds.value = rows.map((r) => r.sampling_point_id);
};
</script>

<template>
  <CommonLayout class="flex flex-col gap-4">
    <c-menu ref="menuRef" @on-click="onMenuClick">
      <template #default="{ handleAction }">
        <div class="px-2 font-bold">Presets:</div>
        <div class="border-l-2 border-nord14 pl-2 pr-4 py-1.5 cursor-pointer hover:bg-nord6" @click="handleAction('This week')">This week</div>
        <div class="border-l-2 border-nord14 pl-2 pr-4 py-1.5 cursor-pointer hover:bg-nord6" @click="handleAction('Last week')">Last week</div>
        <div class="border-l-2 border-nord11 pl-2 pr-4 py-1.5 cursor-pointer hover:bg-nord6" @click="handleAction('This month')">This month</div>
        <div class="border-l-2 border-nord11 pl-2 pr-4 py-1.5 cursor-pointer hover:bg-nord6" @click="handleAction('Last month')">Last month</div>
        <div class="border-l-2 border-nord15 pl-2 pr-4 py-1.5 cursor-pointer hover:bg-nord6" @click="handleAction('This year')">This year</div>
        <div class="border-l-2 border-nord15 pl-2 pr-4 py-1.5 cursor-pointer hover:bg-nord6" @click="handleAction('Last year')">Last year</div>
      </template>
    </c-menu>

    <ToolBar title="Historical data" :show-add="false" :show-filter="false" @download-click="onDownload" />

    <Container>
      <div class="flex gap-2">
        <div>
          <div class="font-bold">From</div>
          <DatetimePicker v-model="fromtime" />
        </div>
        <div>
          <div class="font-bold">To</div>
          <DatetimePicker v-model="totime" />
        </div>
        <div>
          <br />
          <button class="button flex gap-2" @click="onPresetClick">
            <icon-calendar class="self-center text-nord10 text-lg p-0!" />
            <div class="self-center">Presets</div>
          </button>
        </div>
      </div>

      <div class="flex gap-6 bg-white border border-nord4 rounded p-2 self-start">
        <div class="flex gap-2">
          <div class="font-bold self-center">Aggregation</div>
          <select class="select self-center" v-model="meantype">
            <option value="1000">Raw</option>
            <option value="0">Original</option>
            <option value="1">Hour</option>
            <option value="2">Day</option>
            <option value="5">Moving 24 hour</option>
            <option value="3">Moving eigth hour</option>
            <option value="6">Moving eigth hour max</option>
            <option value="7">Month</option>
            <option value="4">Year</option>
            <option value="8">Winter year</option>
            <option value="11">Winter season</option>
            <option value="12">Summer year</option>
            <option value="9">AOT40 Vegetion</option>
            <option value="10">AOT40 forest protection</option>
            <option value="999">Period</option>
          </select>
        </div>
        <div class="flex gap-2">
          <div class="font-bold mb-1 self-center">
            Coverage
            <span class="inline-block w-8 text-right">{{ coverage }}</span>
            %:
          </div>
          <input type="range" min="0" max="100" step="1" v-model="coverage" class="self-center" :disabled="meantype === '1000' || meantype === '0'" :class="{ 'opacity-40': meantype === '1000' || meantype === '0' }" />
        </div>
      </div>

      <div class="flex gap-6 bg-white border border-nord4 rounded p-2 self-start">
        <div class="flex gap-2">
          <label class="self-center cursor-pointer font-bold" @click="useInvalidValues = !useInvalidValues">Include invalid values:</label>
          <input type="checkbox" class="self-center" v-model="useInvalidValues" />
        </div>
        <div class="flex gap-2">
          <label class="self-center cursor-pointer font-bold" @click="verifiedOnly = !verifiedOnly">Use only verified values:</label>
          <input type="checkbox" class="self-center" v-model="verifiedOnly" />
        </div>
      </div>

      <div class="h-64">
        <div class="font-bold">Sampling Points</div>
        <DataTable :font-size="11" :columns="timeseriesColumns" :data="cmp_timeseries" selection-mode="multiRow" :get-row-id="(params) => params.data.sampling_point_id" @grid-ready="onTimeseriesGridReady" @selection-changed="onTimeseriesSelectionChanged" />
      </div>

      <div class="mt-6">
        <button class="button" @click="plotData" :disabled="selectedIds.length == 0">Plot data</button>
      </div>
    </Container>

    <Container v-show="showPlot" class="mt-4 p-4! w-full h-96">
      <div class="flex justify-between mb-2">
        <div class="flex gap-6">
          <div class="flex gap-2">
            <label class="self-center cursor-pointer font-bold" @click="beginAtZero = !beginAtZero">Start Y-axis at zero:</label>
            <input type="checkbox" class="self-center" v-model="beginAtZero" />
          </div>
          <div class="flex gap-2">
            <label class="self-center cursor-pointer font-bold" @click="plotType = plotType === 'bar' ? 'line' : 'bar'">Bar chart:</label>
            <input type="checkbox" class="self-center" :checked="plotType === 'bar'" @change="plotType = plotType === 'bar' ? 'line' : 'bar'" />
          </div>
        </div>
        <button class="button" @click="onResetZoom">Reset zoom</button>
      </div>
      <div class="h-full w-full py-4">
        <canvas id="chart"></canvas>
      </div>
    </Container>

    <Container v-show="showPlot" class="flex-1 mt-4 min-h-48"><DataTable :columns="gridDataColumns" :data="gridData" :get-row-style="getRowStyle"></DataTable></Container>
  </CommonLayout>
</template>

<style></style>
