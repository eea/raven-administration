<script setup>
import { ref, computed, onMounted, shallowRef } from "vue";
import CommonLayout from "../../../components/CommonLayout.vue";
import ToolBar from "../../../components/ToolBar.vue";
import Container from "../../../components/Container.vue";
import DataTable from "../../../components/DataTable.vue";
import ObservationLog from "./ObservationLog.vue";

import Service from "./service";
import { month, downloadCsv } from "../../../helpers/utils";
import Eventy from "../../../helpers/eventy";
import { filterList } from "../../../helpers/utils";

import IconLink from "~icons/ph/link-simple-duotone";
import IconCircle from "~icons/ph/circle-duotone";
import IconHistory from "~icons/ph/clock-counter-clockwise-duotone";

const year = ref("");
const stationId = ref();

const datasets = ref([]);
const stations = ref([]);
const q = ref("");

const selected = ref({});

const showTable = ref(false);
const showLog = ref(false);
const logRows = ref([]);

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

const cmp_datasets = computed(() => filterList(q.value, datasets.value));

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
  }
};

const onSetLevel = async (level) => {
  Eventy.showMessage("Setting verification flag. Please wait", "loading");
  const data = { sampling_point_id: selected.value.id, year: year.value, month: selected.value.month, level: level };
  await Service.flag(data);
  await load();
  Eventy.showHideMessage("Verification flag updated", "success");
};

const onShowHistory = async () => {
  const row = selected.value;
  if (!row?.id) return;
  Eventy.showMessage("Loading history. Please wait", "loading");
  const m = parseInt(row.month);
  const y = parseInt(year.value);
  const fromDt = `${y}-${String(m).padStart(2, "0")}-01 00:00`;
  const nextMonth = m === 12 ? `${y + 1}-01-01 00:00` : `${y}-${String(m + 1).padStart(2, "0")}-01 00:00`;
  logRows.value = await Service.log(row.id, fromDt, nextMonth);
  Eventy.hideMessage();
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
    <observation-log :show="showLog" :rows="logRows" @close="showLog = false" />

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
        </template>
      </DataTable>
    </div>
  </common-layout>
</template>

