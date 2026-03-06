<script setup>
import { onMounted, ref } from "vue";
import CommonLayout from "../../../components/CommonLayout.vue";
import ToolBar from "../../../components/ToolBar.vue";
import Container from "../../../components/Container.vue";
import DataTable from "../../../components/DataTable.vue";
import CMenu from "../../../components/CMenu.vue";
import Service from "./service";
import Eventy from "../../../helpers/eventy";

const years = ref([]);
const selectedYear = ref(null);
const data = ref([]);
const loading = ref(false);
const exceedanceOptions = ref([]);
const documentOptions = ref([]);
const gridApi = ref(null);
const menuRef = ref(null);
const selectedReportId = ref("");
const selectedThreshold = ref("");

const onGridReady = (api) => {
  gridApi.value = api;
};

const getRowId = (params) => {
  return `${params.data.zone_id}_${params.data.environmental_objective_id}`;
};

const onContextMenu = (row, e) => {
  if (gridApi.value) {
    const selectedRows = gridApi.value.getSelectedRows();
    const isRowSelected = selectedRows.some((r) => r === row);

    if (!isRowSelected) {
      if (e.ctrlKey) {
        gridApi.value.forEachNode((node) => {
          if (node.data === row) {
            node.setSelected(true);
          }
        });
      } else {
        gridApi.value.deselectAll();
        gridApi.value.forEachNode((node) => {
          if (node.data === row) {
            node.setSelected(true);
          }
        });
      }
    }
  }

  menuRef.value?.showMenu(row, e);
};

const onMenuClick = async ({ action, data: rowData }) => {
  if (action === "update") {
    await updateRows(rowData);
  } else if (action === "clear") {
    await clearRows(rowData);
  }
};

const updateRows = async (row) => {
  const selectedRows = gridApi.value?.getSelectedRows() || [];
  let rowsToUpdate = selectedRows.length > 0 ? selectedRows : row ? [row] : [];

  if (rowsToUpdate.length === 0) {
    Eventy.showHideMessage("No rows selected", "error", 3000);
    return;
  }

  if (!selectedReportId.value || !selectedThreshold.value) {
    Eventy.showHideMessage("Both threshold and document must be selected", "error", 3000);
    return;
  }

  rowsToUpdate.forEach((r) => {
    r.classification_report_id = selectedReportId.value;
    r.assessment_threshold_exceedance = selectedThreshold.value;
  });

  try {
    Eventy.showMessage("Saving...", "loading");
    await Service.updateRows({ records: rowsToUpdate });
    gridApi.value.applyTransaction({ update: rowsToUpdate });
    Eventy.hideMessage();
    Eventy.showHideMessage(`Updated ${rowsToUpdate.length} row(s)`, "success", 2000);
  } catch (error) {
    console.error("Error updating rows:", error);
    Eventy.showHideMessage("Error saving changes", "error", 3000);
  }

  menuRef.value?.hideMenu();
  selectedReportId.value = "";
  selectedThreshold.value = "";
  gridApi.value.deselectAll();
};

const clearRows = async (row) => {
  const selectedRows = gridApi.value?.getSelectedRows() || [];
  let rowsToClear = selectedRows.length > 0 ? selectedRows : row ? [row] : [];

  if (rowsToClear.length === 0) {
    Eventy.showHideMessage("No rows selected", "error", 3000);
    return;
  }

  rowsToClear.forEach((r) => {
    r.classification_report_id = null;
    r.assessment_threshold_exceedance = null;
  });

  try {
    Eventy.showMessage("Saving...", "loading");
    await Service.updateRows({ records: rowsToClear });
    gridApi.value.applyTransaction({ update: rowsToClear });
    Eventy.hideMessage();
    Eventy.showHideMessage(`Cleared ${rowsToClear.length} row(s)`, "success", 2000);
  } catch (error) {
    console.error("Error clearing rows:", error);
    Eventy.showHideMessage("Error saving changes", "error", 3000);
  }

  menuRef.value?.hideMenu();
  selectedReportId.value = "";
  selectedThreshold.value = "";
  gridApi.value.deselectAll();
};

