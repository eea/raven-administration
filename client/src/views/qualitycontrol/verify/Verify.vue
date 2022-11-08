<script setup>
import Service from "./service";
import { month } from "../../../helpers/utils";
import { computed } from "@vue/reactivity";
import Eventy from "../../../helpers/eventy";
import { tblToCsv, compare, filterList } from "../../../helpers/utils";

import IconLink from "~icons/ph/link-simple-duotone";
import IconCircle from "~icons/ph/circle-duotone";

const year = ref("");
const stationId = ref();

const datasets = ref([]);
const stations = ref([]);
const q = ref("");

const ev = ref({});
const showContextmenu = ref(false);
const selected = ref([]);

const showTable = ref(false);

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
const cls_rowClass = (row) => {
  var classes = "";
  if (row.pre_verified > 0 && row.verified == 0 && row.not_verified == 0) classes = " bg-nord13/20";
  else if (row.not_verified > 0 && row.verified == 0 && row.pre_verified == 0) classes = " bg-nord11/10";
  else if (row.verified == 0) classes = " bg-nord12/10";

  if (compare(selected.value, row)) classes = classes + " selected";
  return classes;
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
const onSetLevel = async (level) => {
  Eventy.showMessage("Setting verification flag. Please wait", "loading");
  const data = { sampling_point_id: selected.value.id, year: year.value, month: selected.value.month, level: level };
  close();
  await Service.flag(data);
  await load();
  Eventy.showHideMessage("Verification flag updated", "success");
};

const close = () => {
  selected.value = {};
  showContextmenu.value = false;
};

const onContextMenu = (row, e) => {
  selected.value = row;
  ev.value = e;
  showContextmenu.value = true;
};

const onDownload = () => {
  tblToCsv("verifyId", "verify");
};
</script>

<template>
  <common-layout>
    <contextmenu :evt="ev" @click-outside="close" :show="showContextmenu">
      <div class="px-2 font-bold">Menu:</div>
      <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="onSetLevel(1)" v-if="selected && (selected.pre_verified > 0 || selected.not_verified > 0)">
        <icon-circle class="text-nord14 text-base self-center" />
        <div class="self-center ml-1">Set to verified</div>
      </div>
      <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="onSetLevel(2)" v-if="selected && (selected.verified > 0 || selected.not_verified > 0)">
        <icon-circle class="text-nord13 text-base self-center" />
        <div class="self-center ml-1">Set to pre verified</div>
      </div>
      <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="onSetLevel(3)" v-if="selected && (selected.pre_verified > 0 || selected.verified > 0)">
        <icon-circle class="text-nord11 text-base self-center" />
        <div class="self-center ml-1">Set to not verified</div>
      </div>
    </contextmenu>

    <tool-bar title="Verify" v-model="q" :show-filter="true" :show-add="false" :show-download="true" @download-click="onDownload" />

    <container>
      <div class="flex gap-3">
        <div>
          <div class="font-bold">Station</div>
          <n-select class="!w-56" v-model="stationId">
            <n-option v-for="opt in stations" :value="opt.id" :label="opt.name" />
          </n-select>
        </div>
        <div>
          <div class="font-bold">Year</div>
          <n-select class="!w-40" v-model="year">
            <n-option v-for="y in cmp_years" :value="y" :label="y" />
          </n-select>
        </div>
        <div>
          <div>&nbsp;</div>
          <button class="n-button" @click="showDatasets" :disabled="false">Show datasets</button>
        </div>
      </div>
      <div class="text-sm flex gap-1 mt-2">
        <icon-link />
        <div><a href="http://dd.eionet.europa.eu/vocabulary/aq/observationverification/view" target="_blank">Read more about verification levels here</a></div>
      </div>
    </container>

    <div class="mt-4" v-if="showTable">
      <table id="verifyId" class="n-table">
        <tr>
          <th>Id</th>
          <th>Station</th>
          <th>Pollutant</th>
          <th>Timestep</th>
          <th>Month</th>
          <th>Verified</th>
          <th>Pre verified</th>
          <th>Not verified</th>
        </tr>
        <tr v-for="row in cmp_datasets" :key="row.month" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}" :class="cls_rowClass(row)">
          <td>{{ row.id }}</td>
          <td>{{ row.station }}</td>
          <td>{{ row.pollutant }}</td>
          <td>{{ row.timestep }}</td>
          <td>{{ month(row.month) }}</td>
          <td>{{ row.verified }}</td>
          <td>{{ row.pre_verified }}</td>
          <td>{{ row.not_verified }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>

<style></style>
