<script setup>
import { computed, onMounted, ref } from "vue";
import Eventy from "../../helpers/eventy";
import Crud from "./Crud.vue";
import GridDataTable from "./GridDataTable.vue";
import useFilter from "../../composables/useFilter";
import Confirm from "../Confirm.vue";
import ToolBar from "../ToolBar.vue";
import CommonLayout from "../CommonLayout.vue";
import IconEdit from "~icons/ph/pencil-simple-duotone";
import IconDelete from "~icons/ph/trash-duotone";
import IconCopy from "~icons/ic/twotone-content-copy";

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
  }
});

const data = ref([]);

const showEdit = ref(false);
const showAdd = ref(false);

const selected = ref([]);

const showConfirm = ref(false);
const currentContextData = ref(null);

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
  // Export filtered data to CSV
  if (!filteredList.value || filteredList.value.length === 0) {
    return;
  }

  const visibleProps = cmp_properties.value.filter((p) => p.showInGrid);
  const headers = visibleProps.map((p) => p.label);

  const rows = filteredList.value.map((row) => {
    return visibleProps.map((prop) => {
      let value = row[prop.prop];

      // Handle different types
      if (prop.type === "checkbox") {
        value = value ? "true" : "false";
      } else if (prop.type === "gridOnly" && prop.val_func) {
        value = prop.val_func(row);
      }

      // Escape and quote
      if (value == null) value = "";
      value = String(value).replace(/"/g, '""');
      return `"${value}"`;
    });
  });

  const csv = [headers.map((h) => `"${h}"`).join(","), ...rows.map((r) => r.join(","))].join("\n");

  const filename = `${props.options.csvName || props.name}.csv`;
  const link = document.createElement("a");
  link.style.display = "none";
  link.setAttribute("href", "data:text/csv;charset=utf-8," + encodeURIComponent(csv));
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const onContextMenuAction = ({ action, data }) => {
  currentContextData.value = data;

  if (action === "edit") {
    selected.value = data?.row ? [data.row] : [];
    showEdit.value = true;
  } else if (action === "delete") {
    selected.value = data?.row ? [data.row] : [];
    showConfirm.value = true;
  } else if (action === "copy-cell") {
    copyToClipboard();
  }
};

const copyToClipboard = async () => {
  if (!currentContextData.value?.gridEvent?.value) return;

  try {
    const cellValue = String(currentContextData.value.gridEvent.value);
    await navigator.clipboard.writeText(cellValue);
    console.log("Copied cell value to clipboard:", cellValue);
  } catch (err) {
    console.error("Failed to copy to clipboard:", err);
  }
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
  if (selected.value?.length == 0) return;

  Eventy.showMessage("Deleting data, Please wait!", "loading");
  showConfirm.value = false;
  await props.service.delete({ ids: selected.value.map((p) => p.id) });
  await loadData();
  Eventy.showHideMessage(`${props.name} deleted`, "success", 5000);
  close();
};

const close = () => {
  showEdit.value = false;
  showAdd.value = false;
  showConfirm.value = false;
  selected.value = [];
};

const cmp_properties = computed(() => {
  if (!props.options.properties) return [];
  return props.options.properties.filter((p) => p.type != "custom");
});
</script>

<template>
  <common-layout>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete?" @close="close" @ok="saveDelete" />

    <component v-if="showAddButton" :is="crudComponent" :is-edit="false" :show="showAdd" :options="options" @close="close" @save="saveAdd" />
    <component :is="crudComponent" :is-edit="true" :show="showEdit" :options="options" :selected-value="selected[0]" @close="close" @save="saveEdit" />

    <tool-bar :title="name" v-model:q="q" :show-add="showAddButton" :show-download="showDownloadButton" @add-click="showAdd = true" @download-click="onDownload" />

    <grid-data-table v-model:selected="selected" :properties="cmp_properties" :values="filteredList" :get-row-style="options.getRowStyle" @context-menu-action="onContextMenuAction" @on-dbl-click="onDoubleClick">
      <template #context-menu-items="{ handleAction, contextData }">
        <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('edit')">
          <icon-edit class="text-nord10 text-base self-center" />
          <div class="self-center ml-1">Edit</div>
        </div>
        <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('delete')">
          <icon-delete class="text-nord11 text-base self-center" />
          <div class="self-center ml-1">Delete</div>
        </div>
        <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('copy-cell')">
          <icon-copy class="text-nord9 text-sm self-center" />
          <div class="self-center ml-1">Copy cell value</div>
        </div>
      </template>
    </grid-data-table>
  </common-layout>
</template>

<style></style>
