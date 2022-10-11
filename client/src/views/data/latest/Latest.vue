<script setup>
import IconValidate from "~icons/material-symbols/fact-check";
import IconPlot from "~icons/material-symbols/bar-chart";
import IconScale from "~icons/uil/process";

import { useRouter } from "vue-router";

import { format, sub, add } from "date-fns";
import Service from "./service";
import { tblToCsv, compare } from "../../../helpers/utils";

const q = ref("");
const data = ref([]);
const ev = ref({});
const showContextmenu = ref(false);
const selected = ref({});

const router = useRouter();

onMounted(async () => {
  await loadData();
});

const loadData = async () => {
  data.value = await Service.get();
};

const cmp_data = computed(() => {
  return data.value.filter((p) => {
    return !q.value || p.station.toLowerCase().includes(q.value.toLowerCase()) || p.pollutant.toLowerCase().includes(q.value.toLowerCase()) || p.timestep.toLowerCase().includes(q.value.toLowerCase());
  });
});

const close = () => {
  showContextmenu.value = false;
  selected.value = {};
};

const cls_rowClass = (row) => {
  var classes = "";
  if (row.validation_flag < 1) classes = " bg-nord11/10";
  if (compare(selected.value, row)) classes = classes + " selected";
  // if (row.pollutant == "O3") return "bg-nord14/20"
  // if (row.pollutant == "NO") return "bg-nord13/20"
  return classes;
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

    <tool-bar title="Latest data" filter-text="Type to filter data" :show-add="false" v-model="q" @download-click="onDownload" />

    <div>
      <table id="latestId" class="n-table">
        <tr>
          <!-- <th>Network</th> -->
          <th>Station</th>
          <th>Pollutant</th>
          <th>Timestep</th>
          <th>First date</th>
          <th>Latest date</th>
          <th>Value</th>
          <th>Validation</th>
          <th>Verification</th>
          <th>Unit</th>
        </tr>
        <tr v-for="row in cmp_data" :class="cls_rowClass(row)" :key="row.id" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}">
          <!-- <td>{{ row.network }}</td> -->
          <td>{{ row.station }}</td>
          <td>{{ row.pollutant }}</td>
          <td>{{ row.timestep }}</td>
          <td>{{ row.from_time }}</td>
          <td class="font-bold">{{ row.to_time }}</td>
          <td>{{ row.value }}</td>
          <td>{{ row.validation_flag }}</td>
          <td>{{ row.verification_flag }}</td>
          <td>{{ row.unit }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>
