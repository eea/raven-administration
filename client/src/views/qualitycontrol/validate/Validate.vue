<script setup>
import { ref, computed, onMounted, watch, nextTick } from "vue";
import { useRoute } from "vue-router";

import { format, sub, isAfter, isBefore } from "date-fns";
import Chart from "chart.js/auto";
import "chartjs-adapter-luxon";

import CommonLayout from "../../../components/CommonLayout.vue";
import DatetimePicker from "../../../components/DatetimePicker.vue";
import ToolBar from "../../../components/ToolBar.vue";
import Container from "../../../components/Container.vue";
import DataTable from "../../../components/DataTable.vue";

import IconCircle from "~icons/ph/circle-duotone";
import IconLink from "~icons/ph/link-simple-duotone";

import Eventy from "../../../helpers/eventy";
import { downloadCsv } from "../../../helpers/utils";

import Service from "./service";
import Plot from "./plot";

const timeseries = ref([]);

const fromtime = ref(sub(new Date(), { days: 14 }));
const totime = ref(new Date());
const selectedId = ref();

const timevalues = ref([]);
const groupMembers = ref([]);
const gridApi = ref(null);
const showValidOnly = ref(false);

const showPlotAndTable = ref(false);

const route = useRoute();

const columns = computed(() => {
  const members = groupMembers.value ?? [];
  const groupHeader = members.map((m) => m.label).join(" / ");
  const memberSpIds = members.map((m) => m.sampling_point_id);

  return [
    { field: "fromtime", headerName: "From", flex: 1, sort: "desc" },
    { field: "totime", headerName: "To", flex: 1 },
    { field: "value", headerName: "Value", width: 120 },
    ...(members.length ? [{
      headerName: groupHeader,
      width: 150,
      valueGetter: (params) => memberSpIds.map((id) => {
        const v = params.data[`m_${id}_value`];
        return v != null ? v : "-";
      }).join(" / ")
    }] : []),
    { field: "import_value", headerName: "Import value", width: 120 },
    { field: "observationvalidity_id", headerName: "Validation", width: 120 },
    {
      field: "observationverification_id",
      headerName: "Verification",
      width: 120,
      cellRenderer: (params) => {
        const value = params.value;
        if (value === 1) {
          return `<div class="flex gap-1 items-center"><span>${value}</span><svg class="text-xs text-nord14" style="width: 12px; height: 12px; display: inline-block;" viewBox="0 0 256 256" fill="currentColor"><path d="M208,80H96V48a8,8,0,0,1,16,0,8,8,0,0,0,16,0,24,24,0,0,0-48,0V80H48A16,16,0,0,0,32,96V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V96A16,16,0,0,0,208,80Zm0,128H48V96H208V208Zm-68-56a12,12,0,1,1-12-12A12,12,0,0,1,140,152Z"></path></svg></div>`;
        }
        return value;
      }
    }
  ];
});

let chart;

onMounted(async () => {
  timeseries.value = await Service.timeseries();

  if (route.query.ids) selectedId.value = route.query.ids.split(";")[0];
  if (route.query.from) fromtime.value = new Date(route.query.from);
  if (route.query.to) totime.value = new Date(route.query.to);
  if (route.query.ids || route.query.from || route.query.to) showData();
});

watch(
  () => showValidOnly.value,
  () => {
    formatAndLoad();
  }
);

const cmp_timeseries = computed(() => {
  return timeseries.value.filter((t) => {
    if (!t.fromtime && !t.totime) return true;
    return isAfter(new Date(t.totime), fromtime.value) && isBefore(new Date(t.fromtime), totime.value);
  });
});

const showData = async () => {
  Eventy.showMessage("Loading data. Please wait", "loading");
  showPlotAndTable.value = true;
  timevalues.value = [];
  groupMembers.value = [];
  if (chart) {
    chart.data = [];
    chart.update();
  }
  await load();
  Eventy.hideMessage();
};

const load = async () => {
  const response = await Service.get({
    sampling_point_id: selectedId.value,
    from_dt: format(fromtime.value, "yyyy-MM-dd HH:00"),
    to_dt: totime.value ? format(totime.value, "yyyy-MM-dd HH:00") : ""
  });
  // Support both old format (flat array) and new format ({rows, members})
  const rows = Array.isArray(response) ? response : (response.rows ?? []);
  const members = Array.isArray(response) ? [] : (response.members ?? []);
  timevalues.value = rows;
  groupMembers.value = members;
  if (!chart) {
    chart = new Chart("chart", Plot.config(onDatapointSelection));
  }
  formatAndLoad();
};
const formatAndLoad = () => {
  chart.data = formatValues();
  chart.update();
};

