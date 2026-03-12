<script setup>
import { AllCommunityModule, ModuleRegistry, ClientSideRowModelModule, TooltipModule } from "ag-grid-community";
import { AgGridVue } from "ag-grid-vue3";
import { ref, watch, computed } from "vue";
import { themeQuartz } from "ag-grid-community";
import CMenu from "./CMenu.vue";
import { rowsToCsv, columnHeadersToCsv, copyToClipboard, copyCellValue } from "../helpers/utilsCopy.js";
import IconCopy from "~icons/ic/twotone-content-copy";
// import IconCopyCell from "~icons/ic/twotone-content-copy";
// import IconCopyRows from "~icons/ic/twotone-content-paste";
// import IconCopyHeaders from "~icons/ic/twotone-view-headline";

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
  },
  showCopyOptions: {
    type: Boolean,
    required: false,
    default: false
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

const emit = defineEmits(["on-double-click", "selection-changed", "grid-ready", "context-menu-action"]);

const colDefs = ref([]);
const gridApi = ref(null);
const builtinMenuRef = ref(null);
const contextData = ref(null);

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
  const { detail, button, ctrlKey } = event.event; // Extract properties

  // Right-click (button === 2) - show unified context menu
  if (button === 2) {
    // Ensure the right-clicked row is selected for consistent UX with bulk operations
    if (gridApi.value && event.data) {
      const selectedRows = gridApi.value.getSelectedRows();
      const isRowSelected = selectedRows.some((r) => r === event.data);

      if (!isRowSelected) {
        if (ctrlKey) {
          // Ctrl+right-click: add to existing selection
          gridApi.value.forEachNode((node) => {
            if (node.data === event.data) {
              node.setSelected(true);
            }
          });
        } else {
          // Plain right-click: replace selection with clicked row
          gridApi.value.deselectAll();
          gridApi.value.forEachNode((node) => {
            if (node.data === event.data) {
              node.setSelected(true);
            }
          });
        }
      }
    }

    contextData.value = { row: event.data, event: event.event, gridEvent: event };
    builtinMenuRef.value?.showMenu(contextData.value, event.event);
    return;
  }
  // Double-click
  if (detail === 2) {
    emit("on-double-click", event.data, event.event, event);
    return;
  }
  // Single left-click - deselect if no selection mode enabled
  if (detail === 1 && !props.selectionMode) {
    gridApi.value?.deselectAll();
  }
};

/**
 * Get visible columns from the grid API
 */
const getVisibleColumns = () => {
  if (!gridApi.value) return [];
  return gridApi.value.getAllDisplayedColumns().map((col) => col.getColDef());
};

/**
 * Copy selected rows (or right-clicked row) as CSV to clipboard
 */
const copyRowsAsCsv = async () => {
  const selectedRows = gridApi.value?.getSelectedRows() || [];
  const rowsToCopy = selectedRows.length > 0 ? selectedRows : contextData.value?.row ? [contextData.value.row] : [];

  if (rowsToCopy.length === 0) return false;

  const visibleColumns = getVisibleColumns();
  const csv = rowsToCsv(rowsToCopy, visibleColumns);
  return await copyToClipboard(csv);
};

/**
 * Copy column headers as CSV to clipboard
 */
const copyHeadersAsCsv = async () => {
  const visibleColumns = getVisibleColumns();
  const csv = columnHeadersToCsv(visibleColumns);
  return await copyToClipboard(csv);
};

/**
 * Copy clicked cell value to clipboard
 */
const copyCell = async () => {
  const cellValue = contextData.value?.gridEvent?.value;
  return await copyCellValue(cellValue);
};

/**
 * Handle context menu actions (both built-in and custom)
 */
const handleMenuAction = async (action) => {
  if (action === "copy-rows-csv") {
    await copyRowsAsCsv();
  } else if (action === "copy-headers-csv") {
    await copyHeadersAsCsv();
  } else if (action === "copy-cell") {
    await copyCell();
  }
  emit("context-menu-action", { action, data: contextData.value });
  builtinMenuRef.value?.hideMenu();
};

const hasCustomMenuItems = computed(() => {
  return !!slots["context-menu-items"];
});

const slots = defineSlots();

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

  <!-- Context menu -->
  <CMenu ref="builtinMenuRef" @on-click="({ action }) => handleMenuAction(action)">
    <template #default="{ handleAction }">
      <!-- Custom items from parent -->
      <slot name="context-menu-items" :handleAction="handleMenuAction" :contextData="contextData" :gridApi="gridApi" />
      <!-- Built-in copy options -->
      <template v-if="showCopyOptions">
        <div v-if="hasCustomMenuItems" class="border-t border-nord4 mt-1 pt-1"></div>
        <div @click="handleAction('copy-cell')" class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6 whitespace-nowrap">
          <IconCopy class="text-nord9 text-base self-center" />
          <div class="self-center ml-1">Copy cell value</div>
        </div>
        <div @click="handleAction('copy-rows-csv')" class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6 whitespace-nowrap">
          <IconCopy class="text-nord9 text-base self-center" />
          <div class="self-center ml-1">Copy rows as CSV</div>
        </div>
        <div @click="handleAction('copy-headers-csv')" class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6 whitespace-nowrap">
          <IconCopy class="text-nord9 text-base self-center" />
          <div class="self-center ml-1">Copy headers as CSV</div>
        </div>
      </template>
    </template>
  </CMenu>
</template>
