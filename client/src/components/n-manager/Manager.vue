<script setup>
import { computed, onMounted, ref } from "vue";
import Eventy from "../../helpers/eventy";
import Crud from "./Crud.vue";
import GridDataTable from "./GridDataTable.vue";
import useFilter from "../../composables/useFilter";
import Confirm from "../Confirm.vue";
import ToolBar from "../ToolBar.vue";
import CommonLayout from "../CommonLayout.vue";
import CMenuItems from "../CMenuItems.vue";
import CmdK from "../CmdK.vue";

const emit = defineEmits(["context-menu-action"]);

const props = defineProps({
  name: String,
  options: Object,
  service: Object,
  crudComponent: {
    type: [String, Object],
    default: Crud
  },
  showDownloadButton: {
    type: Boolean,
    default: true
  },
  showAddButton: {
    type: Boolean,
    default: true
  },
  // Derived row sets -- AQR3 CAM is rebuilt by Recalculate compliance -- have no
  // delete: the spec retracts a row with a flag, not by removing it.
  showDeleteButton: {
    type: Boolean,
    default: true
  },
  showDuplicate: {
    type: Boolean,
    default: false
  }
});

const showUpload = computed(() => typeof props.service?.upload === "function");
const fileInput = ref(null);

const data = ref([]);

const showEdit = ref(false);
const showAdd = ref(false);
const duplicateSource = ref(null);

const selected = ref([]);

const showConfirm = ref(false);

const { q, filteredList } = useFilter(data);

onMounted(async () => {
  await loadData();
});

const loadData = async () => {
  data.value = await props.service.get();
};

const onDoubleClick = () => {
  if (showEdit.value) selected.value = [];
  showEdit.value = !showEdit.value;
};

const onDownload = async () => {
  if (typeof props.service?.download === "function") {
    await props.service.download();
  }
};

const onUpload = () => {
  fileInput.value.click();
};

const onFileChange = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  const formData = new FormData();
  formData.append("file", file);
  try {
    await props.service.upload(formData);
    await loadData();
    Eventy.showHideMessage(`${props.name} imported successfully`, "success", 5000);
  } finally {
    event.target.value = "";
  }
};

const onContextMenuAction = ({ action, data }) => {
  if (action === "edit") {
    selected.value = data?.row ? [data.row] : [];
    showEdit.value = true;
  } else if (action === "delete") {
    selected.value = data?.row ? [data.row] : [];
    showConfirm.value = true;
  } else if (action === "duplicate") {
    duplicateSource.value = data?.row ? { ...data.row } : null;
    showAdd.value = true;
  } else {
    emit("context-menu-action", { action, data });
  }
};

// Entities whose primary key is a single `id` column post a flat object and are
// deleted by `{ids: [...]}`; that is the shape `core/query.py::Q.delete` speaks and
// what every page predating AQR3 v5.02 uses. Declare `keyProps` in pageOptions when
// the key spans several columns -- the AQR3 tables all do -- and update/delete switch
// to the `{key, values}` shape those blueprints expect.
const cmp_keyProps = computed(() => props.options?.keyProps ?? ["id"]);
const isCompositeKey = computed(() => cmp_keyProps.value.length > 1);

const keyOf = (row) => Object.fromEntries(cmp_keyProps.value.map((k) => [k, row?.[k]]));

const saveEdit = async (o) => {
  Eventy.showMessage("Updating data, Please wait!", "loading");
  for (const key in o) {
    o[key] = o[key]?.length == 0 ? null : o[key];
  }
  if (isCompositeKey.value) {
    // selected[0] is the row as loaded -- Crud edits its own copy -- so the original
    // key survives even when the user changes a key column. An UPDATE keyed on the
    // new values would match nothing and leave the original row in place.
    await props.service.update(keyOf(selected.value[0]), o);
  } else {
    await props.service.update(o);
  }
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
  if (selected.value?.length == 0) return;

  Eventy.showMessage("Deleting data, Please wait!", "loading");
  showConfirm.value = false;
  if (isCompositeKey.value) {
    // `where id in (...)` cannot address a composite key, so these delete one row.
    for (const row of selected.value) await props.service.delete(keyOf(row));
  } else {
    await props.service.delete({ ids: selected.value.map((p) => p.id) });
  }
  await loadData();
  Eventy.showHideMessage(`${props.name} deleted`, "success", 5000);
  close();
};

const close = () => {
  showEdit.value = false;
  showAdd.value = false;
  showConfirm.value = false;
  selected.value = [];
  duplicateSource.value = null;
};

const cmp_properties = computed(() => {
  if (!props.options.properties) return [];
  return props.options.properties.filter((p) => p.type != "custom");
});
</script>

<template>
  <common-layout>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete?" @close="close" @ok="saveDelete" />

    <component v-if="showAddButton" :is="crudComponent" :is-edit="false" :show="showAdd" :options="options" :duplicate-source="duplicateSource" @close="close" @save="saveAdd" />
    <component :is="crudComponent" :is-edit="true" :show="showEdit" :options="options" :selected-value="selected[0]" @close="close" @save="saveEdit" />

    <CmdK v-model="q" :result-count="filteredList.length" />

    <tool-bar :title="name" v-model:q="q" :show-add="showAddButton" :show-download="showDownloadButton" :show-upload="showUpload" @add-click="showAdd = true" @download-click="onDownload" @upload-click="onUpload">
      <!-- Page-specific toolbar controls: a year selector, a bulk action. -->
      <slot name="toolbar" v-bind="{ reload: loadData }" />
    </tool-bar>
    <input ref="fileInput" type="file" accept=".csv,.gpkg" class="hidden" @change="onFileChange" />

    <grid-data-table v-model:selected="selected" :properties="cmp_properties" :values="filteredList" :get-row-style="options.getRowStyle" @context-menu-action="onContextMenuAction" @on-dbl-click="onDoubleClick">
      <template #context-menu-items="{ handleAction, contextData }">
        <CMenuItems :show-duplicate="showDuplicate" :show-delete="showDeleteButton" @edit="handleAction('edit')" @delete="handleAction('delete')" @duplicate="handleAction('duplicate')" />
        <slot name="extra-context-menu-items" v-bind="{ handleAction, contextData }" />
      </template>
    </grid-data-table>
  </common-layout>
</template>

<style></style>
