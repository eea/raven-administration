<script setup>
import { ref, computed, onMounted, watch, nextTick, defineComponent, markRaw, h } from "vue";
import { useRoute } from "vue-router";

import { format, sub, isAfter, isBefore } from "date-fns";
import Chart from "chart.js/auto";
import "chartjs-adapter-luxon";

import CommonLayout from "../../../components/CommonLayout.vue";
import DatetimePicker from "../../../components/DatetimePicker.vue";
import DateRangePresets from "../../../components/DateRangePresets.vue";
import ToolBar from "../../../components/ToolBar.vue";
import Container from "../../../components/Container.vue";
import DataTable from "../../../components/DataTable.vue";
import CMenu from "../../../components/CMenu.vue";
import ObservationLogPopup from "../../../components/observationlog/ObservationLogPopup.vue";
import FavoritesPicker from "../../../components/favorites/FavoritesPicker.vue";
import FlagMenuItems from "./FlagMenuItems.vue";
import IconClose from "~icons/mdi/close";

import IconLink from "~icons/ph/link-simple-duotone";
import IconHistory from "~icons/ph/clock-counter-clockwise-duotone";

import Eventy from "../../../helpers/eventy";
import { downloadCsv } from "../../../helpers/utils";

import Service from "./service";
import Plot from "./plot";

const timeseries = ref([]);

const fromtime = ref(sub(new Date(), { days: 14 }));
const totime = ref(new Date());
const selectedId = ref();

const onPresetSelect = ({ from, to }) => {
  fromtime.value = from;
  totime.value = to;
};

const timevalues = ref([]);
const groupMembers = ref([]);
const gridApi = ref(null);
const showValidOnly = ref(false);

const showPlotAndTable = ref(false);

// Log popup state
const showLog = ref(false);
const logRow = ref(null);

const openLog = (row) => {
  logRow.value = row;
  showLog.value = true;
};

// Cell renderer for the log icon column
const LogCellRenderer = markRaw(
  defineComponent({
    props: ["params"],
    setup(props) {
      const onClick = (e) => {
        e.stopPropagation();
        props.params.onLogClick(props.params.data);
      };
      return () =>
        h("div", { style: "display:flex;align-items:center;justify-content:center;height:100%;cursor:pointer", onClick }, [
          h(IconHistory, { style: "color:var(--color-nord9);font-size:12px" })
        ]);
    }
  })
);

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
    ...(pluginMenuHook.value?.columnExtension?.replacesValidation
      ? [pluginMenuHook.value.columnExtension.colDef]
      : [
          { field: "observationvalidity_id", headerName: "Validation", width: 120 },
          ...(pluginMenuHook.value?.columnExtension ? [pluginMenuHook.value.columnExtension.colDef] : [])
        ]
    ),
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
    },
    {
      headerName: "",
      width: 28,
      minWidth: 28,
      maxWidth: 28,
      flex: 0,
      sortable: false,
      resizable: false,
      suppressSizeToFit: true,
      cellStyle: { padding: "0", display: "flex", alignItems: "center", justifyContent: "center" },
      cellRenderer: LogCellRenderer,
      cellRendererParams: { onLogClick: openLog }
    }
  ];
});

let chart;

onMounted(async () => {
  timeseries.value = await Service.timeseries();

  // Check if any plugin has registered a validateContextMenu override
  const plugins = window.__ravenPlugins || {};
  for (const p of Object.values(plugins)) {
    if (p.validateContextMenu) {
      pluginMenuHook.value = p.validateContextMenu;
      pluginMenuItems.value = await p.validateContextMenu.getItems().catch(() => []);
      break;
    }
  }

  if (route.query.ids) selectedId.value = route.query.ids.split(";")[0];
  if (route.query.from) fromtime.value = new Date(route.query.from);
  if (route.query.to) totime.value = new Date(route.query.to);
  // ?ts=<observation to_time> — set by right-clicking a point on a Dashboard chart. Held
  // until load() has rows, then scrolled to and highlighted.
  if (route.query.ts) pendingScrollTs.value = route.query.ts;
  if (route.query.ids || route.query.from || route.query.to) showData();
});

