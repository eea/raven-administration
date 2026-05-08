<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import Service from "./service";

import Chart from "chart.js/auto";
import "chartjs-adapter-luxon";
import zoomPlugin from "chartjs-plugin-zoom";
import Plot, { palette, hexToRgba } from "./plot";

import { format, sub, isAfter, isBefore, startOfWeek } from "date-fns";
import { groupBy, downloadCsv } from "../../../helpers/utils";
import { datetimeCellRenderer, granularityFromHistoricalRow } from "../../../helpers/datetimeHighlight";
import Eventy from "../../../helpers/eventy";
import IconCalendar from "~icons/ic/round-access-time";
import IconModify from "~icons/material-symbols/tune";
import IconReplot from "~icons/material-symbols/bar-chart";
import IconList from "~icons/material-symbols/table-rows-narrow";
import IconPivot from "~icons/material-symbols/pivot-table-chart";

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
const collapsed = ref(false);

const meantypeLabel = computed(() => {
  const labels = { 1000: "Raw", 0: "Original", 1: "Hour", 2: "Day", 5: "Moving 24 hour", 3: "Moving eight hour", 6: "Moving eight hour max", 7: "Month", 4: "Year", 8: "Winter year", 11: "Winter season", 12: "Summer year", 9: "AOT40 Vegetation", 10: "AOT40 forest protection", 999: "Period" };
  return labels[meantype.value] || meantype.value;
});

const showPlot = ref(false);
const legendItems = ref([]);
const hoveredLegendIndex = ref(-1);

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

  const xMin = chart.scales.x?.min;
  const xMax = chart.scales.x?.max;

  chart.destroy();

  var axes = getAxes(gridData.value);
  let config = Plot.config(axes, beginAtZero.value, plotType.value);
  chart = new Chart("chart", config);

  chart.data = formatValues(gridData.value, axes);
  chart.update();

  if (xMin !== undefined && xMax !== undefined) {
    chart.zoomScale("x", { min: xMin, max: xMax }, "none");
  }
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
    coverage: coverage.value
  });

  activeMeantype.value = meantype.value;
  collapsed.value = true;

  var axes = getAxes(gridData.value);
  let config = Plot.config(axes, beginAtZero.value, plotType.value);
  chart = new Chart("chart", config);

  chart.data = formatValues(gridData.value, axes);
  chart.update();

  Eventy.hideMessage();
};

