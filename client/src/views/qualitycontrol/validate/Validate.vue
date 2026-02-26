<script setup>
import { ref, computed, onMounted, watch, shallowRef, nextTick } from "vue";
import { useRoute } from "vue-router";

import { format, sub, isAfter, isBefore } from "date-fns";
import Chart from "chart.js/auto";
import "chartjs-adapter-luxon";

import CommonLayout from "../../../components/CommonLayout.vue";
import DatetimePicker from "../../../components/DatetimePicker.vue";
import ToolBar from "../../../components/ToolBar.vue";
import Container from "../../../components/Container.vue";
import DataTable from "../../../components/DataTable.vue";
import CMenu from "../../../components/CMenu.vue";

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
const menuRef = ref(null);
const gridApi = ref(null);
const showValidOnly = ref(false);

const showPlotAndTable = ref(false);

const route = useRoute();

const columns = shallowRef([
  { field: "fromtime", headerName: "From", flex: 1, sort: "desc" },
  { field: "totime", headerName: "To", flex: 1 },
  { field: "value", headerName: "Value", width: 120 },
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
]);

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
  if (chart) {
    chart.data = [];
    chart.update();
  }
  await load();
  Eventy.hideMessage();
};

const load = async () => {
  timevalues.value = await Service.get({
    sampling_point_id: selectedId.value,
    from_dt: format(fromtime.value, "yyyy-MM-dd HH:00"),
    to_dt: totime.value ? format(totime.value, "yyyy-MM-dd HH:00") : ""
  });
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

const onMenuClick = async ({ action, data }) => {
  const flag = parseInt(action);
  await onValidate(flag, data);
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
    const newData = await Service.get({
      sampling_point_id: selectedId.value,
      from_dt: format(fromtime.value, "yyyy-MM-dd HH:00"),
      to_dt: totime.value ? format(totime.value, "yyyy-MM-dd HH:00") : ""
    });

    // Update timevalues reference
    timevalues.value = newData;

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

const onContextMenu = (row, e) => {
  // Select the row if it's not already selected
  if (gridApi.value) {
    const selectedRows = gridApi.value.getSelectedRows();
    const isRowSelected = selectedRows.some((r) => r.id === row.id);

    if (!isRowSelected) {
      // If Ctrl key is held, add to selection; otherwise replace selection
      if (e.ctrlKey) {
        gridApi.value.forEachNode((node) => {
          if (node.data.id === row.id) {
            node.setSelected(true);
          }
        });
      } else {
        gridApi.value.deselectAll();
        gridApi.value.forEachNode((node) => {
          if (node.data.id === row.id) {
            node.setSelected(true);
          }
        });
      }
    }
  }

  menuRef.value?.showMenu(row, e);
};

const onGridReady = (api) => {
  gridApi.value = api;
};

const formatValues = () => {
  let colors = [];
  let data = [];
  timevalues.value.forEach((o) => {
    var value_to_use = showValidOnly.value ? o.valid_value_only : o.value;
    var v = value_to_use == -9900 ? null : value_to_use;
    var c = o.observationvalidity_id < 1 ? "#BF616A" : "#A3BE8C";
    const n = Object.assign({}, o);
    colors.push(c);
    data.push({ x: o.totime.replace(" ", "T"), y: v, obj: n });
  });
  return { datasets: [Plot.dataset("Value", data, colors)] };
};

const onDatapointSelection = (event, sel, chart) => {
  const row = sel[0].element.$context.raw.obj;
  // Find and select the row in the grid
  if (gridApi.value) {
    gridApi.value.deselectAll();
    gridApi.value.forEachNode((node) => {
      if (node.data.id === row.id) {
        node.setSelected(true);
      }
    });
  }
  menuRef.value?.showMenu(row, event.native);
};

const getRowId = (params) => String(params.data.id);
</script>

<template>
  <common-layout>
    <c-menu ref="menuRef" @on-click="onMenuClick">
      <template #default="{ handleAction }">
        <div class="px-2 font-bold">Set validation to:</div>
        <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="handleAction('-99')">
          <icon-circle class="text-nord11 text-base self-center" />
          <div class="self-center ml-1">Not valid due to station maintenance or calibration (-99)</div>
        </div>
        <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="handleAction('-1')">
          <icon-circle class="text-nord11 text-base self-center" />
          <div class="self-center ml-1">Not valid (-1)</div>
        </div>
        <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="handleAction('1')">
          <icon-circle class="text-nord14 text-base self-center" />
          <div class="self-center ml-1">Valid (1)</div>
        </div>
        <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="handleAction('2')">
          <icon-circle class="text-nord14 text-base self-center" />
          <div class="self-center ml-1">Valid, but below detection limit measurement value given (2)</div>
        </div>
        <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="handleAction('3')">
          <icon-circle class="text-nord14 text-base self-center" />
          <div class="self-center ml-1">Valid, but below detection limit and number replaced by 0.5*detection limit (3)</div>
        </div>
      </template>
    </c-menu>

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
        <DataTable :data="timevalues" :columns="columns" :get-row-style="getRowStyle" :filter="false" :floating-filter="false" selection-mode="multiRow" :get-row-id="getRowId" @on-right-click="onContextMenu" @grid-ready="onGridReady" />
      </div>
    </div>
  </common-layout>
</template>
