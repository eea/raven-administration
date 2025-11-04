<script setup>
import { AllCommunityModule, ModuleRegistry, ClientSideRowModelModule } from "ag-grid-community";
import { AgGridVue } from "ag-grid-vue3";
import { ref, watch } from "vue";
import { themeQuartz } from "ag-grid-community";
import { isTouchBased } from "../helpers/utils";

ModuleRegistry.registerModules([AllCommunityModule, ClientSideRowModelModule]);

const props = defineProps({
  data: Array,
  columns: {
    type: Array,
    required: false,
    default: null
  },
  responsive: {
    type: Boolean,
    required: false,
    default: true
  },
  getRowStyle: {
    type: Function,
    required: false,
    default: () => {
      return null;
    }
  },
  floatingFilter: {
    type: Boolean,
    required: false,
    default: true
  },
  filter: {
    type: Boolean,
    required: false,
    default: true
  },
  enableCellTextSelection: {
    type: Boolean,
    required: false,
    default: false
  }
});

const emit = defineEmits(["on-double-click", "on-right-click"]);

const colDefs = ref([]);
const gridApi = ref(null);
defineExpose({ gridApi });

const isTouchDevice = isTouchBased();

const defaultColDef = {
  // minWidth: 100,
  sortable: true,
  resizable: true,
  filter: props.filter,
  floatingFilter: props.filter ? props.floatingFilter : false
};
if (props.responsive) defaultColDef.flex = 1;

// to use myTheme in an application, pass it to the theme grid option
const myTheme = themeQuartz.withParams({
  accentColor: "#81a1c1",
  backgroundColor: "#F9FBFC",
  borderColor: "#d8dee9",
  borderRadius: 2,
  browserColorScheme: "light",
  fontFamily: {
    googleFont: "Inter"
  },
  foregroundColor: "#4C566A",
  headerBackgroundColor: "#F3F5F7",
  headerFontWeight: 600,
  headerFontSize: 13,
  headerRowBorder: true,
  fontSize: 13,
  spacing: 4,
  wrapperBorderRadius: 4
});

// Watch for changes in props.data and update colDefs
watch(
  () => [props.data, props.columns],
  ([newData, newColumns]) => {
    if (newColumns !== null) {
      colDefs.value = newColumns.map(
        (col) => (typeof col === "string" ? { field: col } : col) // Convert strings to objects
      );
    } else if (newData?.length > 0) {
      colDefs.value = Object.keys(newData[0]).map((field) => ({ field }));
    } else {
      colDefs.value = [];
    }
  },
  { immediate: true }
);

const onClicked = (event) => {
  const { detail, button } = event.event; // Extract properties
  // console.log("isTouchDevice", isTouchDevice);

  // Right-click (button === 2)
  if (button === 2) {
    // console.log("Right Click:", event.data);
    emit("on-right-click", event.data, event.event);
    return;
  }
  // Double-click
  if (detail === 2) {
    // console.log("Double Click:", event.data);
    emit("on-double-click", event.data, event.event);
    return;
  }
  if (isTouchDevice && button === 0) {
    // Handle single click on mobile with a slight delay
    setTimeout(() => {
      emit("on-right-click", event.data, event.event);
    }, 200); // 200ms delay
    return;
  }
};

const onGridReady = (params) => {
  gridApi.value = params.api; // Store API reference
  params.api.sizeColumnsToFit();
  // console.log(params.api);
  //params.api.autoSizeAllColumns();
};
</script>

<template>
  <ag-grid-vue :tooltipShowDelay="0" :tooltipHideDelay="10000" style="width: 100%; height: 100%" :getRowStyle="getRowStyle" :defaultColDef="defaultColDef" :columnDefs="colDefs" :rowData="data" :theme="myTheme" :suppressClickEdit="true" :enableCellTextSelection="enableCellTextSelection" @grid-ready="onGridReady" @cell-context-menu="onClicked" @cell-clicked="onClicked" oncontextmenu="return false;"></ag-grid-vue>
</template>
