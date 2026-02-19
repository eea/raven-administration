<script setup>
import { ref, computed, onMounted, shallowRef } from "vue";
import CommonLayout from "../../../components/CommonLayout.vue";
import ToolBar from "../../../components/ToolBar.vue";
import Container from "../../../components/Container.vue";
import DataTable from "../../../components/DataTable.vue";
import CMenu from "../../../components/CMenu.vue";

import Service from "./service";
import { month, downloadCsv } from "../../../helpers/utils";
import Eventy from "../../../helpers/eventy";
import { filterList } from "../../../helpers/utils";

import IconLink from "~icons/ph/link-simple-duotone";
import IconCircle from "~icons/ph/circle-duotone";

const year = ref("");
const stationId = ref();

const datasets = ref([]);
const stations = ref([]);
const q = ref("");

const menuRef = ref(null);
const selected = ref({});

const showTable = ref(false);

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
const onMenuClick = async ({ action }) => {
  if (action === "verified") {
    await onSetLevel(1);
  } else if (action === "pre-verified") {
    await onSetLevel(2);
  } else if (action === "not-verified") {
    await onSetLevel(3);
  }
};

const onSetLevel = async (level) => {
  Eventy.showMessage("Setting verification flag. Please wait", "loading");
  const data = { sampling_point_id: selected.value.id, year: year.value, month: selected.value.month, level: level };
  await Service.flag(data);
  await load();
  Eventy.showHideMessage("Verification flag updated", "success");
};

const onContextMenu = (row, e) => {
  selected.value = row;
  menuRef.value?.showMenu(row, e);
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
    <c-menu ref="menuRef" @on-click="onMenuClick">
      <template #default="{ handleAction }">
        <div class="px-2 font-bold">Menu:</div>
        <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="handleAction('verified')" v-if="selected && (selected.pre_verified > 0 || selected.not_verified > 0)">
          <icon-circle class="text-nord14 text-base self-center" />
          <div class="self-center ml-1">Set to verified</div>
        </div>
        <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="handleAction('pre-verified')" v-if="selected && (selected.verified > 0 || selected.not_verified > 0)">
          <icon-circle class="text-nord13 text-base self-center" />
          <div class="self-center ml-1">Set to pre verified</div>
        </div>
        <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="handleAction('not-verified')" v-if="selected && (selected.pre_verified > 0 || selected.verified > 0)">
          <icon-circle class="text-nord11 text-base self-center" />
          <div class="self-center ml-1">Set to not verified</div>
        </div>
      </template>
    </c-menu>

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

    <div class="mt-4 h-[calc(100vh-300px)]" v-if="showTable">
      <DataTable :data="cmp_datasets" :columns="columns" :get-row-style="getRowStyle" :filter="false" :floating-filter="false" @on-right-click="onContextMenu" />
    </div>
  </common-layout>
</template>
