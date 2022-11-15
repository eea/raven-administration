<script setup>
import Eventy from "../../helpers/eventy";
import { tblToCsv, filterList } from "../../helpers/utils";
import ToolBar from "../ToolBar.vue";
import Crud from "./Crud.vue";

const props = defineProps({
  name: String,
  options: Object,
  service: Object,
  crudComponent: {
    type: [String, Object],
    default: Crud
  }
});

const q = ref("");
const data = ref([]);

const showEdit = ref(false);
const showAdd = ref(false);
const showColumnPicker = ref(false);

const selected = ref({});
const ev = ref({});
const showContextmenu = ref(false);
const showConfirm = ref(false);

const id = "id" + Math.random().toString(16).slice(2);

onMounted(async () => {
  await loadData();
});

const loadData = async () => {
  data.value = await props.service.get();
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

const onDownload = () => {
  tblToCsv(id, props.name);
};

const onColumnPicker = (e) => {
  ev.value = e;
  showColumnPicker.value = true;
};

const saveEdit = async (o) => {
  for (const key in o) {
    o[key] = o[key]?.length == 0 ? null : o[key];
  }
  await props.service.update(o);
  await loadData();
  Eventy.showHideMessage(`${props.name} saved`, "success", 5000);
  close();
};

const saveAdd = async (o) => {
  for (const key in o) {
    o[key] = o[key]?.length == 0 ? null : o[key];
  }
  await props.service.insert(o);
  await loadData();
  Eventy.showHideMessage(`${props.name} saved`, "success", 5000);
  close();
};

const saveDelete = async (o) => {
  showConfirm.value = false;
  await props.service.delete(selected.value);
  await loadData();
  Eventy.showHideMessage(`${props.name} deleted`, "success", 5000);
  close();
};

const close = () => {
  showEdit.value = false;
  showAdd.value = false;
  showColumnPicker.value = false;
  showContextmenu.value = false;
  showConfirm.value = false;
  selected.value = {};
  ev.value = {};
};

const cmp_data = computed(() => filterList(q.value, data.value));
</script>

<template>
  <common-layout>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete?" @close="close" @ok="saveDelete" />
    <contextmenu-crud :show="showContextmenu" :ev="ev" @click-outside="close" @on-edit="onEdit" @onDelete="onDelete" />
    <column-picker :show="showColumnPicker" :ev="ev" :properties="options.properties" @click-outside="close" />

    <component :is="crudComponent" :is-edit="false" :show="showAdd" :options="options" @close="close" @save="saveAdd" />
    <component :is="crudComponent" :is-edit="true" :show="showEdit" :options="options" :selected-value="selected" @close="close" @save="saveEdit" />

    <tool-bar :title="name" v-model:q="q" @add-click="showAdd = true" @download-click="onDownload" @column-picker-click="onColumnPicker" />

    <grid :id="id" v-model:selected="selected" v-model:ev="ev" :properties="options.properties" :values="cmp_data" @on-right-click="showContextmenu = true" />
  </common-layout>
</template>

<style></style>
