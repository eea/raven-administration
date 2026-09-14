<script setup>
import { ref, onMounted, watch } from "vue";
import Service from "./service";
import Eventy from "../../../helpers/eventy";
import CommonLayout from "../../../components/CommonLayout.vue";
import ToolBar from "../../../components/ToolBar.vue";
import Container from "../../../components/Container.vue";
import IconDownload from "~icons/material-symbols/download";

const isDownloading = ref(false);
const downloadingKey = ref(null);
const isLoading = ref(true);
const selectedYear = ref(null);
const yearOptions = ref([]);
const tables = ref([]);
// Filenames the last ZIP exported with a header row and no data.
const emptyFiles = ref(new Set());
// What is marked for EEA reporting versus what can actually be expressed in AQR3.
// Since reporting scope became an explicit decision, a station or series that is
// marked for reporting but has no EoI code, no EEA pollutant, no unit or no time
// resolution is a discrepancy rather than an ordinary omission -- and a submission
// missing something you meant to report is the expensive kind of mistake.
const scope = ref(null);

onMounted(async () => {
  try {
    isLoading.value = true;
    const [years, registry, reportingScope] = await Promise.all([
      Service.getAvailableYears(),
      Service.tables(),
      // Informational, so a failure here must not stop the export list rendering.
      Service.scope().catch(() => null)
    ]);
    scope.value = reportingScope;
    yearOptions.value = years;
    const lastYear = new Date().getFullYear() - 1;
    selectedYear.value = years.includes(lastYear) ? lastYear : years[0] ?? null;
    tables.value = registry;
  } catch {
    const y = new Date().getFullYear();
    yearOptions.value = [y];
    selectedYear.value = y;
  } finally {
    isLoading.value = false;
  }
});

// Which tables are empty is answered per year, so the markers must not survive a
// change of year — they would then describe a different export than the one shown.
watch(selectedYear, () => {
  emptyFiles.value = new Set();
});

const download = async (table) => {
  isDownloading.value = true;
  downloadingKey.value = table.code;
  const filename = table.year_dependent
    ? `${table.name}_${selectedYear.value}.csv`
    : table.filename;
  Eventy.showMessage(`Downloading ${filename}...`, "loading");
  try {
    await Service.downloadTable(table.code, table.year_dependent ? selectedYear.value : null);
    Eventy.hideMessage();
  } catch {
    // error shown by request helper
  } finally {
    isDownloading.value = false;
    downloadingKey.value = null;
  }
};

const recalculate = async () => {
  isDownloading.value = true;
  downloadingKey.value = "recalc";
  Eventy.showMessage(`Recalculating compliance for ${selectedYear.value}...`, "loading");
  try {
    const summary = await Service.recalculateCompliance(selectedYear.value);
    // Nothing stored is not success — the backend explains why in `message`.
    if (summary.message) {
      Eventy.showMessage(summary.message, "warning");
      return;
    }
    const skipped = summary.skipped_total
      ? ` ${summary.skipped_total} skipped (incomplete assessment regime).`
      : "";
    Eventy.showMessage(
      `ComplianceAssessmentMethod: ${summary.written} row(s) stored for ${summary.reporting_year}.${skipped}`,
      "success"
    );
  } catch {
    // error shown by request helper
  } finally {
    isDownloading.value = false;
    downloadingKey.value = null;
  }
};

const downloadAll = async () => {
  isDownloading.value = true;
  downloadingKey.value = "all";
  Eventy.showMessage("Creating ZIP file with all exports. Please wait...", "loading");
  try {
    const response = await Service.downloadAll(selectedYear.value);

    // Every table is exported now, so a file in the ZIP does not mean it has
    // data. Mark the header-only ones in the list and summarise the split.
    const header = response?.headers?.["x-aqr3-empty"] ?? "";
    emptyFiles.value = new Set(header.split(",").filter(Boolean));

    const total = tables.value.length;
    const blank = emptyFiles.value.size;
    if (blank) {
      Eventy.showMessage(
        `Exported ${total - blank} of ${total} tables with data. ` +
          `${blank} exported as headers only — marked "empty" below.`,
        "warning"
      );
    } else {
      Eventy.hideMessage();
    }
  } catch {
    // error shown by request helper
  } finally {
    isDownloading.value = false;
    downloadingKey.value = null;
  }
};
</script>

