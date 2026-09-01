<script setup>
import { ref, computed, onMounted, shallowRef } from "vue";
import CommonLayout from "../../../components/CommonLayout.vue";
import ToolBar from "../../../components/ToolBar.vue";
import Container from "../../../components/Container.vue";
import DataTable from "../../../components/DataTable.vue";
import ObservationLog from "../../../components/observationlog/ObservationLogPopup.vue";
import FavoritesPicker from "../../../components/favorites/FavoritesPicker.vue";
import IconClose from "~icons/mdi/close";

import Service from "./service";
import { month, downloadCsv } from "../../../helpers/utils";
import Eventy from "../../../helpers/eventy";
import { filterList } from "../../../helpers/utils";

import IconLink from "~icons/ph/link-simple-duotone";
import IconCircle from "~icons/ph/circle-duotone";
import IconHistory from "~icons/ph/clock-counter-clockwise-duotone";
import IconArchive from "~icons/mdi/history";

const year = ref("");
const stationId = ref();

const datasets = ref([]);
const stations = ref([]);
const q = ref("");

const selected = ref({});

const showTable = ref(false);
const showLog = ref(false);
const logCtx = ref({ samplingPointId: null, fromDt: null, toDt: null });

const columns = shallowRef([
  { field: "id", headerName: "Id", width: 100 },
  { field: "station", headerName: "Station", flex: 1 },
  { field: "pollutant", headerName: "Pollutant/Meteo", flex: 1 },
  { field: "timestep", headerName: "Timestep", width: 120 },
  {
    field: "month",
    headerName: "Month",
    width: 120,
    valueGetter: (params) => month(params.data.month)
  },
  { field: "verified", headerName: "Verified", width: 100 },
  { field: "pre_verified", headerName: "Pre verified", width: 120 },
  { field: "not_verified", headerName: "Not verified", width: 120 }
]);

onMounted(async () => {
  stations.value = await Service.stations();
  if (stations.value.length) stationId.value = stations.value[0].id;
});

// ACTIONS //
const showDatasets = async () => {
  Eventy.showMessage("Loading data. Please wait", "loading");
  showTable.value = true;
  await load();
  Eventy.hideMessage();
};

const load = async () => {
  datasets.value = await Service.datasets({ year: parseInt(year.value), station_id: stationId.value });
  await loadPluginMenu();
};

// PLUGIN CONTEXT MENU //
//
// Deliberately unlike Validate.vue's `validateContextMenu`, which breaks after the first
// plugin: here every plugin that registers `verifyContextMenu` contributes items, because
// these are additive read-only entries rather than a replacement for the page's own actions.
//
// A hook may narrow itself to specific rows via getRowAvailability, returning the
// "<samplingPointId>:<month>" keys it can serve. That keeps a plugin from advertising an
// action that leads to an empty dialog. Omitting it means "every row".
const pluginMenu = ref([]);

const loadPluginMenu = async () => {
  const entries = [];
  for (const p of Object.values(window.__ravenPlugins || {})) {
    const hook = p.verifyContextMenu;
    if (!hook) continue;

    // A plugin that throws must not take the page's own context menu down with it.
    const items = (await Promise.resolve(hook.getItems?.()).catch(() => [])) || [];
    if (!items.length) continue;

    let rows = null;
    if (hook.getRowAvailability) {
      const keys = await Promise.resolve(
        hook.getRowAvailability({
          stationId: stationId.value,
          year: parseInt(year.value),
          rows: datasets.value.map((d) => ({ id: d.id, month: d.month }))
        })
      ).catch(() => null);
      if (keys) rows = new Set(keys);
    }

    for (const item of items) {
      entries.push({ idx: entries.length, pluginId: p.pluginId, hook, item, rows });
    }
  }
  pluginMenu.value = entries;
};

const pluginItemsFor = (row) => {
  if (!row) return [];
  const key = `${row.id}:${row.month}`;
  return pluginMenu.value.filter((e) => e.rows === null || e.rows.has(key));
};

// STYLING //
const getRowStyle = (params) => {
  const row = params.data;
  if (!row) return null;

  if (row.pre_verified > 0 && row.verified == 0 && row.not_verified == 0) {
    return { background: "rgba(235, 203, 139, 0.2)" }; // nord13/20
  } else if (row.not_verified > 0 && row.verified == 0 && row.pre_verified == 0) {
    return { background: "rgba(191, 97, 106, 0.1)" }; // nord11/10
  } else if (row.verified == 0) {
    return { background: "rgba(208, 135, 112, 0.1)" }; // nord12/10
  }

  return null;
};

// COMPUTED //

const cmp_years = computed(() => {
  const s = stations.value.find((p) => p.id == stationId.value);
  if (!s) return "";

  year.value = String(s.to_year);
  const l = s.to_year - s.from_year + 1;
  return Array.from({ length: l }, (_, i) => i + s.from_year)
    .reverse()
    .map((p) => String(p));
});

// Optional favorite filter: only show datasets whose sampling point is in the
// favorite. String-normalize ids — favorites may store them as numbers.
const activeFavorite = ref(null);

const cmp_datasets = computed(() => {
  let list = datasets.value;
  if (activeFavorite.value) {
    const ids = new Set((activeFavorite.value.config?.seriesIds || []).map(String));
    list = list.filter((d) => ids.has(String(d.id)));
  }
  return filterList(q.value, list);
});

