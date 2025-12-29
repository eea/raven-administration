<script setup>
import IconLink from "~icons/ph/link-simple-duotone";
import Container from "../../../components/Container.vue";
import { onMounted, computed, watch } from "vue";
import Service from "./service";
import { columns } from "./datatable";

const years = ref([]);
const pollutantsAndAggregationProcess = ref([]);

const selectedYears = ref([]);  // Changed from selectedYear to support multi-select
const selectedPollutant = ref("");
const selectedAggregationProcess = ref("");

const cols = ref(columns);
const data = ref([]);

// Computed property to get unique pollutants from pollutantsAndAggregationProcess
const availablePollutants = computed(() => {
  if (!pollutantsAndAggregationProcess.value) {
    return [];
  }

  return pollutantsAndAggregationProcess.value.map((item) => item.pollutant);
});

// Computed property to get available aggregation processes for selected pollutant
const availableAggregationProcesses = computed(() => {
  if (!selectedPollutant.value || !pollutantsAndAggregationProcess.value) {
    return [];
  }

  const found = pollutantsAndAggregationProcess.value.find((item) => item.pollutant === selectedPollutant.value);

  if (!found || !found.ap_with_directives) {
    return [];
  }

  // Extract just the aggregation process names (first element of each inner array)
  return found.ap_with_directives.map((ap) => ap[0]);
});

// Computed property to get directive information for selected aggregation process
const currentDirectiveInfo = computed(() => {
  if (!selectedPollutant.value || !selectedAggregationProcess.value || !pollutantsAndAggregationProcess.value) {
    return null;
  }

  const found = pollutantsAndAggregationProcess.value.find((item) => item.pollutant === selectedPollutant.value);

  if (!found || !found.ap_with_directives) {
    return null;
  }

  const apInfo = found.ap_with_directives.find((ap) => ap[0] === selectedAggregationProcess.value);

  if (!apInfo) {
    return null;
  }

  return {
    directive1: apInfo[1] === "true",
    directive2: apInfo[2] === "true"
  };
});

// Watch for pollutant changes and keep aggregation process if available, reset if not
watch(selectedPollutant, (newPollutant) => {
  if (newPollutant && availableAggregationProcesses.value.length > 0) {
    // Check if current aggregation process is available for the new pollutant
    if (selectedAggregationProcess.value && availableAggregationProcesses.value.includes(selectedAggregationProcess.value)) {
      // Keep the current aggregation process if it exists in the new pollutant's options
      return;
    } else {
      // Reset to first available option if current one doesn't exist
      selectedAggregationProcess.value = availableAggregationProcesses.value[0];
    }
  } else {
    selectedAggregationProcess.value = "";
  }
});

onMounted(async () => {
  data.value = [];
  years.value = await Service.years();
  selectedYears.value = [years.value[0]];  // Initialize with first year as array
  console.log(years.value);

  pollutantsAndAggregationProcess.value = await Service.pollutants_and_aggregationprocess();
  console.log(pollutantsAndAggregationProcess.value);

  // Set initial pollutant from the first item in pollutantsAndAggregationProcess
  if (availablePollutants.value.length > 0) {
    selectedPollutant.value = availablePollutants.value[0];
  }

  // Set initial aggregation process based on first pollutant
  if (availableAggregationProcesses.value.length > 0) {
    selectedAggregationProcess.value = availableAggregationProcesses.value[0];
  }
});

const showValues = async () => {
  data.value = [];
  
  const requestData = {
    years: selectedYears.value.map(y => parseInt(y)),  // Send array of years
    pollutant: selectedPollutant.value,
    aggregation_process: selectedAggregationProcess.value
  };

  data.value = await Service.get(requestData);
  console.log(data.value);
};

const exportToCSV = () => {
  if (data.value.length === 0) {
    alert("No data to export. Please show statistics first.");
    return;
  }

  // Get column headers
  const headers = cols.value.map(col => col.headerName);
  const fields = cols.value.map(col => col.field);

  // Build CSV content
  let csvContent = headers.join(",") + "\n";
  
  data.value.forEach(row => {
    const values = fields.map(field => {
      let value = row[field];
      // Handle null/undefined
      if (value === null || value === undefined) {
        value = "";
      }
      // Escape quotes and wrap in quotes if contains comma
      value = String(value).replace(/"/g, '""');
      if (value.includes(",") || value.includes("\n") || value.includes('"')) {
        value = `"${value}"`;
      }
      return value;
    });
    csvContent += values.join(",") + "\n";
  });

  // Create download link
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
  const filename = `statistics_${selectedPollutant.value}_${selectedAggregationProcess.value}_${timestamp}.csv`;
  
  link.setAttribute("href", url);
  link.setAttribute("download", filename);
  link.style.visibility = "hidden";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
</script>

<template>
  <common-layout>
    <tool-bar title="Statistics" :show-column-picker="false" :show-add="false" :show-download="false" :show-filter="false" />

    <container>
      <div class="flex gap-2">
        <div>
          <div class="font-bold">Years</div>
          <select 
            class="n-select !w-48 px-3 py-2 border rounded" 
            v-model="selectedYears" 
            multiple 
            size="5"
          >
            <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
          </select>
          <div class="text-xs text-gray-500 mt-1">Hold Ctrl/Cmd to select multiple</div>
        </div>
        <div>
          <div class="font-bold">Pollutants</div>
          <n-select class="!w-48" v-model="selectedPollutant">
            <n-option v-for="pollutant in availablePollutants" :key="pollutant" :value="pollutant" :label="pollutant" />
          </n-select>
        </div>
        <div>
          <div class="font-bold">Aggregation Process</div>
          <n-select class="!w-48" v-model="selectedAggregationProcess">
            <n-option v-for="process in availableAggregationProcesses" :key="process" :value="process" :label="process" />
          </n-select>
        </div>
        <div>
          <div>&nbsp;</div>
          <button class="n-button" @click="showValues">Show statistics</button>
        </div>
        <div v-if="data.length > 0">
          <div>&nbsp;</div>
          <button class="n-button" @click="exportToCSV">Download CSV</button>
        </div>
      </div>

      <div v-if="currentDirectiveInfo" class="text-xs flex gap-2">
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full" :class="currentDirectiveInfo.directive1 ? 'bg-green-500' : 'bg-gray-300'"></span>
          <span>Directive 2008/50</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full" :class="currentDirectiveInfo.directive2 ? 'bg-green-500' : 'bg-gray-300'"></span>
          <span>Directive 2024/2881</span>
        </div>
      </div>

      <div class="text-sm flex gap-1 mt-2">
        <icon-link />
        <div><a href="https://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/view" target="_blank">Read more about aggregation processes here</a></div>
      </div>

    </container>

    <div class="w-full h-full text-xs mt-8">
      <DataTable :data="data" :columns="cols" :filter="true" :responsive="false" :floating-filter="false" :enableCellTextSelection="true" />
    </div>
  </common-layout>
</template>
