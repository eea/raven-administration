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

const emit = defineEmits(["update:selected", "on-right-click", "on-dbl-click"]);

// Map properties to DataTable column format
const columns = computed(() => {
  return props.properties
    .filter((p) => p.showInGrid)
    .map((prop) => {
      const col = {
        field: prop.prop,
        headerName: prop.label,
        sortable: true
        // tooltipField: prop.prop
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

const onRightClick = (data, event, gridEvent) => {
  // Select the row and emit event with data and event
  emit("update:selected", [klona(data)]);
  emit("on-right-click", data, event, gridEvent);
};

const onDoubleClick = (data, event, gridEvent) => {
  // Select the row and emit event
  emit("update:selected", [klona(data)]);
  emit("on-dbl-click");
};
</script>

<template>
  <DataTable :data="values" :columns="columns" :filter="true" :floating-filter="false" :responsive="true" :get-row-style="getRowStyle" @on-right-click="onRightClick" @on-double-click="onDoubleClick" />
</template>

<style scoped></style>
