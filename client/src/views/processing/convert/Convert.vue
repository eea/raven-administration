<script setup>
import LAdd from "./LAdd.vue";
import LEdit from "./LEdit.vue";

import Service from "./service";
import Eventy from "../../../helpers/eventy";
import { tblToCsv, compare, filterList } from "../../../helpers/utils";

const units = ref([]);
const timeseries = ref([]);
const convertions = ref([]);
const q = ref("");
const showEdit = ref(false);
const showAdd = ref(false);
const selected = ref({});
const ev = ref({});
const showContextmenu = ref(false);
const showConfirm = ref(false);

onMounted(async () => {
  units.value = await Service.units();
  timeseries.value = await Service.timeseries();
  await loadData();
});

const loadData = async () => {
  convertions.value = await Service.get();
};

const cmp_convertions = computed(() => filterList(q.value, convertions.value));

const cls_rowClass = (row) => {
  if (compare(selected.value, row)) return " selected";
  return "";
};

const onContextMenu = (row, e) => {
  selected.value = row;
  ev.value = e;
  showContextmenu.value = true;
};

const onEdit = () => {
  if (showEdit.value) selected.value = {};
  showEdit.value = !showEdit.value;
  showContextmenu.value = false;
};

const onSaveEdit = async (o) => {
  await Service.update(o);
  await loadData();
  Eventy.showHideMessage("Convertion saved", "success", 5000);
  close();
};

const onSaveAdd = async (o) => {
  await Service.insert(o);
  await loadData();
  Eventy.showHideMessage("Convertion saved", "success", 5000);
  close();
};

const close = () => {
  showEdit.value = false;
  showAdd.value = false;
  selected.value = {};
  showContextmenu.value = false;
  showConfirm.value = false;
};

const onDelete = () => {
  if (showConfirm.value) selected.value = {};
  showConfirm.value = !showConfirm.value;
  showContextmenu.value = false;
};

const onSaveDelete = async (o) => {
  showConfirm.value = false;
  await Service.delete(selected.value);
  await loadData();
  Eventy.showHideMessage("Convertion deleted", "success", 5000);
  close();
};

const onDownload = () => {
  tblToCsv("convertionsId", "convertions");
};
</script>

<template>
  <common-layout>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete convertion?" @close="close" @ok="onSaveDelete" />
    <contextmenu-crud :show="showContextmenu" :ev="ev" @click-outside="close" @on-edit="onEdit" @onDelete="onDelete" />

    <l-add :show="showAdd" @close="close" @save="onSaveAdd" :timeseries="timeseries" :units="units" />
    <l-edit :show="showEdit" @close="close" @save="onSaveEdit" :timeseries="timeseries" :units="units" :convertion="selected" />

    <tool-bar title="Convert" :show-column-picker="false" v-model:q="q" @add-click="showAdd = true" @download-click="onDownload" />

    <div>
      <table id="convertionsId" class="n-table">
        <tr>
          <th>Station</th>
          <th>Pollutant</th>
          <th>Timestep</th>
          <th>Source</th>
          <th>Target</th>
          <th>Factor</th>
        </tr>
        <tr v-for="row in cmp_convertions" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}" :class="cls_rowClass(row)">
          <td>{{ row.station }}</td>
          <td>{{ row.pollutant }}</td>
          <td>{{ row.timestep }}</td>
          <td>{{ row.source }}</td>
          <td>{{ row.target }}</td>
          <td>{{ row.factor }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>

<style></style>