watch(
  () => showValidOnly.value,
  () => {
    formatAndLoad();
  }
);

// Optional favorite filter: narrow the timeseries dropdown to the favorite's
// series. String-normalize ids — favorites may store them as numbers.
const activeFavorite = ref(null);

const cmp_timeseries = computed(() => {
  let list = timeseries.value;
  if (activeFavorite.value) {
    const ids = new Set((activeFavorite.value.config?.seriesIds || []).map(String));
    list = list.filter((t) => ids.has(String(t.value)));
  }
  return list.filter((t) => {
    if (!t.fromtime && !t.totime) return true;
    return isAfter(new Date(t.totime), fromtime.value) && isBefore(new Date(t.fromtime), totime.value);
  });
});

const applyFavorite = (favorite) => {
  activeFavorite.value = favorite;
  const options = cmp_timeseries.value;
  if (options.length === 1) selectedId.value = options[0].value;
};

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
  highlightId.value = null;
  const response = await Service.get({
    sampling_point_id: selectedId.value,
    from_dt: format(fromtime.value, "yyyy-MM-dd HH:00"),
    to_dt: totime.value ? format(totime.value, "yyyy-MM-dd HH:00") : ""
  });
  // Support both old format (flat array) and new format ({rows, members})
  const rows = Array.isArray(response) ? response : (response.rows ?? []);
  const members = Array.isArray(response) ? [] : (response.members ?? []);
  timevalues.value = rows;
  if (pluginMenuHook.value?.columnExtension?.getRowData && rows.length) {
    const ids = rows.map(r => r.id);
    const extra = await pluginMenuHook.value.columnExtension.getRowData(ids).catch(() => new Map());
    timevalues.value = rows.map(r => ({ ...r, ...(extra.get(r.id) ?? {}) }));
  }
  groupMembers.value = members;
  const sp = timeseries.value.find((t) => String(t.value) === String(selectedId.value));
  const timestep = sp?.timestep_seconds ?? null;
  if (chart) { chart.destroy(); chart = null; }
  chart = new Chart("chart", Plot.config(onDatapointSelection, timestep));
  formatAndLoad();

  // Consumed once, so the plugin's reload callback and the post-validate reload below
  // don't yank the table back to the deep-linked row.
  if (pendingScrollTs.value) {
    const ts = pendingScrollTs.value;
    pendingScrollTs.value = null;
    await scrollToTimestamp(ts);
  }
};
const formatAndLoad = () => {
  chart.data = formatValues();
  chart.update();
};