const getRowStyle = (params) => {
  const row = params.data;
  if (!row) return { background: "" };

  if (row.observationvalidity_id < 1) {
    return { background: "rgba(191, 97, 106, 0.1)" }; // nord11/10
  }

  return { background: "" };
};

const onDownload = () => {
  const o = timeseries.value.find((p) => p.value == selectedId.value);
  if (o) {
    const name = o.label.replaceAll(", ", "-");
    const columnMapping = {
      fromtime: "From",
      totime: "To",
      value: "Value",
      import_value: "Import value",
      observationvalidity_id: "Validation",
      observationverification_id: "Verification"
    };
    downloadCsv(timevalues.value, columnMapping, name);
  }
};

const onContextMenuAction = async ({ action, data }) => {
  // Handle validation flag actions
  if (["-99", "-1", "1", "2", "3"].includes(action)) {
    const flag = parseInt(action);
    await onValidate(flag, data?.row);
  }
};

const onValidate = async (flag, row) => {
  Eventy.showMessage("Setting validation flag. Please wait", "loading");

  // Prioritize selected rows over right-clicked row
  const selectedRows = gridApi.value?.getSelectedRows() || [];
  let ids;

  if (selectedRows.length > 0) {
    // Use selected rows if any exist
    ids = selectedRows.map((p) => p.id);
  } else if (row) {
    // Otherwise use the right-clicked row
    ids = [row.id];
  } else {
    ids = [];
  }

  if (ids.length === 0) {
    Eventy.showHideMessage("No rows selected", "error", 3000);
    return;
  }

  try {
    await Service.validate({ flag, ids, sampling_point_id: selectedId.value });

    // Reload data
    const response = await Service.get({
      sampling_point_id: selectedId.value,
      from_dt: format(fromtime.value, "yyyy-MM-dd HH:00"),
      to_dt: totime.value ? format(totime.value, "yyyy-MM-dd HH:00") : ""
    });

    // Update timevalues reference (support old flat-array and new {rows,members} format)
    timevalues.value = Array.isArray(response) ? response : (response.rows ?? []);

    // Wait for DOM update
    await nextTick();

    // Force ag-grid to redraw rows to update row styles
    if (gridApi.value) {
      gridApi.value.redrawRows();
    }

    // Update chart
    if (chart) {
      chart.data = formatValues();
      chart.update();
    }

    gridApi.value?.deselectAll();
    Eventy.showHideMessage("Validation flag updated", "success");
  } catch (error) {
    console.error("Error validating:", error);
    // Display the actual error message from the server
    const errorMessage = error.message || "Error updating validation flag";
    Eventy.showHideMessage(errorMessage, "error", 5000);
  }
};

const onGridReady = (api) => {
  gridApi.value = api;
};

const formatValues = () => {
  let colors = [];
  let data = [];
  timevalues.value.forEach((o) => {
    var value_to_use = showValidOnly.value ? o.valid_value_only : o.value;
    // Invalid + -9900 → render as 0 (no meaningful measurement, don't distort axis)
    // Valid + -9900 → keep -9900 (user explicitly validated it, show actual value)
    var v = (o.observationvalidity_id < 1 && value_to_use === -9900) ? 0 : value_to_use;
    var c = o.observationvalidity_id < 1 ? "#BF616A" : "#A3BE8C";
    const n = Object.assign({}, o);
    colors.push(c);
    data.push({ x: o.totime.replace(" ", "T"), y: v, obj: n });
  });
  return { datasets: [Plot.dataset("Value", data, colors)] };
};

const chartMenu = ref({ visible: false, x: 0, y: 0, row: null });
const chartMenuRef = ref(null);

const onDatapointSelection = async (event, sel) => {
  if (!sel?.length) return;
  const row = sel[0].element.$context.raw.obj;
  // Select the corresponding grid row
  if (gridApi.value) {
    gridApi.value.deselectAll();
    gridApi.value.forEachNode((node) => {
      if (node.data.id === row.id) node.setSelected(true);
    });
  }
  // Show floating flag menu at click position, then clamp to viewport
  chartMenu.value = { visible: true, x: event.native.clientX, y: event.native.clientY, row };
  await nextTick();
  if (chartMenuRef.value) {
    const { offsetWidth: w, offsetHeight: h } = chartMenuRef.value;
    const vw = window.innerWidth, vh = window.innerHeight;
    chartMenu.value.x = Math.min(chartMenu.value.x, vw - w - 8);
    chartMenu.value.y = Math.min(chartMenu.value.y, vh - h - 8);
  }
};

const getRowId = (params) => String(params.data.id);
</script>

