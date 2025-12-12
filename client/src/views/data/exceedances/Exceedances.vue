<script setup>
import IconInfo from "~icons/ph/info-duotone";
import Container from "../../../components/Container.vue";
import { onMounted, computed, watch } from "vue";
import Service from "./service";
import { columns } from "./datatable";

const years = ref([]);
const directives = ref([]);
const pollutants = ref([]);

const selectedYear = ref("");
const selectedDirective = ref("");
const selectedPollutant = ref("");

const cols = ref(columns);
const data = ref([]);
const loading = ref(false);

// Summary statistics
const summary = computed(() => {
  if (!data.value || data.value.length === 0) {
    return {
      total: 0,
      exceeded: 0,
      compliant: 0
    };
  }

  return {
    total: data.value.length,
    exceeded: data.value.filter(d => d.exceeded).length,
    compliant: data.value.filter(d => !d.exceeded).length
  };
});

// Watch for directive changes and reload pollutants
watch(selectedDirective, async (newDirective) => {
  if (newDirective) {
    pollutants.value = await Service.pollutants(newDirective);
    // Select first pollutant by default
    if (pollutants.value.length > 0) {
      selectedPollutant.value = pollutants.value[0].notation;
    }
  }
});

onMounted(async () => {
  data.value = [];
  
  // Load years
  years.value = await Service.years();
  console.log('Years loaded:', years.value);
  if (years.value.length > 0) {
    selectedYear.value = years.value[0];
    console.log('Selected year:', selectedYear.value);
  }

  // Load directives
  directives.value = await Service.directives();
  console.log('Directives loaded:', directives.value);
  if (directives.value.length > 0) {
    // Default to 2024/2881 directive if available, otherwise first one
    const directive2024 = directives.value.find(d => d.id === "2024/2881");
    selectedDirective.value = directive2024 ? directive2024.id : directives.value[0].id;
    console.log('Selected directive:', selectedDirective.value);
  }
});

const evaluateExceedances = async () => {
  if (!selectedYear.value || !selectedPollutant.value || !selectedDirective.value) {
    return;
  }

  loading.value = true;
  data.value = [];

  try {
    const requestData = {
      year: parseInt(selectedYear.value),
      pollutant: selectedPollutant.value,
      directive: selectedDirective.value
    };

    data.value = await Service.evaluate(requestData);
    console.log("Exceedances data:", data.value);
  } catch (error) {
    console.error("Error evaluating exceedances:", error);
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <common-layout>
    <tool-bar 
      title="Exceedances" 
      :show-column-picker="false" 
      :show-add="false" 
      :show-download="false" 
      :show-filter="false" 
    />

    <container>
      <div class="flex gap-2 flex-wrap">
        <div>
          <div class="font-bold">Year</div>
          <n-select class="!w-48" v-model="selectedYear">
            <n-option 
              v-for="year in years" 
              :key="year" 
              :value="year" 
              :label="year.toString()" 
            />
          </n-select>
        </div>
        
        <div>
          <div class="font-bold">Directive</div>
          <n-select class="!w-56" v-model="selectedDirective">
            <n-option 
              v-for="directive in directives" 
              :key="directive.id" 
              :value="directive.id" 
              :label="directive.label" 
            />
          </n-select>
        </div>

        <div>
          <div class="font-bold">Pollutant</div>
          <n-select class="!w-48" v-model="selectedPollutant">
            <n-option 
              v-for="pollutant in pollutants" 
              :key="pollutant.notation" 
              :value="pollutant.notation" 
              :label="pollutant.notation" 
            />
          </n-select>
        </div>

        <div>
          <div>&nbsp;</div>
          <button class="n-button" @click="evaluateExceedances" :disabled="loading">
            {{ loading ? 'Evaluating...' : 'Evaluate Exceedances' }}
          </button>
        </div>
      </div>

      <div v-if="data.length > 0" class="mt-4 flex gap-4 text-sm">
        <div class="flex items-center gap-2">
          <span class="font-bold">Summary:</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-red-500"></span>
          <span>{{ summary.exceeded }} Exceeded</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-green-500"></span>
          <span>{{ summary.compliant }} Compliant</span>
        </div>
        <div class="text-gray-600">
          (Total: {{ summary.total }} assessments)
        </div>
      </div>

      <div class="text-sm flex gap-1 mt-4 items-start">
        <icon-info class="text-blue-500 mt-0.5" />
        <div class="text-gray-700">
          <p class="mb-1">
            <strong>Exceedances</strong> occur when measured air quality values exceed regulatory thresholds 
            defined in EU Air Quality Directives or WHO guidelines.
          </p>
          <p class="text-xs">
            Select a year, directive, and pollutant to evaluate compliance at all sampling points. 
            Results show whether each threshold has been exceeded based on calculated statistics.
          </p>
        </div>
      </div>
    </container>

    <div class="w-full h-full text-xs mt-8">
      <DataTable 
        :data="data" 
        :columns="cols" 
        :filter="true" 
        :responsive="false" 
        :floating-filter="false" 
        :enableCellTextSelection="true" 
      />
    </div>
  </common-layout>
</template>
