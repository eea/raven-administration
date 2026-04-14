<script setup>
import { ref, onMounted } from "vue";
import CommonLayout from "../../../components/CommonLayout.vue";
import ToolBar from "../../../components/ToolBar.vue";
import Popup from "../../../components/Popup.vue";
import DataTable from "../../../components/DataTable.vue";
import DashboardPlot from "./DashboardPlot.vue";
import Service from "./service";
import { datetimeCellRenderer, granularityFromTimestep } from "../../../helpers/datetimeHighlight";
import IconHeart from "~icons/mdi/heart";
import IconHeartOutline from "~icons/mdi/heart-outline";
import CircleHover from "../../../components/CircleHover.vue";

const PREF_KEY = "raven_default_view";
const isDefault = ref(localStorage.getItem(PREF_KEY) === "Dashboard");
const toggleDefault = () => {
  localStorage.setItem(PREF_KEY, "Dashboard");
  isDefault.value = true;
};

const STORAGE_KEY = "raven_dashboard_plots";
const PRESETS = ["6h", "12h", "24h", "3d", "7d", "14d"];

// ── Persisted plots ──────────────────────────────────────────────────────────
const plots = ref([]);

const savePlots = () => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(plots.value));
};

const loadPlots = () => {
  try {
    plots.value = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
  } catch {
    plots.value = [];
  }
};

// ── Available timeseries (loaded once) ───────────────────────────────────────
const allTimeseries = ref([]);

onMounted(async () => {
  loadPlots();
  allTimeseries.value = await Service.samplingPoints();
});

// ── Add / Edit popup ─────────────────────────────────────────────────────────
const showPopup = ref(false);
const editingId = ref(null); // null = adding new
const formTitle = ref("");
const formPreset = ref("24h");
const formIds = ref(new Set());
const formPlotType = ref("line");
const formFullWidth = ref(false);

const timeseriesColumns = [
  { field: "station", headerName: "Station", flex: 1, filter: true },
  { field: "pollutant", headerName: "Pollutant", flex: 1, filter: true },
  { field: "timestep", headerName: "Timestep", flex: 0.7, filter: true },
  { field: "unit", headerName: "Unit", flex: 0.7, filter: true },
  { field: "equipment", headerName: "Equipment", flex: 1, filter: true },
  { field: "equipment_identifier", headerName: "Eq. ID", flex: 1, filter: true },
  { field: "totime", headerName: "Latest date", flex: 1, filter: false, cellRenderer: (params) => {
    if (!params.value) return "";
    const fmt = params.value.replace("T", " ").slice(0, 16);
    return datetimeCellRenderer((row) => granularityFromTimestep(row?.timestep))({ ...params, value: fmt });
  }}
];

const onGridFirstData = (api) => {
  api.forEachNode((node) => {
    if (formIds.value.has(node.data.sampling_point_id)) node.setSelected(true);
  });
};

const onSelectionChanged = (rows) => {
  formIds.value = new Set(rows.map((r) => r.sampling_point_id));
};

const searchQuery = ref("");
const timeseriesGrid = ref(null);

const onGridReady = (api) => {
  timeseriesGrid.value = api;
};

const onSearch = (q) => {
  searchQuery.value = q;
  timeseriesGrid.value?.setGridOption("quickFilterText", q);
};

const openAdd = () => {
  editingId.value = null;
  formTitle.value = "";
  formPreset.value = "24h";
  formIds.value = new Set();
  formPlotType.value = "line";
  formFullWidth.value = false;
  searchQuery.value = "";
  showPopup.value = true;
};

const openEdit = (plot) => {
  editingId.value = plot.id;
  formTitle.value = plot.title;
  formPreset.value = plot.timePreset;
  formIds.value = new Set(plot.seriesIds);
  formPlotType.value = plot.plotType ?? "line";
  formFullWidth.value = plot.fullWidth ?? false;
  searchQuery.value = "";
  showPopup.value = true;
};

const closePopup = () => {
  showPopup.value = false;
};

const savePopup = () => {
  const config = {
    title: formTitle.value.trim() || "Untitled",
    timePreset: formPreset.value,
    plotType: formPlotType.value,
    fullWidth: formFullWidth.value,
    seriesIds: [...formIds.value]
  };

  if (editingId.value === null) {
    plots.value.push({ id: crypto.randomUUID(), ...config });
  } else {
    const idx = plots.value.findIndex((p) => p.id === editingId.value);
    if (idx !== -1) plots.value[idx] = { ...plots.value[idx], ...config };
  }

  savePlots();
  closePopup();
};

// ── Plot events ───────────────────────────────────────────────────────────────
const onUpdate = (updated) => {
  const idx = plots.value.findIndex((p) => p.id === updated.id);
  if (idx !== -1) {
    plots.value[idx] = updated;
    savePlots();
  }
};