const onDownload = async () => {
  if (pivotView.value) {
    downloadCsv(pivotData.value, pivotColumns.value, "historical_data_pivot");
    return;
  }
  Eventy.showMessage("Downloading data. Please wait", "loading");
  await Service.download({
    sampling_point_ids: selectedIds.value,
    from_dt: format(fromtime.value, "yyyy-MM-dd HH:00"),
    to_dt: format(totime.value, "yyyy-MM-dd HH:00"),
    meantype: meantype.value,
    coverage: coverage.value
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

  // Build shared sorted timeline across all series
  const allTimestamps = [...new Set(meanvalues.map((o) => o.datetime))].sort();

  const series = [];
  legendItems.value = [];
  grouped_values.forEach((p, i) => {
    const color = palette[i % palette.length];
    const values = p[1];
    values.forEach((row) => (row._color = color));
    const byDatetime = new Map(values.map((o) => [o.datetime, o]));
    // Align to shared timeline so mode:"index" works across different-length series
    const data = allTimestamps.map((ts) => {
      const o = byDatetime.get(ts);
      return { x: ts.replace(" ", "T"), y: o ? o.value : null };
    });
    var axis = axes.find((a) => a == values[0].unit);
    const first = values[0];
    const equipmentPart = [first.equipment, first.equipment_identifier].filter(Boolean).join(" / ");
    const label = [first.station, first.component, first.unit, equipmentPart].filter(Boolean).join(" - ");
    legendItems.value.push({ color, label, hidden: false, sampling_point_id: p[0] });
    let serie = Plot.dataset(label, data, color, plotType.value, axis);
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

const filteredGridData = computed(() => {
  const hiddenIds = new Set(legendItems.value.filter((l) => l.hidden).map((l) => l.sampling_point_id));
  if (hiddenIds.size === 0) return gridData.value;
  return gridData.value.filter((row) => !hiddenIds.has(row.sampling_point_id));
});

const toggleSeries = (i) => {
  if (!chart) return;
  const visible = chart.isDatasetVisible(i);
  chart.setDatasetVisibility(i, !visible);
  chart.update();
  legendItems.value[i].hidden = visible;
};

const onLegendHover = (i) => {
  if (!chart || legendItems.value[i].hidden) return;
  hoveredLegendIndex.value = i;
  chart.data.datasets.forEach((dataset, idx) => {
    const color = legendItems.value[idx].color;
    const faded = hexToRgba(color, 0.2);
    const isBar = dataset.type === "bar";
    if (idx === i) {
      dataset.borderColor = color;
      dataset.backgroundColor = color;
      dataset.pointBackgroundColor = color;
      dataset.pointBorderColor = color;
      dataset.borderWidth = 3;
      dataset.pointRadius = 1;
      dataset.pointHoverRadius = 3;
    } else {
      dataset.borderColor = faded;
      dataset.backgroundColor = faded;
      dataset.pointBackgroundColor = faded;
      dataset.pointBorderColor = faded;
      dataset.borderWidth = 1;
      dataset.pointRadius = 0;
      dataset.pointHoverRadius = 0;
    }
  });
  chart.update();
};

const onLegendLeave = () => {
  if (!chart) return;
  hoveredLegendIndex.value = -1;
  chart.data.datasets.forEach((dataset, idx) => {
    const color = legendItems.value[idx].color;
    dataset.borderColor = color;
    dataset.backgroundColor = color;
    dataset.pointBackgroundColor = color;
    dataset.pointBorderColor = color;
    dataset.borderWidth = 2;
    dataset.pointRadius = 1;
    dataset.pointHoverRadius = 3;
  });
  chart.update();
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
    { field: "_color", headerName: "", width: 32, minWidth: 32, maxWidth: 32, flex: 0, sortable: false, filter: false, cellRenderer: (params) => params.value ? `<div style="width:8px;height:8px;border-radius:50%;background:${params.value};margin:auto;margin-top:8px"></div>` : "" },
    { field: "network", headerName: "Network", flex: 1, filter: true },
    { field: "station", headerName: "Station", flex: 1, filter: true },
    { field: "component", headerName: "Pollutant", flex: 0.5, filter: true },
    { headerName: "Timestep", flex: 0.5, filter: true, valueGetter: (params) => (params.data?.meantype === 0 || params.data?.meantype === 1000 ? params.data?.timestep : params.data?.meantype_string) },
    { field: "equipment", headerName: "Equipment", flex: 1, filter: true },
    { field: "equipment_identifier", headerName: "Eq. Identifier", flex: 1, filter: true },
    { field: "datetime_begin", headerName: "From", flex: 1, filter: true, hide: !isRawOrOriginal, cellRenderer: datetimeCellRenderer(granularityFromHistoricalRow) },
    { field: "datetime", headerName: isRawOrOriginal ? "To" : "Datetime", flex: 1, filter: true, sort: "desc", cellRenderer: datetimeCellRenderer(granularityFromHistoricalRow) },
    { field: "actual_value", headerName: "Value", flex: 0.5, filter: true },
    { field: "coverage", headerName: "Coverage", flex: 0.5, filter: true },
    { field: "valid", headerName: "Valid", flex: 0.5, cellRenderer: (params) => (params.value ? "✓" : "✗"), cellStyle: (params) => ({ color: params.value ? "#a3be8c" : "#bf616a", fontWeight: "bold", textAlign: "center" }) }
  ];
});

const getRowStyle = (params) => {
  if (!params.data) return {};
  return params.data.valid === false ? { background: "rgba(191, 97, 106, 0.1)" } : {};
};

const onTimeseriesGridReady = (api) => {
  timeseriesGridApi.value = api;
};

const onTimeseriesFirstDataRendered = (api) => {
  if (selectedIds.value.length > 0) {
    api.forEachNode((node) => {
      if (selectedIds.value.includes(node.data.sampling_point_id)) {
        node.setSelected(true);
      }
    });
  }
};

const onTimeseriesSelectionChanged = (rows) => {
  selectedIds.value = rows.map((r) => r.sampling_point_id);
};

const pivotView = ref(false);

const pivotColumns = computed(() => {
  if (!filteredGridData.value.length) return [];
  const isRawOrOriginal = activeMeantype.value === "1000" || activeMeantype.value === "0";
  const uniqueSps = [...new Map(filteredGridData.value.map((r) => [r.sampling_point_id, r])).values()];
  const cols = [];
  if (isRawOrOriginal) {
    cols.push({ field: "datetime_begin", headerName: "From", flex: 1, filter: true });
  }
  cols.push({ field: "datetime", headerName: isRawOrOriginal ? "To" : "Datetime", flex: 1, filter: true, sort: "desc" });
  uniqueSps.forEach((sp) => {
    const equipmentPart = [sp.equipment, sp.equipment_identifier].filter(Boolean).join(" / ");
    const label = [sp.station, sp.component, sp.unit, equipmentPart].filter(Boolean).join(" / ");
    cols.push({ field: `sp_${sp.sampling_point_id}`, headerName: label, flex: 1, filter: true });
  });
  return cols;
});

const pivotData = computed(() => {
  if (!filteredGridData.value.length) return [];
  const byDatetime = new Map();
  filteredGridData.value.forEach((row) => {
    const key = row.datetime;
    if (!byDatetime.has(key)) {
      byDatetime.set(key, { datetime: row.datetime, datetime_begin: row.datetime_begin });
    }
    byDatetime.get(key)[`sp_${row.sampling_point_id}`] = row.actual_value;
  });
  return [...byDatetime.values()].sort((a, b) => b.datetime.localeCompare(a.datetime));
});
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

    <Transition name="collapse">
      <Container v-show="!collapsed">
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

      <div class="h-64">
        <div class="font-bold">Sampling Points</div>
        <DataTable :font-size="11" :columns="timeseriesColumns" :data="cmp_timeseries" selection-mode="multiRow" :get-row-id="(params) => params.data.sampling_point_id" @grid-ready="onTimeseriesGridReady" @first-data-rendered="onTimeseriesFirstDataRendered" @selection-changed="onTimeseriesSelectionChanged" />
      </div>

      <div class="mt-6">
        <button class="button" @click="plotData" :disabled="selectedIds.length == 0">Plot data</button>
      </div>
      </Container>
    </Transition>

    <Transition name="collapse">
      <Container v-show="collapsed">
      <div class="flex flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-3 text-sm text-nord3">
          <span class="text-nord10 font-semibold">{{ format(fromtime, "yyyy-MM-dd HH:mm") }}</span>
          <span class="text-nord4">→</span>
          <span class="text-nord10 font-semibold">{{ format(totime, "yyyy-MM-dd HH:mm") }}</span>
          <span class="text-nord4">|</span>
          <span class="font-semibold text-nord2">{{ meantypeLabel }}</span>
          <template v-if="meantypeLabel !== 'Raw' && meantypeLabel !== 'Original'">
            <span class="text-nord4">|</span>
            <span>
              Coverage
              <span class="font-semibold">{{ coverage }}%</span>
            </span>
          </template>
          <span class="text-nord4">|</span>
          <span>
            <span class="font-semibold">{{ selectedIds.length }}</span>
            sampling point{{ selectedIds.length !== 1 ? "s" : "" }}
          </span>
        </div>
        <div class="flex gap-2">
          <button class="button flex items-center gap-1.5" @click="collapsed = false">
            <IconModify class="text-base" />
            Modify
          </button>
          <button class="button flex items-center gap-1.5" @click="plotData" :disabled="selectedIds.length == 0">
            <IconReplot class="text-base" />
            Re-plot
          </button>
        </div>
      </div>
    </Container>
    </Transition>

    <Container v-show="showPlot" class="mt-4 p-4! w-full h-96">
      <div class="flex justify-between mb-2 gap-4">
        <div class="flex flex-wrap items-center gap-x-4 gap-y-1">
          <div v-for="(item, i) in legendItems" :key="item.label" class="flex items-center gap-1.5 cursor-pointer select-none" :style="{ opacity: item.hidden ? 0.35 : (hoveredLegendIndex === -1 || hoveredLegendIndex === i ? 1 : 0.35) }" @click="toggleSeries(i)" @mouseenter="onLegendHover(i)" @mouseleave="onLegendLeave">
            <div :style="{ width: '8px', height: '8px', borderRadius: '50%', background: item.color, flexShrink: 0 }"></div>
            <span class="text-xs text-nord3">{{ item.label }}</span>
          </div>
        </div>
        <div class="flex items-center gap-6 shrink-0">
          <div class="flex gap-2">
            <label class="self-center cursor-pointer font-bold" @click="beginAtZero = !beginAtZero">Start Y-axis at zero:</label>
            <input type="checkbox" class="self-center" v-model="beginAtZero" />
          </div>
          <div class="flex gap-2">
            <label class="self-center cursor-pointer font-bold" @click="plotType = plotType === 'bar' ? 'line' : 'bar'">Bar chart:</label>
            <input type="checkbox" class="self-center" :checked="plotType === 'bar'" @change="plotType = plotType === 'bar' ? 'line' : 'bar'" />
          </div>
        </div>
      </div>
      <div class="h-full w-full py-4">
        <canvas id="chart" @dblclick="onResetZoom" style="cursor: crosshair"></canvas>
      </div>
    </Container>

    <Container v-show="showPlot" class="flex-1 mt-4 min-h-48">
      <div class="flex justify-end mb-2">
        <div class="flex items-center gap-1.5 cursor-pointer select-none text-sm font-bold" @click="pivotView = !pivotView" :title="pivotView ? 'Switch to row view' : 'Switch to pivot view'">
          <component :is="pivotView ? IconList : IconPivot" class="text-base text-nord10" />
          {{ pivotView ? "Row view" : "Pivot view" }}
        </div>
      </div>
      <DataTable v-if="!pivotView" :columns="gridDataColumns" :data="filteredGridData" :get-row-style="getRowStyle"></DataTable>
      <DataTable v-else :columns="pivotColumns" :data="pivotData"></DataTable>
    </Container>
  </CommonLayout>
</template>

<style>
.collapse-enter-active,
.collapse-leave-active {
  transition: max-height 0.3s ease, opacity 0.3s ease;
  overflow: hidden;
}
.collapse-enter-from,
.collapse-leave-to {
  max-height: 0;
  opacity: 0;
}
.collapse-enter-to,
.collapse-leave-from {
  max-height: 800px;
  opacity: 1;
}
</style>