<template>
  <common-layout>
    <tool-bar title="Validate" :show-filter="false" :show-add="false" :show-column-picker="false" @download-click="onDownload" />

    <container>
      <div class="flex gap-2">
        <div>
          <div class="font-bold">From</div>
          <DatetimePicker v-model="fromtime" />
        </div>
        <div>
          <div class="font-bold">To</div>
          <DatetimePicker v-model="totime" />
        </div>
      </div>

      <div>
        <div class="font-bold">Timeseries</div>
        <select class="select w-full" v-model="selectedId">
          <option v-for="t in cmp_timeseries" :key="t.value" :value="t.value">{{ t.label }}</option>
          <option v-if="cmp_timeseries.length == 0" :value="0" disabled>No timeseries found for time period</option>
        </select>
      </div>

      <div class="mt-2">
        <button class="button" @click="showData" :disabled="!selectedId">Show data</button>
      </div>
      <div class="text-sm flex gap-1 mt-2">
        <icon-link />
        <div><a href="http://dd.eionet.europa.eu/vocabulary/aq/observationvalidity/view" target="_blank">Read more about validation levels here</a></div>
      </div>
    </container>

    <div v-show="showPlotAndTable" class="h-full flex flex-col gap-4 mt-4">
      <container class="p-4 h-80">
        <div class="px-2 flex w-fit gap-2">
          <div class="font-bold self-center flex-1 cursor-pointer" @click="showValidOnly = !showValidOnly">Show only valid values</div>
          <input type="checkbox" v-model="showValidOnly" class="self-center" />
        </div>
        <canvas id="chart" class="h-64!"></canvas>
      </container>

      <div class="h-full">
        <DataTable :data="timevalues" :columns="columns" :get-row-style="getRowStyle" :filter="false" :floating-filter="false" selection-mode="multiRow" :get-row-id="getRowId" @context-menu-action="onContextMenuAction" @grid-ready="onGridReady">
          <template #context-menu-items="{ handleAction }">
            <div class="px-2 font-bold text-base text-nord3">Set validation to:</div>
            <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('-99')">
              <icon-circle class="text-nord11 text-base self-center" />
              <div class="self-center ml-1">Not valid due to maintenance (-99)</div>
            </div>
            <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('-1')">
              <icon-circle class="text-nord11 text-base self-center" />
              <div class="self-center ml-1">Not valid (-1)</div>
            </div>
            <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('1')">
              <icon-circle class="text-nord14 text-base self-center" />
              <div class="self-center ml-1">Valid (1)</div>
            </div>
            <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('2')">
              <icon-circle class="text-nord14 text-base self-center" />
              <div class="self-center ml-1">Valid, below detection limit (2)</div>
            </div>
            <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('3')">
              <icon-circle class="text-nord14 text-base self-center" />
              <div class="self-center ml-1">Valid, 0.5*detection limit (3)</div>
            </div>
          </template>
        </DataTable>
      </div>
    </div>
  </common-layout>

  <!-- Floating flag menu triggered by chart click -->
  <div v-if="chartMenu.visible"
       class="fixed inset-0 z-40"
       @click.self="chartMenu.visible = false">
    <div ref="chartMenuRef" class="absolute z-50 bg-white border border-nord4 rounded shadow-lg py-1 min-w-48"
         :style="{ left: chartMenu.x + 'px', top: chartMenu.y + 'px' }">
      <div class="px-2 font-bold text-base text-nord3">Set validation to:</div>
      <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="onValidate(-99, chartMenu.row); chartMenu.visible = false">
        <icon-circle class="text-nord11 text-base self-center" />
        <div class="self-center ml-1">Not valid due to maintenance (-99)</div>
      </div>
      <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="onValidate(-1, chartMenu.row); chartMenu.visible = false">
        <icon-circle class="text-nord11 text-base self-center" />
        <div class="self-center ml-1">Not valid (-1)</div>
      </div>
      <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="onValidate(1, chartMenu.row); chartMenu.visible = false">
        <icon-circle class="text-nord14 text-base self-center" />
        <div class="self-center ml-1">Valid (1)</div>
      </div>
      <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="onValidate(2, chartMenu.row); chartMenu.visible = false">
        <icon-circle class="text-nord14 text-base self-center" />
        <div class="self-center ml-1">Valid, below detection limit (2)</div>
      </div>
      <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="onValidate(3, chartMenu.row); chartMenu.visible = false">
        <icon-circle class="text-nord14 text-base self-center" />
        <div class="self-center ml-1">Valid, 0.5*detection limit (3)</div>
      </div>
    </div>
  </div>
</template>