const columns = ref([
  { field: "zone_id", headerName: "Zone Id", sortable: true, filter: true, minWidth: 100, flex: 1 },
  { field: "zone_name", headerName: "Zone Name", sortable: true, filter: true, minWidth: 150, flex: 1.5 },
  { field: "pollutant_name", headerName: "Pollutant Name", sortable: true, filter: true, minWidth: 120, flex: 1 },
  { field: "protection_target", headerName: "Protection Target", sortable: true, filter: true, minWidth: 120, flex: 1 },
  { field: "objective_type", headerName: "Objective Type", sortable: true, filter: true, minWidth: 110, flex: 1 },
  { field: "reporting_metric", headerName: "Reporting Metric", sortable: true, filter: true, minWidth: 120, flex: 1 },
  { field: "classification_year", headerName: "Classification Year", sortable: true, filter: true, minWidth: 100, flex: 0.8 },
  { field: "classification_report_id", headerName: "Classification Document", sortable: true, filter: true, minWidth: 150, flex: 1.5 },
  {
    field: "assessment_threshold_exceedance",
    headerName: "Threshold Exceedance",
    sortable: true,
    filter: true,
    minWidth: 150,
    flex: 1.5,
    valueGetter: (params) => {
      if (!params.data.assessment_threshold_exceedance) return null;
      const option = exceedanceOptions.value.find((opt) => opt.value === params.data.assessment_threshold_exceedance);
      return option ? option.text : params.data.assessment_threshold_exceedance;
    }
  }
]);

onMounted(async () => {
  years.value = await Service.years();
  exceedanceOptions.value = await Service.getExceedanceOptions();
  documentOptions.value = await Service.getDocumentOptions();
  if (years.value.length > 0) {
    selectedYear.value = years.value[0];
    await showData();
  }
});

const showData = async () => {
  if (!selectedYear.value) {
    Eventy.showHideMessage("Please select a year", "error", 3000);
    return;
  }

  try {
    loading.value = true;
    data.value = [];
    Eventy.showMessage("Loading assessment regime zones...", "loading");
    data.value = await Service.get({ year: parseInt(selectedYear.value) });
    Eventy.hideMessage();

    if (data.value.length === 0) {
      Eventy.showHideMessage("No zone × objective combinations found", "warning", 3000);
    } else {
      Eventy.showHideMessage(`Loaded ${data.value.length} combinations`, "success", 3000);
    }
  } catch (error) {
    console.error("Error loading assessment regime zones:", error);
    Eventy.showHideMessage("Error loading data", "error", 5000);
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <common-layout>
    <c-menu ref="menuRef" @on-click="onMenuClick">
      <template #default="{ handleAction }">
        <div class="px-2 py-2">
          <div class="text-xs font-bold mb-1">Threshold exceedance:</div>
          <select v-model="selectedThreshold" class="select w-full text-sm" @click.stop>
            <option value="">-- Select threshold --</option>
            <option v-for="option in exceedanceOptions" :key="option.value" :value="option.value">
              {{ option.text }}
            </option>
          </select>
        </div>

        <div class="px-2 py-4">
          <div class="text-xs font-bold mb-1">Classification document:</div>
          <select v-model="selectedReportId" class="select w-full text-sm" @click.stop>
            <option value="">-- Select document --</option>
            <option v-for="doc in documentOptions" :key="doc.value" :value="doc.value">
              {{ doc.text }}
            </option>
          </select>
        </div>

        <div class="border-t border-nord4 mt-1 pt-4 px-2 pb-2 flex gap-2">
          <button
            class="button button-sm flex-1"
            @click="
              (e) => {
                e.stopPropagation();
                handleAction('clear');
              }
            "
          >
            Clear Rows
          </button>
          <button
            class="button button-sm button-primary flex-1"
            @click="
              (e) => {
                e.stopPropagation();
                handleAction('update');
              }
            "
          >
            Update Rows
          </button>
        </div>
      </template>
    </c-menu>

    <tool-bar title="Assessment Regime Zones" :show-column-picker="false" :show-add="false" :show-download="false" :show-filter="false" />

    <container>
      <div class="flex gap-2 items-end">
        <div>
          <div class="font-bold">Classification Year</div>
          <select class="select w-48" v-model="selectedYear" :disabled="loading">
            <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
          </select>
        </div>
        <div>
          <button class="button" @click="showData" :disabled="loading">
            <span v-if="loading">Loading...</span>
            <span v-else>Load Data</span>
          </button>
        </div>
      </div>

      <div v-if="data.length > 0" class="mt-4 text-sm text-gray-600">Select rows and right-click to set threshold exceedance and classification document.</div>

      <div v-if="data.length === 0 && !loading" class="mt-4 text-sm text-gray-600">
        <div class="font-bold mb-2">Instructions:</div>
        <ol class="list-decimal list-inside space-y-1">
          <li>Select a classification year</li>
          <li>Click "Load Data" to see all combinations</li>
          <li>Right-click rows to set threshold exceedance and classification report</li>
          <li>Select multiple rows with checkboxes for bulk updates</li>
          <li>Click "Save Changes" to store the data</li>
        </ol>
      </div>
    </container>

    <div class="w-full h-full text-xs mt-8">
      <DataTable :data="data" :columns="columns" :filter="true" :floating-filter="false" :getRowId="getRowId" selectionMode="multiRow" @grid-ready="onGridReady" @on-right-click="onContextMenu" />
    </div>
  </common-layout>
</template>
