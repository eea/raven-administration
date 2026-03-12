<script setup>
import { computed } from "vue";
import { klona } from "klona";
import DataTable from "../DataTable.vue";

const props = defineProps({
  properties: Array,
  values: Array,
  selected: Array,
  getRowStyle: {
    type: Function,
    default: null
  }
});

const emit = defineEmits(["update:selected", "on-dbl-click", "context-menu-action"]);

// Map properties to DataTable column format
const columns = computed(() => {
  return props.properties
    .filter((p) => p.showInGrid)
    .map((prop) => {
      const col = {
        field: prop.prop,
        headerName: prop.label,
        sortable: true
      };

      // Handle width and flex
      if (prop.width) col.width = prop.width;
      if (prop.flex) col.flex = prop.flex;

      // Handle different property types
      if (prop.type === "checkbox") {
        col.cellRenderer = (params) => {
          const checked = params.value ? "checked" : "";
          return `<input type="checkbox" ${checked} disabled   />`;
        };
      } else if (prop.type === "gridOnly" && prop.val_func) {
        col.valueGetter = (params) => {
          return prop.val_func(klona(params.data));
        };
      }

      // Handle cell class
      if (prop.cls_func) {
        col.cellClass = (params) => {
          return prop.cls_func(klona(params.data));
        };
      }
      return col;
    });
});

const onContextMenuAction = ({ action, data }) => {
  // Select the row when context menu is used
  if (data?.row) {
    emit("update:selected", [klona(data.row)]);
  }
  emit("context-menu-action", { action, data });
};

const onDoubleClick = (data, event, gridEvent) => {
  // Select the row and emit event
  emit("update:selected", [klona(data)]);
  emit("on-dbl-click");
};
</script>

<template>
  <DataTable :data="values" :columns="columns" :filter="true" :floating-filter="false" :responsive="true" :get-row-style="getRowStyle" :show-copy-options="true" @context-menu-action="onContextMenuAction" @on-double-click="onDoubleClick">
    <template #context-menu-items="slotProps">
      <slot name="context-menu-items" v-bind="slotProps" />
    </template>
  </DataTable>
</template>

<style scoped></style>
