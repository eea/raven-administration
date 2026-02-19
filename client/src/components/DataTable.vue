<script setup>
import { AllCommunityModule, ModuleRegistry, ClientSideRowModelModule, TooltipModule } from "ag-grid-community";
import { AgGridVue } from "ag-grid-vue3";
import { ref, watch, computed } from "vue";
import { themeQuartz } from "ag-grid-community";

ModuleRegistry.registerModules([AllCommunityModule, ClientSideRowModelModule, TooltipModule]);

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
  searchWord: {
    type: String,
    required: false,
    default: ""
  },
  loading: {
    type: Boolean,
    required: false,
    default: false
  },
  floatingFilter: {
    type: Boolean,
    required: false,
    default: false
  },
  filter: {
    type: Boolean,
    required: false,
    default: true
  },
  selectionMode: {
    type: String,
    required: false,
    default: null // "singleRow" or "multiRow"
  },
  enableClickSelection: {
    type: Boolean,
    required: false,
    default: null // null = auto-detect based on editable columns
  },
  getRowId: {
    type: Function,
    required: false,
    default: undefined
  },
  fontSize: {
    type: Number,
    required: false,
    default: 14
  }
});

const highlightRenderer = (params) => {
  const value = params.value ?? "";
  const keyword = props.searchWord || "";
  if (!keyword) return value;

  const regex = new RegExp(`(${keyword})`, "gi");
  const highlighted = value.toString().replace(regex, `<span style="background: yellow">$1</span>`);

  return highlighted;
};

const emit = defineEmits(["on-double-click", "on-right-click", "selection-changed", "grid-ready"]);

const colDefs = ref([]);
const gridApi = ref(null);
defineExpose({ gridApi });

const hasEditableColumns = computed(() => {
  return colDefs.value.some((col) => col.editable === true);
});

const rowSelection = computed(() => {
  if (!props.selectionMode) return { mode: "singleRow", checkboxes: false, headerCheckbox: false, enableClickSelection: false };

  const isMultiRow = props.selectionMode === "multiRow";

  // Auto-detect: disable click selection if grid has editable columns (unless explicitly overridden)
  const shouldEnableClickSelection = props.enableClickSelection !== null ? props.enableClickSelection : !hasEditableColumns.value;

  return {
    mode: isMultiRow ? "multiRow" : "singleRow",
    checkboxes: isMultiRow,
    headerCheckbox: isMultiRow,
    enableClickSelection: shouldEnableClickSelection,
    enableSelectionWithoutKeys: isMultiRow
  };
});

const defaultColDef = {
  // minWidth: 100,
  sortable: true,
  resizable: true,
  filter: props.filter,
  floatingFilter: props.floatingFilter,
  cellRendererParams: {
    suppressCount: true
  },
  // Needed so HTML in renderer is rendered as HTML, but don't override
  // explicit cellRenderers (e.g. custom icons like DeleteIcon).
  cellRendererSelector: (params) => {
    const col = params.colDef || {};
    // If column defines its own cellRenderer or selector, let it win.
    if (col.cellRenderer) return null;
    // Otherwise, use the highlight renderer.
    return {
      component: highlightRenderer,
      params: {}
    };
  }
};
if (props.responsive) defaultColDef.flex = 1;

// to use myTheme in an application, pass it to the theme grid option
const myTheme = themeQuartz.withParams({
  accentColor: "#81a1c1",
  backgroundColor: "#F9FBFC",
  borderColor: "#d8dee9",
  borderRadius: 2,
  browserColorScheme: "light",
  fontFamily: ["ui-sans-serif", "system-ui", "sans-serif"],
  foregroundColor: "#4C566A",
  headerBackgroundColor: "#F3F5F7",
  headerFontWeight: 600,
  headerFontSize: props.fontSize,
  headerRowBorder: true,
  fontSize: props.fontSize,
  spacing: 4,
  wrapperBorderRadius: 4,

  checkboxUncheckedBackgroundColor: "#fff",
  checkboxUncheckedBorderColor: "#d8dee9",
  checkboxCheckedBackgroundColor: "#3b4252",
  checkboxCheckedBorderColor: "#d8dee9",
  checkboxCheckedShapeColor: "#fff",
  checkboxIndeterminateBorderColor: "#d8dee9",
  checkboxIndeterminateBackgroundColor: "#4c566a"
});

// Watch for changes in props.columns only
watch(
  () => props.columns,
  (newColumns) => {
    if (newColumns !== null && newColumns !== undefined) {
      colDefs.value = newColumns;
    } else if (props.data?.length > 0) {
      colDefs.value = Object.keys(props.data[0]).map((field) => ({ field }));
    } else {
      colDefs.value = [];
    }
  },
  { immediate: true }
);

const onClicked = (event) => {
  const { detail, button } = event.event; // Extract properties
  // console.log('click', event);

  // Right-click (button === 2)
  if (button === 2) {
    emit("on-right-click", event.data, event.event, event);
    return;
  }
  // Double-click
  if (detail === 2) {
    // console.log("Double Click:", event.data);
    emit("on-double-click", event.data, event.event, event);
    return;
  }
};

const onSelectionChanged = (event) => {
  emit("selection-changed", event.api.getSelectedRows());
};

const onGridReady = (params) => {
  gridApi.value = params.api; // Store API reference

  // Only call sizeColumnsToFit if no flex columns are defined
  const hasFlexColumns = colDefs.value.some((col) => col.flex);
  if (!hasFlexColumns) {
    params.api.sizeColumnsToFit();
  }

  emit("grid-ready", params.api);
};
</script>

<template>
  <ag-grid-vue @selection-changed="onSelectionChanged" :rowSelection="rowSelection" :getRowId="getRowId" :tooltipShowDelay="0" :tooltipHideDelay="10000" :tooltipShowMode="'whenTruncated'" style="width: 100%; height: 100%" :loading="loading" :getRowStyle="getRowStyle" :defaultColDef="defaultColDef" :columnDefs="colDefs" :rowData="data" :theme="myTheme" :suppressClickEdit="false" :suppressRowTransform="true" :suppressColumnVirtualisation="false" :immutableData="false" :suppressCellFlash="true" @grid-ready="onGridReady" @cell-context-menu="onClicked" @cell-clicked="onClicked" oncontextmenu="return false;"></ag-grid-vue>
</template>
