<script setup>
import LEdit from "./LEdit.vue";
import LAdd from "./LAdd.vue";

import IconEdit from "~icons/ic/baseline-edit";
import IconDelete from "~icons/ic/baseline-delete";

import Service from "./service";
import Eventy from "../../../helpers/eventy";
import { tblToCsv, compare } from "../../../helpers/utils";

const authoritites = ref([]);
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
  authoritites.value = await Service.get();
};

const cmp_authoritites = computed(() => {
  var t = authoritites.value.filter((p) => {
    return !q.value || p.id.toLowerCase().includes(q.value.toLowerCase()) || p.name.toLowerCase().includes(q.value.toLowerCase()) || p.organisation.toLowerCase().includes(q.value.toLowerCase()) || p.locator.toLowerCase().includes(q.value.toLowerCase());
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

const saveEdit = async (o) => {
  await Service.update(o);
  await loadData();
  Eventy.showHideMessage("Authority saved", "success", 5000);
  close();
};

const saveAdd = async (o) => {
  await Service.insert(o);
  await loadData();
  Eventy.showHideMessage("Authority saved", "success", 5000);
  close();
};

const saveDelete = async () => {
  showConfirm.value = false;
  await Service.delete(selected.value);
  await loadData();
  Eventy.showHideMessage("Authority deleted", "success", 5000);
  close();
};

const onDownload = () => {
  tblToCsv("authoritiesId", "authorities");
};
</script>
<template>
  <common-layout>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete authority?" @close="close" @ok="saveDelete" />

    <contextmenu :evt="ev" @click-outside="close" :show="showContextmenu">
      <div class="px-2 font-bold">Menu:</div>
      <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="onEdit()">
        <icon-edit class="text-nord15 text-sm self-center" />
        <div class="self-center ml-1">Edit</div>
      </div>
      <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="onDelete()">
        <icon-delete class="text-nord11 text-sm self-center" />
        <div class="self-center ml-1">Delete</div>
      </div>
    </contextmenu>

    <l-add :show="showAdd" @close="close" @save="saveAdd" />
    <l-edit :show="showEdit" :authority="selected" @close="close" @save="saveEdit" />

    <tool-bar title="Authorities" filter-text="Type to filter authorities " v-model="q" @add-click="showAdd = true" @download-click="onDownload" />

    <div>
      <table id="authoritiesId" class="n-table">
        <tr>
          <th>Id</th>
          <th>Name</th>
          <th>Organisation</th>
          <th>Locator</th>
          <th>Postcode</th>
          <th>Email</th>
          <th>Address</th>
          <th>Phone</th>
          <th>Website</th>
        </tr>
        <tr v-for="row in cmp_authoritites" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}" :class="cls_rowClass(row)">
          <td>{{ row.id }}</td>
          <td>{{ row.name }}</td>
          <td>{{ row.organisation }}</td>
          <td>{{ row.locator }}</td>
          <td>{{ row.postcode }}</td>
          <td>{{ row.email }}</td>
          <td>{{ row.address }}</td>
          <td>{{ row.phone }}</td>
          <td>{{ row.website }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>
