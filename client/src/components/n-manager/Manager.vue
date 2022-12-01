<script setup>
import Eventy from "../../helpers/eventy";
import { filterList } from "../../helpers/utils";
import ToolBar from "../ToolBar.vue";
import Crud from "./Crud.vue";

const props = defineProps({
  name: String,
  options: Object,
  service: Object,
  crudComponent: {
    type: [String, Object],
    default: Crud
  },
  showUploadButton: {
    type: Boolean,
    default: true
  },
  showDownloadButton: {
    type: Boolean,
    default: true
  },
  showAddButton: {
    type: Boolean,
    default: true
  }
});

const q = ref("");
const data = ref([]);

const showEdit = ref(false);
const showAdd = ref(false);
const showUpload = ref(false);
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

const onDownload = async () => {
  await props.service.download();
};

const onUpload = (e) => {
  ev.value = e;
  showUpload.value = true;
};

const onUploadClick = async (file) => {
  if (!props.service.upload) {
    Eventy.showHideMessage("Upload not available", "error");
    close();
    return;
  }
  Eventy.showMessage("Uploading file, Please wait!", "loading");
  close();
  let formData = new FormData();
  formData.append("file", file);
  await props.service.upload(formData);
  await loadData();
  Eventy.hideMessage();
};

const onColumnPicker = (e) => {
  ev.value = e;
  showColumnPicker.value = true;
};

const saveEdit = async (o) => {
  Eventy.showMessage("Updating data, Please wait!", "loading");
  for (const key in o) {
    o[key] = o[key]?.length == 0 ? null : o[key];
  }
  await props.service.update(o);
  await loadData();
  Eventy.showHideMessage(`${props.name} saved`, "success", 5000);
  close();
};

const saveAdd = async (o) => {
  Eventy.showMessage("Inserting data, Please wait!", "loading");
  for (const key in o) {
    o[key] = o[key]?.length == 0 ? null : o[key];
  }
  await props.service.insert(o);
  await loadData();
  Eventy.showHideMessage(`${props.name} saved`, "success", 5000);
  close();
};

const saveDelete = async (o) => {
  Eventy.showMessage("Deleting data, Please wait!", "loading");
  showConfirm.value = false;
  await props.service.delete(selected.value);
  await loadData();
  Eventy.showHideMessage(`${props.name} deleted`, "success", 5000);
  close();
};

const close = () => {
  showEdit.value = false;
  showAdd.value = false;
  showUpload.value = false;
  showColumnPicker.value = false;
  showContextmenu.value = false;
  showConfirm.value = false;
  selected.value = {};
  ev.value = {};
};

const cmp_data = computed(() => filterList(q.value, data.value, !props.options.properties ? [] : props.options.properties.filter((p) => !p.showInGrid).map((p) => p.prop)));

const cmp_properties = computed(() => {
  if (!props.options.properties) return [];
  return props.options.properties.filter((p) => p.type != "custom");
});
</script>

<template>
  <common-layout>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete?" @close="close" @ok="saveDelete" />
    <contextmenu-crud :show="showContextmenu" :ev="ev" @click-outside="close" @on-edit="onEdit" @onDelete="onDelete" />
    <file-upload :show="showUpload" :ev="ev" @click-outside="close" @on-upload-click="onUploadClick" />
    <column-picker :show="showColumnPicker" :ev="ev" :properties="cmp_properties" @click-outside="close" />

    <component v-if="showAddButton" :is="crudComponent" :is-edit="false" :show="showAdd" :options="options" @close="close" @save="saveAdd" />
    <component :is="crudComponent" :is-edit="true" :show="showEdit" :options="options" :selected-value="selected" @close="close" @save="saveEdit" />

    <tool-bar :title="name" v-model:q="q" :show-add="showAddButton" :show-download="showDownloadButton" :show-upload="showUploadButton" @add-click="showAdd = true" @upload-click="onUpload" @download-click="onDownload" @column-picker-click="onColumnPicker" />

    <grid :id="id" v-model:selected="selected" v-model:ev="ev" :properties="cmp_properties" :values="cmp_data" @on-right-click="showContextmenu = true" />
  </common-layout>
</template>

<style></style>