const onRemove = (id) => {
  plots.value = plots.value.filter((p) => p.id !== id);
  savePlots();
};
</script>

<template>
  <common-layout>
    <tool-bar title="Dashboard" :show-filter="false" :show-download="false" @add-click="openAdd">
      <CircleHover class="ml-1 self-center" @click="toggleDefault" :title="isDefault ? 'Opens here after login' : 'Open here after login'">
        <icon-heart v-if="isDefault" class="text-nord10 text-sm self-center" />
        <icon-heart-outline v-else class="text-nord3 text-sm self-center" />
      </CircleHover>
    </tool-bar>

    <!-- Responsive plot grid -->
    <div v-if="plots.length" class="p-3 grid gap-4 grid-cols-1 xl:grid-cols-2 items-start">
      <dashboard-plot v-for="(plot, i) in plots" :key="plot.id" :class="{ 'xl:col-span-2': plot.fullWidth || (!plot.fullWidth && plots.filter((p) => !p.fullWidth).length % 2 !== 0 && i === plots.length - 1) }" :plot="plot" :all-timeseries="allTimeseries" @update="onUpdate" @remove="onRemove" @edit="openEdit" />
    </div>

    <div v-else class="flex-1 flex flex-col items-center justify-center gap-3 text-nord3 select-none">
      <span class="text-sm">No plots configured yet</span>
      <button class="button" @click="openAdd">Add your first plot</button>
    </div>

    <!-- Add / Edit popup -->
    <Popup :show="showPopup" :title="editingId ? 'Edit Plot' : 'Add Plot'" @on-close="closePopup" class="w-[90%]! h-[90%]!">
      <div class="flex flex-col gap-4 pt-1 h-full">
        <!-- Title -->
        <div class="flex flex-col gap-1">
          <label class="text-xs font-bold text-nord3 uppercase tracking-wide">Title</label>
          <input v-model="formTitle" class="input" placeholder="e.g. PM2.5 – Station A" />
        </div>

        <!-- Time preset -->
        <div class="flex flex-col gap-1">
          <label class="text-xs font-bold text-nord3 uppercase tracking-wide">Time range</label>
          <div class="flex gap-2">
            <button v-for="p in PRESETS" :key="p" class="px-3 py-1 rounded border text-sm font-mono transition-colors" :class="formPreset === p ? 'bg-nord10 text-white border-nord10' : 'border-nord4 text-nord3 hover:border-nord10 hover:text-nord10'" @click="formPreset = p">
              {{ p }}
            </button>
          </div>
        </div>

        <!-- Plot type -->
        <div class="flex gap-6 items-end">
          <div class="flex flex-col gap-1">
            <label class="text-xs font-bold text-nord3 uppercase tracking-wide">Plot type</label>
            <div class="flex gap-2">
              <button v-for="t in ['line', 'bar']" :key="t" class="px-4 py-1 rounded border text-sm capitalize transition-colors" :class="formPlotType === t ? 'bg-nord10 text-white border-nord10' : 'border-nord4 text-nord3 hover:border-nord10 hover:text-nord10'" @click="formPlotType = t">
                {{ t }}
              </button>
            </div>
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-xs font-bold text-nord3 uppercase tracking-wide">Width</label>
            <div class="flex gap-2">
              <button
                v-for="opt in [
                  { label: 'Auto', val: false },
                  { label: 'Full row', val: true }
                ]"
                :key="opt.label"
                class="px-4 py-1 rounded border text-sm transition-colors"
                :class="formFullWidth === opt.val ? 'bg-nord10 text-white border-nord10' : 'border-nord4 text-nord3 hover:border-nord10 hover:text-nord10'"
                @click="formFullWidth = opt.val"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>
        </div>

        <!-- Series selector -->
        <div class="flex flex-col gap-1 h-full">
          <label class="text-xs font-bold text-nord3 uppercase tracking-wide">
            Series
            <span v-if="formIds.size" class="ml-1 text-nord10 normal-case font-normal">({{ formIds.size }} selected)</span>
          </label>
          <input :value="searchQuery" class="input" placeholder="Search station, pollutant, timestep…" @input="onSearch($event.target.value)" />
          <div class="h-full">
            <DataTable :font-size="11" :columns="timeseriesColumns" :data="allTimeseries" selection-mode="multiRow" :get-row-id="(p) => p.data.sampling_point_id" @grid-ready="onGridReady" @first-data-rendered="onGridFirstData" @selection-changed="onSelectionChanged" />
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-2 pt-1">
          <button class="button" @click="closePopup">Cancel</button>
          <button class="button button-primary" :disabled="!formTitle.trim() || !formIds.size" @click="savePopup">
            {{ editingId ? "Save" : "Add plot" }}
          </button>
        </div>
      </div>
    </Popup>
  </common-layout>
</template>