const getRowStyle = (params) => {
  const row = params.data;
  if (!row) return { background: "" };

  // The deep-linked row (?ts=) wins over the invalid-row tint: making that one row
  // obvious is the entire point of the jump from the Dashboard.
  if (highlightId.value != null && row.id === highlightId.value) {
    return {
      background: "rgba(129, 161, 193, 0.35)", // nord9
      outline: "1px solid var(--color-nord10)",
      outlineOffset: "-1px"
    };
  }

  // outline is reset explicitly: ag-Grid assigns these styles onto the row element, so a
  // key left out of the object keeps whatever the highlight branch last set.
  if (row.observationvalidity_id < 1) {
    return { background: "rgba(191, 97, 106, 0.1)", outline: "" }; // nord11/10
  }

  return { background: "", outline: "" };
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
  // Plugin QA flag action
  if (pluginMenuHook.value && action.startsWith('plugin:')) {
    const qaId = parseInt(action.slice(7));
    const item = pluginMenuItems.value.find(i => i.id === qaId);
    if (item) {
      const selectedRows = gridApi.value?.getSelectedRows() || [];
      const ids = selectedRows.length > 0 ? selectedRows.map(r => r.id) : (data?.row ? [data.row.id] : []);
      await pluginMenuHook.value.onSelect(item, {
        selectedIds: ids,
        samplingPointId: selectedId.value,
        reload: load,
        showMessage: (msg, type) => Eventy.showHideMessage(msg, type, 3000),
      });
    }
    return;
  }
  // Default EEA validation flag actions
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

// Deep-link target from the Dashboard: ?ts=<observation to_time>
const pendingScrollTs = ref(null);
const highlightId = ref(null);

const parseTs = (value) => new Date(String(value).replace(" ", "T")).getTime();

// ag-Grid receives rowData through a prop watcher, so the row nodes may not exist yet on
// the tick the response lands. first-data-rendered is no help here: the grid sits inside a
// v-show and mounts with empty data, so it may already have fired.
const waitForRows = async () => {
  for (let i = 0; i < 5; i++) {
    if (gridApi.value?.getDisplayedRowCount()) return true;
    await new Promise((resolve) => requestAnimationFrame(resolve));
  }
  return !!gridApi.value?.getDisplayedRowCount();
};

const scrollToTimestamp = async (ts) => {
  const target = parseTs(ts);
  if (Number.isNaN(target) || !timevalues.value.length) return;

  await nextTick();
  const ready = await waitForRows();
  if (!ready) return;

  // Nearest row, not an exact match. The Dashboard sends the observation's to_time in the
  // same 'YYYY-MM-DD HH:MM:SS' format so this normally lands exactly, but nearest keeps
  // working if the Dashboard ever moves off meantype 0 and sends aggregate boundaries.
  let best = null;
  let bestDiff = Infinity;
  gridApi.value.forEachNode((node) => {
    const diff = Math.abs(parseTs(node.data?.totime) - target);
    if (diff < bestDiff) {
      bestDiff = diff;
      best = node;
    }
  });
  if (!best) return;

  gridApi.value.deselectAll();
  best.setSelected(true);
  highlightId.value = best.data.id;
  gridApi.value.redrawRows(); // getRowStyle owns the highlight, so it has to re-run
  // Node, not row index: the grid is sorted 'fromtime desc', the reverse of the response.
  gridApi.value.ensureNodeVisible(best, "middle");
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

// Plugin context menu override — populated at mount if any plugin registers validateContextMenu
const pluginMenuItems = ref([]);
const pluginMenuHook = ref(null);

const chartMenuRef = ref(null);

const onDatapointSelection = (event, sel) => {
  if (!sel?.length) return;
  const row = sel[0].element.$context.raw.obj;
  // Select the corresponding grid row
  if (gridApi.value) {
    gridApi.value.deselectAll();
    gridApi.value.forEachNode((node) => {
      if (node.data.id === row.id) node.setSelected(true);
    });
  }
  // Same { row } shape DataTable passes for a grid right-click, so onContextMenuAction
  // serves both entry points. CMenu owns the placement — this menu used to clamp with a
  // bare Math.min, which put a 36-flag list at a negative top and hid its first items.
  chartMenuRef.value?.showMenu({ row }, event.native);
};

const getRowId = (params) => String(params.data.id);
</script>

<template>
  <common-layout>
    <observation-log-popup
      :show="showLog"
      :sampling-point-id="logRow?.sampling_point_id"
      :from-dt="logRow?.fromtime"
      :to-dt="logRow?.totime"
      @close="showLog = false"
    />
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
        <div>
          <br />
          <DateRangePresets @select="onPresetSelect" />
        </div>
      </div>

      <div>
        <div class="font-bold flex items-center gap-2">
          Timeseries
          <FavoritesPicker title="Filter by favorite" @select="applyFavorite" />
          <div v-if="activeFavorite" class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-nord6 border border-nord4 text-xs font-normal text-nord2 cursor-pointer hover:border-nord11 select-none" title="Clear favorite filter" @click="activeFavorite = null">
            <span class="truncate max-w-40">{{ activeFavorite.name }}</span>
            <icon-close class="text-nord3" />
          </div>
        </div>
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
            <flag-menu-items :items="pluginMenuItems" @select="handleAction" />
          </template>
        </DataTable>
      </div>
    </div>
  </common-layout>

  <!-- Flag menu triggered by a chart datapoint click. Same items and same handler as the
       grid's right-click menu; CMenu keeps it inside the viewport. -->
  <c-menu ref="chartMenuRef" @on-click="onContextMenuAction">
    <template #default="{ handleAction }">
      <flag-menu-items :items="pluginMenuItems" @select="handleAction" />
    </template>
  </c-menu>
</template>
