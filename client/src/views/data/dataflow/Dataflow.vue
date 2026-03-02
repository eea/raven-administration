<script setup>
import { ref, onMounted } from "vue";
import Service from "./service";
import Eventy from "../../../helpers/eventy";
import CommonLayout from "../../../components/CommonLayout.vue";
import ToolBar from "../../../components/ToolBar.vue";
import Container from "../../../components/Container.vue";

const isDownloading = ref(false);
const isLoadingYears = ref(true);
const selectedYear = ref(null);
const yearOptions = ref([]);

onMounted(async () => {
  try {
    isLoadingYears.value = true;
    const years = await Service.getAvailableYears();
    yearOptions.value = years;

    // Default to last year (previous year from current)
    const currentYear = new Date().getFullYear();
    const lastYear = currentYear - 1;

    if (years.includes(lastYear)) {
      selectedYear.value = lastYear;
    } else if (years.length > 0) {
      // If last year not available, use the most recent year
      selectedYear.value = years[0];
    }
  } catch (error) {
    console.error("Failed to load available years:", error);
    // Fallback to current year if API fails
    const currentYear = new Date().getFullYear();
    yearOptions.value = [currentYear];
    selectedYear.value = currentYear;
  } finally {
    isLoadingYears.value = false;
  }
});

const downloadAuthorities = async () => {
  try {
    isDownloading.value = true;
    Eventy.showMessage("Downloading Authority.csv...", "loading");
    await Service.downloadAuthorities();
    Eventy.hideMessage();
  } catch (error) {
    // Error already displayed by Request helper
    console.error("Download failed:", error);
  } finally {
    isDownloading.value = false;
  }
};

const downloadStations = async () => {
  try {
    isDownloading.value = true;
    Eventy.showMessage("Downloading Station.csv...", "loading");
    await Service.downloadStations();
    Eventy.hideMessage();
  } catch (error) {
    // Error already displayed by Request helper
    console.error("Download failed:", error);
  } finally {
    isDownloading.value = false;
  }
};

const downloadSamplingPoints = async () => {
  try {
    isDownloading.value = true;
    Eventy.showMessage("Downloading SamplingPoint.csv...", "loading");
    await Service.downloadSamplingPoints();
    Eventy.hideMessage();
  } catch (error) {
    // Error already displayed by Request helper
    console.error("Download failed:", error);
  } finally {
    isDownloading.value = false;
  }
};

const downloadProcesses = async () => {
  try {
    isDownloading.value = true;
    Eventy.showMessage("Downloading SamplingPointProcess.csv...", "loading");
    await Service.downloadProcesses();
    Eventy.hideMessage();
  } catch (error) {
    // Error already displayed by Request helper
    console.error("Download failed:", error);
  } finally {
    isDownloading.value = false;
  }
};

const downloadMeasurements = async () => {
  try {
    isDownloading.value = true;
    Eventy.showMessage(`Downloading MeasurementResult for ${selectedYear.value}...`, "loading");
    await Service.downloadMeasurements(selectedYear.value);
    Eventy.hideMessage();
  } catch (error) {
    // Error already displayed by Request helper
    console.error("Download failed:", error);
  } finally {
    isDownloading.value = false;
  }
};

const downloadZoneGeometry = async () => {
  try {
    isDownloading.value = true;
    Eventy.showMessage("Downloading ZoneGeometry.csv...", "loading");
    await Service.downloadZoneGeometry();
    Eventy.hideMessage();
  } catch (error) {
    // Error already displayed by Request helper
    console.error("Download failed:", error);
  } finally {
    isDownloading.value = false;
  }
};

const downloadAll = async () => {
  try {
    isDownloading.value = true;
    Eventy.showMessage("Creating ZIP file with all exports. Please wait...", "loading");
    await Service.downloadAll(selectedYear.value);
    Eventy.hideMessage();
  } catch (error) {
    // Error already displayed by Request helper
    console.error("Download failed:", error);
  } finally {
    isDownloading.value = false;
  }
};
</script>

<template>
  <common-layout>
    <tool-bar title="Dataflow Export" :show-filter="false" :show-add="false" :show-column-picker="false" :show-download="false" />

    <container>
      <!-- Year Selection -->
      <div class="mb-6">
        <div class="font-bold text-base mb-3">Reporting Year</div>
        <select v-model="selectedYear" class="border border-gray-300 rounded px-3 py-2 w-48" :disabled="isDownloading || isLoadingYears">
          <option v-if="isLoadingYears" disabled>Loading years...</option>
          <option v-for="year in yearOptions" :key="year" :value="year">
            {{ year }}
          </option>
        </select>
        <div class="text-xs text-gray-600 mt-1">Years are based on available data in sampling points</div>
      </div>

      <div class="mb-6">
        <div class="font-bold text-base mb-3">Individual Exports</div>
        <div class="flex flex-wrap gap-3">
          <button class="button" @click="downloadAuthorities" :disabled="isDownloading">Download Authority.csv</button>
          <button class="button" @click="downloadStations" :disabled="isDownloading">Download Station.csv</button>
          <button class="button" @click="downloadSamplingPoints" :disabled="isDownloading">Download SamplingPoint.csv</button>
          <button class="button" @click="downloadProcesses" :disabled="isDownloading">Download SamplingPointProcess.csv</button>
          <button class="button" @click="downloadMeasurements" :disabled="isDownloading">Download MeasurementResult ({{ selectedYear }}).csv</button>
          <button class="button" @click="downloadZoneGeometry" :disabled="isDownloading">Download ZoneGeometry.csv</button>
        </div>
      </div>

      <div class="border-t pt-6 mb-6">
        <div class="font-bold text-base mb-3">Complete Export</div>
        <div>
          <button class="button bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6" @click="downloadAll" :disabled="isDownloading">Download All (ZIP) - {{ selectedYear }}</button>
          <div class="text-xs text-gray-500 mt-2">Downloads a ZIP file containing all CSV exports including measurements for {{ selectedYear }}</div>
        </div>
      </div>

      <div class="border-t pt-6">
        <div class="font-bold text-sm mb-3">Available Exports:</div>
        <ul class="text-sm space-y-2">
          <li class="flex items-center gap-2">
            <span class="text-green-600 font-bold">✓</span>
            <span>
              <strong>Authority</strong>
              - Contact information for authorities
            </span>
          </li>
          <li class="flex items-center gap-2">
            <span class="text-green-600 font-bold">✓</span>
            <span>
              <strong>Station</strong>
              - Station metadata and location
            </span>
          </li>
          <li class="flex items-center gap-2">
            <span class="text-green-600 font-bold">✓</span>
            <span>
              <strong>SamplingPoint</strong>
              - Sampling point configuration
            </span>
          </li>
          <li class="flex items-center gap-2">
            <span class="text-green-600 font-bold">✓</span>
            <span>
              <strong>SamplingPointProcess</strong>
              - Process information
            </span>
          </li>
          <li class="flex items-center gap-2">
            <span class="text-green-600 font-bold">✓</span>
            <span>
              <strong>MeasurementResult</strong>
              - Observation data for selected year
            </span>
          </li>
          <li class="flex items-center gap-2">
            <span class="text-green-600 font-bold">✓</span>
            <span>
              <strong>ZoneGeometry</strong>
              - Geographic zone boundaries (GeoJSON)
            </span>
          </li>
        </ul>
      </div>
    </container>
  </common-layout>
</template>

<style scoped>
.button:disabled {
  cursor: not-allowed;
}
</style>
