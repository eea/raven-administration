<script setup>
import Service from "./service";
import Eventy from "../../../helpers/eventy";
import { tblToCsv, compare, filterList } from "../../../helpers/utils";

import LAdd from "./LAdd.vue";
import LEdit from "./LEdit.vue";

const zones = ref([]);
const authorities = ref([]);
const types = ref([]);
const q = ref("");
const showEdit = ref(false);
const showAdd = ref(false);
const selected = ref({});
const ev = ref({});
const showContextmenu = ref(false);
const showConfirm = ref(false);

onMounted(async () => {
  authorities.value = await Service.authorities();
  types.value = await Service.types();
  await loadData();
});

const loadData = async () => {
  zones.value = await Service.get();
};

const saveAdd = async (o) => {
  await Service.insert(o);
  await loadData();
  Eventy.showHideMessage("Zone saved", "success", 5000);
  close();
};

const saveEdit = async (o) => {
  await Service.update(o);
  await loadData();
  Eventy.showHideMessage("Zone saved", "success", 5000);
  close();
};

const saveDelete = async (o) => {
  showConfirm.value = false;
  await Service.delete(selected.value);
  await loadData();
  Eventy.showHideMessage("Zone deleted", "success", 5000);
  close();
};

const cmp_zones = computed(() => filterList(q.value, zones.value));

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

const onDelete = () => {
  if (showConfirm.value) selected.value = {};
  showConfirm.value = !showConfirm.value;
  showContextmenu.value = false;
};

const close = () => {
  showEdit.value = false;
  showAdd.value = false;
  selected.value = {};
  showContextmenu.value = false;
  showConfirm.value = false;
};

const onDownload = () => {
  tblToCsv("zonesId", "zones");
};
</script>

<template>
  <common-layout>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete zone?" @close="close" @ok="saveDelete" />
    <contextmenu-crud :show="showContextmenu" :ev="ev" @click-outside="close" @on-edit="onEdit" @onDelete="onDelete" />
    <l-add :show="showAdd" @close="close" @save="saveAdd" :authorities="authorities" :types="types" />
    <l-edit :show="showEdit" @close="close" @save="saveEdit" :zone="selected" :authorities="authorities" :types="types" />

    <tool-bar title="Zones" filter-text="Type to filter zones " v-model="q" @add-click="showAdd = true" @download-click="onDownload" />

    <div>
      <table id="zonesId" class="n-table">
        <tr>
          <th>Id</th>
          <th>Code</th>
          <th>Name</th>
          <th>Year</th>
          <th>Area</th>
          <th>Population</th>
          <th>Population year</th>
          <th>Type</th>
          <th>Authority</th>
          <th class="hidden">Geojson</th>
        </tr>
        <tr v-for="row in cmp_zones" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}" :class="cls_rowClass(row)">
          <td>{{ row.id }}</td>
          <td>{{ row.code }}</td>
          <td>{{ row.name }}</td>
          <td>{{ row.year }}</td>
          <td>{{ row.area }}</td>
          <td>{{ row.population }}</td>
          <td>{{ row.population_year }}</td>
          <td>{{ row.type_label }}</td>
          <td>{{ row.authority_label }}</td>
          <td class="hidden">{{ row.geojson }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>

<style></style>
