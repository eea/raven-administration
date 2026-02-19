<script setup>
import IconValidate from "~icons/material-symbols/fact-check";
import IconPlot from "~icons/material-symbols/bar-chart";
import IconScale from "~icons/uil/process";
import IconCopy from "~icons/ic/twotone-content-copy";

import { useRouter } from "vue-router";
import { ref, computed, onMounted, watch } from "vue";

import { format, sub, add } from "date-fns";
import Service from "./service";
import { compare, filterList, downloadCsv } from "../../../helpers/utils";

import CommonLayout from "../../../components/CommonLayout.vue";
import ToolBar from "../../../components/ToolBar.vue";
import DataTable from "../../../components/DataTable.vue";
import CMenu from "../../../components/CMenu.vue";

const q = ref("");
const data = ref([]);
const contextMenuRef = ref(null);
const selected = ref({});
const currentGridEvent = ref(null);
const aqi_type = ref(localStorage.getItem("aqi_type") || "eea");
const showAqiToggle = ref(false);

const router = useRouter();

const columns = ref([]);

const createColumns = () => {
  columns.value = [
    { field: "station", headerName: "Station", flex: 1 },
    { field: "pollutant", headerName: "Pollutant/Meteo", flex: 1 },
    { field: "timestep", headerName: "Timestep", flex: 0.8 },
    { field: "from_time", headerName: "First date", flex: 1 },
    {
      field: "to_time",
      headerName: "Latest date",
      flex: 1,
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
    { field: "validation_flag", headerName: "Validation", flex: 1 },
    { field: "verification_flag", headerName: "Verification", flex: 1 },
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
  data.value = await Service.get();
};

const cmp_data = computed(() => filterList(q.value, data.value));

const getRowStyle = (params) => {
  const row = params.data;
  let style = {};

  if (row.validation_flag < 1) {
    style.backgroundColor = "#bf616a1a"; // bg-nord11/10
  }

  if (compare(selected.value, row)) {
    style.backgroundColor = "#81a1c133"; // selected highlight
  }

  return style;
};

const onRowClick = (row) => {
  selected.value = {};
};

const onContextMenu = (row, e, gridEvent) => {
  currentGridEvent.value = gridEvent;
  contextMenuRef.value.showMenu(row, e);
};

const onMenuClick = ({ action, data }) => {
  selected.value = data;

  if (action === "copy-cell") {
    copyToClipboard();
  } else {
    onGoto(action);
  }
};

const copyToClipboard = async () => {
  if (!currentGridEvent.value?.value) return;

  try {
    const cellValue = String(currentGridEvent.value.value);
    await navigator.clipboard.writeText(cellValue);
    console.log("Copied cell value to clipboard:", cellValue);
  } catch (err) {
    console.error("Failed to copy to clipboard:", err);
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
    <CMenu ref="contextMenuRef" @on-click="onMenuClick" v-slot="{ handleAction }">
      <div class="px-2 font-bold">Menu:</div>
      <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="handleAction('Historical')">
        <icon-plot class="text-nord15 self-center" />
        <div class="self-center ml-1">Plot data</div>
      </div>
      <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="handleAction('Validate')">
        <icon-validate class="text-nord12 self-center" />
        <div class="self-center ml-1">Validate data</div>
      </div>
      <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="handleAction('Scale')">
        <icon-scale class="text-nord10 self-center" />
        <div class="self-center ml-1">Scale data</div>
      </div>
      <div class="border-t border-nord4 pt-1">
        <div class="pl-2 pr-4 py-1 flex cursor-pointer hover:bg-gray-100" @click="handleAction('copy-cell')">
          <icon-copy class="text-nord8 text-sm self-center" />
          <div class="self-center ml-1">Copy cell value</div>
        </div>
      </div>
    </CMenu>

    <ToolBar title="Latest data" :show-column-picker="false" :show-add="false" v-model:q="q" @download-click="onDownload">
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
      <DataTable :data="cmp_data" :columns="columns" :get-row-style="getRowStyle" :filter="true" :floating-filter="false" @on-right-click="onContextMenu" @cell-clicked="onRowClick" />
    </div>
  </CommonLayout>
</template>
