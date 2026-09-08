<script setup>
import { computed, onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Eventy from "../../../helpers/eventy";
import Service from "./service";
import pageOptions from "./pageOptions";

// Rows are derived and are rebuilt by Recalculate compliance on the Dataflow page, so
// this page has no add and no delete -- AQR3 retracts a row with the Deletion flag,
// which is editable. See pageOptions.js for what is and is not editable.

const options = ref({});
const years = ref([]);
const year = ref(null);

// A year is always part of the request: the table holds every calculated year, and
// showing them mixed together would make two rows differing only by year look like
// duplicates. Manager calls service.get() with no arguments, so bind the year here
// and remount on change.
const yearService = computed(() => ({
  ...Service,
  get: async () => (year.value ? Service.get(year.value) : [])
}));

onMounted(async () => {
  let lookups;
  try {
    lookups = await Service.lookups();
  } catch {
    Eventy.showHideMessage("Failed to load lookups.", "error", 4000);
    return;
  }
  years.value = lookups.years ?? [];
  year.value = years.value[0] ?? null;
  options.value = pageOptions(lookups);
});
</script>

<template>
  <Manager
    :key="year"
    name="Compliance assessment method"
    :options="options"
    :service="yearService"
    :show-add-button="false"
    :show-delete-button="false"
    :show-download-button="false"
  >
    <template #toolbar>
      <select v-if="years.length" v-model="year" class="select ml-3 self-center text-sm">
        <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
      </select>
      <div v-else class="ml-3 self-center text-xs text-nord3">
        No compliance calculated yet — use <em>Recalculate compliance</em> on the Dataflow page.
      </div>
    </template>
  </Manager>
</template>
