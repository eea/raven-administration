<script setup>
import { ref, onMounted } from "vue";
import Service from "./service";
import Eventy from "../../../helpers/eventy";
import CommonLayout from "../../../components/CommonLayout.vue";
import ToolBar from "../../../components/ToolBar.vue";
import Container from "../../../components/Container.vue";
import IconDownload from "~icons/material-symbols/download";

const isDownloading = ref(false);
const downloadingKey = ref(null);
const isLoadingYears = ref(true);
const selectedYear = ref(null);
const yearOptions = ref([]);

onMounted(async () => {
  try {
    isLoadingYears.value = true;
    const years = await Service.getAvailableYears();
    yearOptions.value = years;
    const lastYear = new Date().getFullYear() - 1;
    selectedYear.value = years.includes(lastYear) ? lastYear : years[0] ?? null;
  } catch {
    const y = new Date().getFullYear();
    yearOptions.value = [y];
    selectedYear.value = y;
  } finally {
    isLoadingYears.value = false;
  }
});

const exports = [
  { key: "authorities",               label: "Authority",               description: "Contact details of responsible authorities and their area of responsibility.",                                                          fn: () => Service.downloadAuthorities() },
  { key: "stations",                  label: "Station",                 description: "Air quality measuring stations — EoI codes, names, networks and operating time zones.",                                                  fn: () => Service.downloadStations() },
  { key: "samplingpoints",            label: "SamplingPoint",           description: "Air quality sampling locations — identifiers, coordinates and area/location characteristics.",                                           fn: () => Service.downloadSamplingPoints() },
  { key: "processes",                 label: "SamplingPointProcess",    description: "Measurement techniques and methodologies — equipment configuration, quality information and operational periods.",                        fn: () => Service.downloadProcesses() },
  { key: "measurements",              label: "MeasurementResult",       description: "Air quality measurement values with time reference for the selected year, linked to sampling points.",                                    fn: () => Service.downloadMeasurements(selectedYear.value), yearDependent: true },
  { key: "zonegeometry",              label: "ZoneGeometry",            description: "Air quality zone boundaries reported as GeoJSON geometries.",                                                                            fn: () => Service.downloadZoneGeometry() },
  { key: "spatialrepresentativeness", label: "SpatialRepresentativeness", description: "Links the spatial representativeness area of a sampling point or exceedance extent to the compliance assessment method.",             fn: () => Service.downloadSpatialRepresentativeness() },
  { key: "srareainline",              label: "SRAreaInline",            description: "Representativeness area as a set of EPSG:3035 grid cells for each sampling point declared for compliance assessments.",                  fn: () => Service.downloadSrAreaInline() },
];

const download = async (exp) => {
  isDownloading.value = true;
  downloadingKey.value = exp.key;
  const filename = exp.yearDependent ? `${exp.label}_${selectedYear.value}.csv` : `${exp.label}.csv`;
  Eventy.showMessage(`Downloading ${filename}...`, "loading");
  try {
    await exp.fn();
    Eventy.hideMessage();
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
    await Service.downloadAll(selectedYear.value);
    Eventy.hideMessage();
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
    <tool-bar title="Dataflow Export" :show-filter="false" :show-add="false" :show-column-picker="false" :show-download="false" />

    <container>
      <!-- Year selector + Download All -->
      <div class="flex items-center gap-4 mb-6">
        <div class="font-bold">Reporting Year</div>
        <select v-model="selectedYear" class="select" :disabled="isDownloading || isLoadingYears">
          <option v-if="isLoadingYears" disabled>Loading...</option>
          <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}</option>
        </select>
        <button class="button flex items-center gap-2 ml-auto" @click="downloadAll" :disabled="isDownloading">
          <IconDownload class="text-base" />
          {{ downloadingKey === "all" ? "Creating ZIP..." : "Download all (ZIP)" }}
        </button>
      </div>

      <!-- Exports table -->
      <table class="w-full text-sm border-collapse">
        <thead>
          <tr class="border-b border-nord4 text-left text-nord3">
            <th class="py-2 pr-4 font-semibold w-56">File</th>
            <th class="py-2 font-semibold">Description</th>
            <th class="py-2 w-12"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="exp in exports" :key="exp.key" class="border-b border-nord6 hover:bg-nord6/50">
            <td class="py-2 pr-4 font-medium">
              {{ exp.label }}<span v-if="exp.yearDependent" class="text-nord3 font-normal">_{{ selectedYear }}</span>.csv
            </td>
            <td class="py-2 text-nord3">{{ exp.description }}</td>
            <td class="py-2 text-right">
              <button class="button py-1 px-2 flex items-center gap-1 ml-auto"
                @click="download(exp)"
                :disabled="isDownloading"
                :title="`Download ${exp.label}.csv`">
                <IconDownload class="text-base" />
                <span v-if="downloadingKey === exp.key" class="text-xs">...</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </container>
  </common-layout>
</template>