// EVENTS //
const onContextMenuAction = async ({ action, data }) => {
  if (data?.row) {
    selected.value = data.row;
  }

  if (action === "verified") {
    await onSetLevel(1);
  } else if (action === "pre-verified") {
    await onSetLevel(2);
  } else if (action === "not-verified") {
    await onSetLevel(3);
  } else if (action === "history") {
    await onShowHistory();
  } else if (action.startsWith("plugin:")) {
    const entry = pluginMenu.value[parseInt(action.slice(7))];
    if (!entry) return;
    await Promise.resolve(
      entry.hook.onSelect(entry.item, {
        row: selected.value,
        year: parseInt(year.value),
        reload: load,
        showMessage: (msg, type) => Eventy.showHideMessage(msg, type || "success")
      })
    ).catch((err) => Eventy.showHideMessage(err?.message || "Plugin action failed", "error"));
  }
};

const onSetLevel = async (level) => {
  Eventy.showMessage("Setting verification flag. Please wait", "loading");
  const data = { sampling_point_id: selected.value.id, year: year.value, month: selected.value.month, level: level };
  await Service.flag(data);
  await load();
  Eventy.showHideMessage("Verification flag updated", "success");
};

const onShowHistory = () => {
  const row = selected.value;
  if (!row?.id) return;
  const m = parseInt(row.month);
  const y = parseInt(year.value);
  const fromDt = `${y}-${String(m).padStart(2, "0")}-01 00:00`;
  const nextMonth = m === 12 ? `${y + 1}-01-01 00:00` : `${y}-${String(m + 1).padStart(2, "0")}-01 00:00`;
  // The popup fetches and pages itself, so there is no pre-fetch to wait on and no
  // loading toast. It also no longer stops at the first 500 entries.
  logCtx.value = { samplingPointId: row.id, fromDt, toDt: nextMonth };
  showLog.value = true;
};

const onDownload = () => {
  // Export filtered datasets to CSV
  const csvData = cmp_datasets.value.map((row) => ({
    Id: row.id,
    Station: row.station,
    "Pollutant/Meteo": row.pollutant,
    Timestep: row.timestep,
    Month: month(row.month),
    Verified: row.verified,
    "Pre verified": row.pre_verified,
    "Not verified": row.not_verified
  }));
  downloadCsv(csvData, null, "verify");
};
</script>

<template>
  <common-layout>
    <observation-log
      :show="showLog"
      :sampling-point-id="logCtx.samplingPointId"
      :from-dt="logCtx.fromDt"
      :to-dt="logCtx.toDt"
      @close="showLog = false"
    />

    <tool-bar title="Verify" v-model:q="q" :show-filter="true" :show-add="false" :show-column-picker="false" @download-click="onDownload" />

    <container>
      <div class="flex gap-3">
        <div>
          <div class="font-bold">Station</div>
          <select class="select w-56" v-model="stationId">
            <option v-for="opt in stations" :key="opt.id" :value="opt.id">{{ opt.name }}</option>
          </select>
        </div>
        <div>
          <div class="font-bold">Year</div>
          <select class="select w-40" v-model="year">
            <option v-for="y in cmp_years" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
        <div>
          <div>&nbsp;</div>
          <button class="button" @click="showDatasets">Show datasets</button>
        </div>
        <div>
          <div>&nbsp;</div>
          <div class="flex items-center gap-2 h-9">
            <FavoritesPicker title="Filter by favorite" @select="activeFavorite = $event" />
            <div v-if="activeFavorite" class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-nord6 border border-nord4 text-xs text-nord2 cursor-pointer hover:border-nord11 select-none" title="Clear favorite filter" @click="activeFavorite = null">
              <span class="truncate max-w-40">{{ activeFavorite.name }}</span>
              <icon-close class="text-nord3" />
            </div>
          </div>
        </div>
      </div>
      <div class="text-sm flex gap-1 mt-2">
        <icon-link />
        <div><a href="http://dd.eionet.europa.eu/vocabulary/aq/observationverification/view" target="_blank">Read more about verification levels here</a></div>
      </div>
    </container>

    <div class="mt-4 h-full" v-if="showTable">
      <DataTable :data="cmp_datasets" :columns="columns" :get-row-style="getRowStyle" :filter="false" :floating-filter="false" @context-menu-action="onContextMenuAction">
        <template #context-menu-items="{ handleAction, contextData }">
          <div class="px-2 font-bold text-base text-nord3">Set verification:</div>
          <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('verified')" v-if="contextData?.row && (contextData.row.pre_verified > 0 || contextData.row.not_verified > 0)">
            <icon-circle class="text-nord14 text-base self-center" />
            <div class="self-center ml-1">Set to verified</div>
          </div>
          <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('pre-verified')" v-if="contextData?.row && (contextData.row.verified > 0 || contextData.row.not_verified > 0)">
            <icon-circle class="text-nord13 text-base self-center" />
            <div class="self-center ml-1">Set to pre verified</div>
          </div>
          <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('not-verified')" v-if="contextData?.row && (contextData.row.pre_verified > 0 || contextData.row.verified > 0)">
            <icon-circle class="text-nord11 text-base self-center" />
            <div class="self-center ml-1">Set to not verified</div>
          </div>
          <div class="border-t border-nord4 my-1" v-if="contextData?.row" />
          <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('history')" v-if="contextData?.row">
            <icon-history class="text-nord9 text-base self-center" />
            <div class="self-center ml-1">View history</div>
          </div>
          <!-- Plugin-contributed entries, only for rows the plugin said it can serve. -->
          <div
            v-for="entry in pluginItemsFor(contextData?.row)"
            :key="`${entry.pluginId}:${entry.idx}`"
            class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6"
            @click="handleAction(`plugin:${entry.idx}`)"
          >
            <icon-archive class="text-nord3 text-base self-center" />
            <div class="self-center ml-1">{{ entry.item.label }}</div>
          </div>
        </template>
      </DataTable>
    </div>
  </common-layout>
</template>

