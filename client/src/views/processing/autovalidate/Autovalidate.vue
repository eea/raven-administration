<script setup>
import LAdd from "./LAdd.vue";
import LEdit from "./LEdit.vue";

import Service from "./service";
import Eventy from "../../../helpers/eventy";
import { tblToCsv, compare } from "../../../helpers/utils";

const pollutants = ref([]);
const autovalidations = ref([]);
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
  pollutants.value = await Service.pollutants();
  autovalidations.value = await Service.get();
};

const cmp_autovalidations = computed(() => {
  var t = autovalidations.value.filter((p) => {
    return !q.value || p.pollutant.toLowerCase().includes(q.value.toLowerCase()) || p.min.toLowerCase().includes(q.value.toLowerCase()) || p.max.toLowerCase().includes(q.value.toLowerCase()) || p.repeat.toLowerCase().includes(q.value.toLowerCase());
  });
  return t;
});

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
  autovalidations.value = await Service.get();
  Eventy.showHideMessage("Validation saved", "success", 5000);
  close();
};

const onSaveAdd = async (o) => {
  await Service.insert(o);
  autovalidations.value = await Service.get();
  Eventy.showHideMessage("Validation saved", "success", 5000);
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
  Eventy.showHideMessage("Validation deleted", "success", 5000);
  close();
};

const onDownload = () => {
  tblToCsv("autovalidationsId", "autovalidations");
};
</script>

<template>
  <common-layout>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete validation?" @close="close" @ok="onSaveDelete" />
    <contextmenu-crud :show="showContextmenu" :ev="ev" @click-outside="close" @on-edit="onEdit" @onDelete="onDelete" />

    <l-add :show="showAdd" @close="close" @save="onSaveAdd" :pollutants="pollutants" />
    <l-edit :show="showEdit" @close="close" @save="onSaveEdit" :pollutants="pollutants" :validation="selected" />

    <tool-bar title="Auto validate" filter-text="Type to filter " v-model="q" @add-click="showAdd = true" @download-click="onDownload" />

    <div>
      <table id="autovalidationsId" class="n-table">
        <tr>
          <th>Pollutant</th>
          <th>Minimum</th>
          <th>Maximum</th>
          <th>Repeat</th>
        </tr>
        <tr v-for="row in cmp_autovalidations" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}" :class="cls_rowClass(row)">
          <td>{{ row.pollutant }}</td>
          <td>{{ row.min }}</td>
          <td>{{ row.max }}</td>
          <td>{{ row.rep }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>

<style></style>