<template>
  <common-layout>
    <tool-bar title="Dataflow Export" :show-filter="false" :show-add="false" :show-download="false" />

    <container>
      <!-- Year selector + Download All -->
      <div class="flex items-center gap-4 mb-6">
        <div class="font-bold">Reporting Year</div>
        <select v-model="selectedYear" class="select" :disabled="isDownloading || isLoading">
          <option v-if="isLoading" disabled>Loading...</option>
          <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}</option>
        </select>
        <div class="text-nord3 text-sm">Reportnet3 schema v5.02</div>
        <button class="button ml-auto" @click="recalculate" :disabled="isDownloading || isLoading"
          title="ComplianceAssessmentMethod is derived from the exceedance calculation — refresh it before exporting">
          {{ downloadingKey === "recalc" ? "Recalculating..." : "Recalculate compliance" }}
        </button>
        <button class="button flex items-center gap-2" @click="downloadAll" :disabled="isDownloading || isLoading">
          <IconDownload class="text-base" />
          {{ downloadingKey === "all" ? "Creating ZIP..." : "Download all (ZIP)" }}
        </button>
      </div>

      <!-- Marked for reporting but not expressible in AQR3. Only rendered when
           there is something to say; a clean instance sees nothing. -->
      <div v-if="scope && (scope.stations.in_scope !== scope.stations.exported
                           || scope.sampling_points.in_scope !== scope.sampling_points.exported)"
        class="mb-6 p-3 rounded border border-nord13 bg-nord13/10 text-sm">
        <div class="font-bold mb-1">Marked for EEA reporting, but not exported</div>
        <div v-if="scope.stations.in_scope !== scope.stations.exported" class="text-nord3">
          {{ scope.stations.in_scope - scope.stations.exported }} of
          {{ scope.stations.in_scope }} stations have no EoI code, so AQR3 cannot name them.
          <span v-if="scope.stations.without_eoi_code.length" class="text-nord3">
            {{ scope.stations.without_eoi_code.map((s) => s.name).join(", ") }}
          </span>
        </div>
        <div v-if="scope.sampling_points.in_scope !== scope.sampling_points.exported" class="text-nord3">
          {{ scope.sampling_points.in_scope - scope.sampling_points.exported }} of
          {{ scope.sampling_points.in_scope }} sampling points are missing an EEA pollutant,
          unit or time resolution.
        </div>
        <div class="text-nord3 mt-1 text-xs">
          Either give them what they are missing, or switch EEA Reporting off for them on the
          Stations and Sampling Points pages.
        </div>
      </div>

      <!-- Exports table, driven by the AQR3 registry -->
      <table class="w-full text-sm border-collapse">
        <thead>
          <tr class="border-b border-nord4 text-left text-nord3">
            <th class="py-2 pr-4 font-semibold w-16">Code</th>
            <th class="py-2 pr-4 font-semibold w-64">File</th>
            <th class="py-2 font-semibold">Description</th>
            <th class="py-2 w-12"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="isLoading">
            <td colspan="4" class="py-4 text-nord3">Loading reporting tables...</td>
          </tr>
          <tr v-for="table in tables" :key="table.code" class="border-b border-nord6 hover:bg-nord6/50">
            <td class="py-2 pr-4 font-mono text-nord3">{{ table.code }}</td>
            <td class="py-2 pr-4 font-medium">
              {{ table.name }}<span v-if="table.year_dependent" class="text-nord3 font-normal">_{{ selectedYear }}</span>.csv
              <span v-if="emptyFiles.has(table.filename)"
                class="ml-2 px-1.5 py-0.5 rounded text-xs font-normal bg-nord13/40 text-nord3"
                title="Exported with a header row but no records">empty</span>
            </td>
            <td class="py-2 text-nord3">{{ table.description }}</td>
            <td class="py-2 text-right">
              <button class="button py-1 px-2 flex items-center gap-1 ml-auto"
                @click="download(table)"
                :disabled="isDownloading"
                :title="`Download ${table.filename}`">
                <IconDownload class="text-base" />
                <span v-if="downloadingKey === table.code" class="text-xs">...</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </container>
  </common-layout>
</template>
