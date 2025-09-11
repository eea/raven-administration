<script setup>
import IconValidate from "~icons/material-symbols/fact-check";
import IconPlot from "~icons/material-symbols/bar-chart";
import IconScale from "~icons/uil/process";

import { useRouter } from "vue-router";
import { ref, computed, onMounted, watch } from "vue";

import { format, sub, add } from "date-fns";
import Service from "./service";
import { tblToCsv, compare, filterList } from "../../../helpers/utils";

const q = ref("");
const data = ref([]);
const ev = ref({});
const showContextmenu = ref(false);
const selected = ref({});
const aqi_type = ref(localStorage.getItem("aqi_type") || "eea");
const showAqiToggle = ref(false);

const router = useRouter();

onMounted(async () => {
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
});

const loadData = async () => {
  data.value = await Service.get();
};

const cmp_data = computed(() => filterList(q.value, data.value));

const close = () => {
  showContextmenu.value = false;
  selected.value = {};
};

const cls_rowClass = (row) => {
  var classes = "";
  if (row.validation_flag < 1) classes = " bg-nord11/10";
  if (compare(selected.value, row)) classes = classes + " selected";
  return classes;
};

const cls_cellClass = (row) => {
  if (row.status == 1) return "text-nord12";
  if (row.status == 2) return "text-nord11";
  return "";
};

const onDownload = () => {
  tblToCsv("latestId", "latest_data");
};

const onGoto = (name) => {
  const { id, to_time } = selected.value;
  var tt = format(add(new Date(to_time), { hours: 1 }), "yyy-MM-dd HH:00");
  var ft = format(sub(new Date(tt), { days: 14 }), "yyy-MM-dd HH:00");
  if (name == "Scale") router.push({ name: name, query: { id: id } });
  else router.push({ name: name, query: { ids: id, from: ft, to: tt } });
};

const onContextMenu = (row, e) => {
  selected.value = row;
  ev.value = e;
  showContextmenu.value = true;
};
</script>

<template>
  <common-layout>
    <contextmenu :evt="ev" @click-outside="close" :show="showContextmenu">
      <div class="px-2 font-bold">Menu:</div>
      <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="onGoto('Historical')">
        <icon-plot class="text-nord15 self-center" />
        <div class="self-center ml-1">Plot data</div>
      </div>
      <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="onGoto('Validate')">
        <icon-validate class="text-nord12 self-center" />
        <div class="self-center ml-1">Validate data</div>
      </div>
      <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="onGoto('Scale')">
        <icon-scale class="text-nord10 self-center" />
        <div class="self-center ml-1">Scale data</div>
      </div>
    </contextmenu>

    <tool-bar title="Latest data" :show-column-picker="false" :show-add="false" v-model:q="q" @download-click="onDownload">
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
    </tool-bar>

    <div>
      <table id="latestId" class="n-table">
        <tr>
          <!-- <th>Network</th> -->
          <th>Station</th>
          <th>Pollutant/Meteo</th>
          <th>Timestep</th>
          <th>First date</th>
          <th>Latest date</th>
          <th>AQI</th>
          <th>Value</th>
          <th>Validation</th>
          <th>Verification</th>
          <th>Unit</th>
          <th>SPO</th>
        </tr>
        <tr v-for="row in cmp_data" :class="cls_rowClass(row)" :key="row.id" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}">
          <!-- <td>{{ row.network }}</td> -->
          <td>{{ row.station }}</td>
          <td>{{ row.pollutant }}</td>
          <td>{{ row.timestep }}</td>
          <td>{{ row.from_time }}</td>
          <td :class="cls_cellClass(row)">{{ row.to_time }}</td>
          <td v-if="aqi_type === 'eea'">
            <div v-if="row.eea_aqi_level > 0" class="w-4 h-4 rounded-full flex items-center justify-center" v-tooltip="row.eea_aqi_desc" :style="{ backgroundColor: row.eea_aqi_color + 'BB', borderColor: row.eea_aqi_color, borderStyle: 'solid', borderWidth: '1px' }"></div>
          </td>
          <td v-if="aqi_type === 'local'">
            <div v-if="row.local_aqi_level > 0" class="w-4 h-4 rounded-full flex items-center justify-center" v-tooltip="row.local_aqi_desc" :style="{ backgroundColor: row.local_aqi_color + 'BB', borderColor: row.local_aqi_color, borderStyle: 'solid', borderWidth: '1px' }"></div>
          </td>
          <td>{{ row.value }}</td>
          <td>{{ row.validation_flag }}</td>
          <td>{{ row.verification_flag }}</td>
          <td>{{ row.unit }}</td>
          <td>{{ row.id }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>
