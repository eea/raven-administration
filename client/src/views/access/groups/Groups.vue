<script setup>
import LAdd from "./LAdd.vue";
import LEdit from "./LEdit.vue";
import Service from "./service";
import { compare } from "../../../helpers/utils";
import Eventy from "../../../helpers/eventy";

const networks = ref([]);
const data = ref([]);
const q = ref("");
const showEdit = ref(false);
const showAdd = ref(false);
const selected = ref({});
const ev = ref({});
const showContextmenu = ref(false);
const showConfirm = ref(false);

onMounted(async () => {
  networks.value = await Service.networks();
  await loadData();
});

const loadData = async () => {
  data.value = await Service.groups();
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
  Eventy.showHideMessage("Group updated", "success", 5000);
  close();
};

const onSaveAdd = async (o) => {
  await Service.insert(o);
  await loadData();
  Eventy.showHideMessage("Group added", "success", 5000);
  close();
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
  Eventy.showHideMessage("Group deleted", "success", 5000);
  close();
};

const close = () => {
  showEdit.value = false;
  showAdd.value = false;
  selected.value = {};
  showContextmenu.value = false;
  showConfirm.value = false;
};

const cmp_data = computed(() => {
  return data.value.filter((p) => {
    return !q.value || p.name.toLowerCase().includes(q.value.toLowerCase());
  });
});

const cls_rowClass = (row) => {
  if (compare(selected.value, row)) return " selected";
  return "";
};

const cls_usedby = (row) => {
  if (row.user_count == 0) return "text-nord11";
  return "text-nord10";
};
</script>

<template>
  <common-layout>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete the group?" @close="close" @ok="onSaveDelete" />
    <contextmenu-crud :show="showContextmenu" :ev="ev" @click-outside="close" @on-delete="onDelete" @on-edit="onEdit" />
    <l-add :show="showAdd" @close="close" @save="onSaveAdd" :networks="networks" />
    <l-edit :show="showEdit" @close="close" @save="onSaveEdit" :networks="networks" :group="selected" />

    <tool-bar title="Groups" :show-column-picker="false" v-model:q="q" @add-click="showAdd = true" :show-download="false" />

    <div>
      <table class="n-table">
        <tr>
          <th>Id</th>
          <th>Name</th>
          <th>Management</th>
          <th>Data</th>
          <th>EEA dataflow</th>
          <th>Processing</th>
          <th>Quality control</th>
          <th>Users</th>
          <th>All networks</th>
          <th>Referenced by</th>
        </tr>

        <tr v-for="row in cmp_data" :key="row.id" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}" :class="cls_rowClass(row)">
          <td>{{ row.id }}</td>
          <td>{{ row.name }}</td>
          <td><n-checkbox class="align-middle" v-model="row.management" :disabled="true" /></td>
          <td><n-checkbox class="align-middle" v-model="row.data" :disabled="true" /></td>
          <td><n-checkbox class="align-middle" v-model="row.exporting" :disabled="true" /></td>
          <td><n-checkbox class="align-middle" v-model="row.processing" :disabled="true" /></td>
          <td><n-checkbox class="align-middle" v-model="row.qualitycontrol" :disabled="true" /></td>
          <td><n-checkbox class="align-middle" v-model="row.users" :disabled="true" /></td>
          <td><n-checkbox class="align-middle" v-model="row.allnetworks" :disabled="true" /></td>
          <td>
            <span class="font-bold mr-1" :class="cls_usedby(row)">{{ row.user_count }}</span>
            user(s)
          </td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>

<style></style>
