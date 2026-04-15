<script setup>
import IconValidate from "~icons/material-symbols/fact-check";
import IconPlot from "~icons/material-symbols/bar-chart";
import IconScale from "~icons/uil/process";
import IconHeart from "~icons/mdi/heart";
import IconHeartOutline from "~icons/mdi/heart-outline";
import CircleHover from "../../../components/CircleHover.vue";
import { ref as vref } from "vue";

const PREF_KEY = "raven_default_view";
const isDefault = vref(localStorage.getItem(PREF_KEY) === "Latest" || !localStorage.getItem(PREF_KEY));
const toggleDefault = () => {
  const val = "Latest";
  localStorage.setItem(PREF_KEY, val);
  isDefault.value = true;
};

import { useRouter } from "vue-router";
import { ref, computed, onMounted, watch } from "vue";

import { format, sub, add } from "date-fns";
import Service from "./service";
import { filterList, downloadCsv } from "../../../helpers/utils";
import { datetimeCellRenderer, granularityFromTimestep } from "../../../helpers/datetimeHighlight";

import CommonLayout from "../../../components/CommonLayout.vue";
import ToolBar from "../../../components/ToolBar.vue";
import DataTable from "../../../components/DataTable.vue";

const q = ref("");
const data = ref([]);
const selected = ref({});
const aqi_type = ref(localStorage.getItem("aqi_type") || "eea");
const showAqiToggle = ref(false);

const router = useRouter();

const columns = ref([]);

const createColumns = () => {
  columns.value = [
    { field: "station", headerName: "Station", flex: 1 },
    { field: "pollutant", headerName: "Pollutant/Meteo", flex: 1 },
    { field: "timestep", headerName: "Timestep", flex: 0.8 },
    { field: "from_time", headerName: "First date", flex: 1, cellRenderer: datetimeCellRenderer((row) => granularityFromTimestep(row?.timestep)) },
    {
      field: "to_time",
      headerName: "Latest date",
      flex: 1,
      cellRenderer: datetimeCellRenderer((row) => granularityFromTimestep(row?.timestep)),
      cellStyle: (params) => {
        if (params.data.status == 1) return { color: "#d08770" };
        if (params.data.status == 2) return { color: "#bf616a" };
        return null;
      }
    },
    {
      field: "aqi",
      headerName: "AQI",
      flex: 0.7,
      cellStyle: { display: "flex", alignItems: "center", justifyContent: "center" },
      cellRenderer: (params) => {
        const level = aqi_type.value === "eea" ? params.data.eea_aqi_level : params.data.local_aqi_level;
        if (!level || level <= 0) return "";

        const color = aqi_type.value === "eea" ? params.data.eea_aqi_color : params.data.local_aqi_color;
        const desc = aqi_type.value === "eea" ? params.data.eea_aqi_desc : params.data.local_aqi_desc;

        return `<div class="w-4 h-4 rounded-full" title="${desc}" style="background-color: ${color}BB; border: 1px solid ${color};"></div>`;
      }
    },
    { field: "value", headerName: "Value", flex: 1 },
    { field: "observationvalidity_id", headerName: "Validity", flex: 1 },
    { field: "observationverification_id", headerName: "Verification", flex: 1 },
    { field: "unit", headerName: "Unit", flex: 0.7 },
    { field: "id", headerName: "SPO", flex: 1 }
  ];
};

onMounted(async () => {
  createColumns();
  await loadData();
  // check if all data.local_aqi is null, if so, set aqi_type to eea
  if (data.value.every((row) => row.local_aqi_level === null)) {
    aqi_type.value = "eea";
    showAqiToggle.value = false;
  } else {
    showAqiToggle.value = true;
  }
});

watch(aqi_type, (val) => {
  localStorage.setItem("aqi_type", val);
  createColumns(); // Recreate columns to update AQI rendering
});

const loadData = async () => {
  const result = await Service.get();
  if (result) data.value = result;
};

const cmp_data = computed(() => filterList(q.value, data.value));

const getRowStyle = (params) => {
  const row = params.data;
  if (!row) return null;

  if (row.observationvalidity_id && row.observationvalidity_id !== 1) {
    return { backgroundColor: "#bf616a1a" }; // bg-nord11/10
  }

  return null;
};

const onContextMenuAction = ({ action, data }) => {
  if (data?.row) {
    selected.value = data.row;
  }

  if (action === "Historical" || action === "Validate" || action === "Scale") {
    onGoto(action);
  }
};

const onDownload = () => {
  downloadCsv(cmp_data.value, columns.value, "latest_data");
};

const onGoto = (name) => {
  const { id, to_time } = selected.value;
  var tt = format(add(new Date(to_time), { hours: 1 }), "yyy-MM-dd HH:00");
  var ft = format(sub(new Date(tt), { days: 14 }), "yyy-MM-dd HH:00");
  if (name == "Scale") router.push({ name: name, query: { id: id } });
  else router.push({ name: name, query: { ids: id, from: ft, to: tt } });
};
</script>

<template>
  <CommonLayout>
    <ToolBar title="Latest data" :show-column-picker="false" :show-add="false" v-model:q="q" @download-click="onDownload">
      <CircleHover class="ml-1 self-center" @click="toggleDefault" :title="isDefault ? 'Opens here after login' : 'Open here after login'">
        <icon-heart v-if="isDefault" class="text-nord10 text-sm self-center" />
        <icon-heart-outline v-else class="text-nord3 text-sm self-center" />
      </CircleHover>
      <div class="self-center flex gap-2 ml-10" v-if="showAqiToggle">
        <div class="flex items-center gap-1">
          <input v-model="aqi_type" type="radio" value="eea" id="aqi_eea" class="cursor-pointer accent-[#74992e]" />
          <label for="aqi_eea" class="cursor-pointer">EEA AQI</label>
        </div>
        <div class="flex items-center gap-1">
          <input v-model="aqi_type" type="radio" value="local" id="aqi_local" class="cursor-pointer accent-[#74992e]" />
          <label for="aqi_local" class="cursor-pointer">Local AQI</label>
        </div>
      </div>
    </ToolBar>

    <div class="flex-1 min-h-0">
      <DataTable :data="cmp_data" :columns="columns" :get-row-style="getRowStyle" :filter="true" :floating-filter="false" :show-copy-options="true" @context-menu-action="onContextMenuAction">
        <template #context-menu-items="{ handleAction }">
          <div class="px-2 font-bold text-base text-nord3">Menu:</div>
          <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('Historical')">
            <icon-plot class="text-nord15 self-center" />
            <div class="self-center ml-1">Plot data</div>
          </div>
          <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('Validate')">
            <icon-validate class="text-nord12 self-center" />
            <div class="self-center ml-1">Validate data</div>
          </div>
          <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('Scale')">
            <icon-scale class="text-nord10 self-center" />
            <div class="self-center ml-1">Scale data</div>
          </div>
        </template>
      </DataTable>
    </div>
  </CommonLayout>
</template>
