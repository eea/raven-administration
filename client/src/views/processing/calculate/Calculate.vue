<script setup>
import LAdd from "./LAdd.vue";
import LEdit from "./LEdit.vue";

import Service from "./service";
import Eventy from "../../../helpers/eventy";
import { tblToCsv, compare, filterList } from "../../../helpers/utils";

const timeseries = ref([]);
const calculations = ref([]);
const q = ref("");
const showEdit = ref(false);
const showAdd = ref(false);
const selected = ref({});
const ev = ref({});
const showContextmenu = ref(false);
const showConfirm = ref(false);

onMounted(async () => {
  await loadData();
});

const loadData = async () => {
  timeseries.value = await Service.timeseries();
  calculations.value = await Service.get();
};

const cmp_calculations = computed(() => filterList(q.value, calculations.value));

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
  Eventy.showHideMessage("Calculation saved", "success", 5000);
  close();
};

const onSaveAdd = async (o) => {
  await Service.insert(o);
  await loadData();
  Eventy.showHideMessage("Calculation saved", "success", 5000);
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
  Eventy.showHideMessage("Calculation deleted", "success", 5000);
  close();
};

const onDownload = () => {
  tblToCsv("calculationsId", "calculations");
};
</script>

<template>
  <common-layout>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete calculation?" @close="close" @ok="onSaveDelete" />
    <contextmenu-crud :show="showContextmenu" :ev="ev" @click-outside="close" @on-edit="onEdit" @onDelete="onDelete" />

    <l-add :show="showAdd" @close="close" @save="onSaveAdd" :timeseries="timeseries" />
    <l-edit :show="showEdit" @close="close" @save="onSaveEdit" :timeseries="timeseries" :calculation="selected" />

    <tool-bar title="Calculations" filter-text="Type to filter" v-model="q" @add-click="showAdd = true" @download-click="onDownload" />

    <div>
      <table id="calculationsId" class="n-table">
        <tr>
          <th>Station</th>
          <th>Primary</th>
          <th>Operator</th>
          <th>Secondary</th>
          <th>Result</th>
        </tr>
        <tr v-for="row in cmp_calculations" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}" :class="cls_rowClass(row)">
          <td>{{ row.station }}</td>
          <td>{{ row.primary_pollutant }}</td>
          <td>{{ row.operator }}</td>
          <td>{{ row.secondary_pollutant }}</td>
          <td>{{ row.result_pollutant }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>

<style></style>
