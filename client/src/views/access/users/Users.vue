<script setup>
import LAdd from "./LAdd.vue";
import LEdit from "./LEdit.vue";
import Service from "./service";
import { compare } from "../../../helpers/utils";
import Eventy from "../../../helpers/eventy";

const data = ref([]);
const groups = ref([]);
const q = ref("");
const showEdit = ref(false);
const showAdd = ref(false);
const selected = ref({});
const ev = ref({});
const showContextmenu = ref(false);
const showConfirm = ref(false);

onMounted(async () => {
  groups.value = await Service.groups();
  await loadData();
});

const loadData = async () => {
  data.value = await Service.users();
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
  Eventy.showHideMessage("User updated", "success", 5000);
  close();
};

const onSaveAdd = async (o) => {
  await Service.insert(o);
  await loadData();
  Eventy.showHideMessage("Users added", "success", 5000);
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
  Eventy.showHideMessage("User deleted", "success", 5000);
  close();
};

const close = () => {
  showEdit.value = false;
  showAdd.value = false;
  selected.value = {};
  showContextmenu.value = false;
  showConfirm.value = false;
};

const cls_rowClass = (row) => {
  if (compare(selected.value, row)) return " selected";
  return "";
};

const cmp_data = computed(() => {
  return data.value.filter((p) => {
    return !q.value || p.name.toLowerCase().includes(q.value.toLowerCase()) || p.username.toLowerCase().includes(q.value.toLowerCase()) || p.groups.toLowerCase().includes(q.value.toLowerCase());
  });
});
</script>

<template>
  <common-layout>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete the user?" @close="close" @ok="onSaveDelete" />
    <contextmenu-crud :show="showContextmenu" :ev="ev" @click-outside="close" @on-delete="onDelete" @on-edit="onEdit" />
    <l-add :show="showAdd" @close="close" @save="onSaveAdd" :groups="groups" />
    <l-edit :show="showEdit" @close="close" @save="onSaveEdit" :groups="groups" :user="selected" />

    <tool-bar title="Users" :show-column-picker="false" v-model:q="q" @add-click="showAdd = true" :show-download="false" />

    <div>
      <table class="n-table">
        <tr>
          <th>Id</th>
          <th>Name</th>
          <th>Username</th>
          <th>Created by</th>
          <th>Created</th>
          <th>Groups</th>
        </tr>

        <tr v-for="row in cmp_data" :key="row.id" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}" :class="cls_rowClass(row)">
          <!-- <td>{{ row.network }}</td> -->
          <td>{{ row.id }}</td>
          <td>{{ row.name }}</td>
          <td>{{ row.username }}</td>
          <td>{{ row.createdby }}</td>
          <td>{{ row.created }}</td>
          <td>{{ row.group_labels }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>

<style></style>
