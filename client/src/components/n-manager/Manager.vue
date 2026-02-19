<script setup>
import { computed, onMounted, ref } from "vue";
import Eventy from "../../helpers/eventy";
import Crud from "./Crud.vue";
import GridDataTable from "./GridDataTable.vue";
import CMenuCrud from "../CMenuCrud.vue";
import useFilter from "../../composables/useFilter";
import Confirm from "../Confirm.vue";
import ToolBar from "../ToolBar.vue";
import CommonLayout from "../CommonLayout.vue";
import IconCopy from "~icons/ic/twotone-content-copy";

const props = defineProps({
  name: String,
  options: Object,
  service: Object,
  crudComponent: {
    type: [String, Object],
    default: Crud
  },
  contextMenuComponent: {
    type: [String, Object],
    default: null
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

const showContextmenu = ref(false);
const showConfirm = ref(false);
const contextMenuRef = ref(null);
const currentGridEvent = ref(null);

const { q, filteredList } = useFilter(data);

onMounted(async () => {
  await loadData();
  //console.log(props.options.lookups["organizations"]);
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

const onRightClick = (data, event, gridEvent) => {
  currentGridEvent.value = gridEvent;
  if (contextMenuRef.value) {
    contextMenuRef.value.showMenu(data, event);
    showContextmenu.value = true;
  }
};

const onMenuClick = ({ action, data }) => {
  showContextmenu.value = false;

  if (action === "edit") {
    selected.value = [data];
    showEdit.value = true;
  } else if (action === "delete") {
    selected.value = [data];
    showConfirm.value = true;
  } else if (action === "copy-cell") {
    copyToClipboard();
  }
};

const copyToClipboard = async () => {
  if (!currentGridEvent.value?.value) return;

  try {
    const cellValue = String(currentGridEvent.value.value);
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
  showContextmenu.value = false;
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
    <c-menu-crud ref="contextMenuRef" @click-outside="close" @on-menu-click="onMenuClick">
      <template #extra-items="{ handleAction }">
        <div class="border-t border-nord4 pt-1">
          <div class="pl-2 pr-4 py-1 flex cursor-pointer hover:bg-gray-100" @click="handleAction('copy-cell')">
            <icon-copy class="text-nord9 text-sm self-center" />
            <div class="self-center ml-1">Copy cell value</div>
          </div>
        </div>
      </template>
    </c-menu-crud>

    <component v-if="showAddButton" :is="crudComponent" :is-edit="false" :show="showAdd" :options="options" @close="close" @save="saveAdd" />
    <component :is="crudComponent" :is-edit="true" :show="showEdit" :options="options" :selected-value="selected[0]" @close="close" @save="saveEdit" />

    <tool-bar :title="name" v-model:q="q" :show-add="showAddButton" :show-download="showDownloadButton" @add-click="showAdd = true" @download-click="onDownload" />

    <grid-data-table v-model:selected="selected" :properties="cmp_properties" :values="filteredList" :get-row-style="options.getRowStyle" @on-right-click="onRightClick" @on-dbl-click="onDoubleClick" />
  </common-layout>
</template>

<style></style>
