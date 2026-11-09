<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import Manager from "../../../components/n-manager/Manager.vue";
import CircleHover from "../../../components/CircleHover.vue";
import ComplianceFeedback from "../../../components/ComplianceFeedback.vue";
import Eventy from "../../../helpers/eventy";
import Service from "./service";
import pageOptions from "./pageOptions";
import IconRecalculate from "~icons/material-symbols/wand-stars";

// Rows are derived and are rebuilt by Recalculate compliance -- here, as step 3 of the
// assessment setup wizard, or on the Dataflow page -- so this page has no add and no
// delete; AQR3 retracts a row with the Deletion flag, which is editable. See
// pageOptions.js for what is and is not editable.

const route = useRoute();
const router = useRouter();
const options = ref({});
const years = ref([]);
const year = ref(null);
const recalc = ref(null);
const running = ref(false);
const confirming = ref(false);
// Remount Manager after a recalculation so its row set reloads.
const dataVersion = ref(0);

// A year is always part of the request: the table holds every calculated year, and
// showing them mixed together would make two rows differing only by year look like
// duplicates. Manager calls service.get() with no arguments, so bind the year here
// and remount on change.
const yearService = computed(() => ({
  ...Service,
  get: async () => (year.value ? Service.get(year.value) : [])
}));

// The calculated years, plus the linked year and last year, so a year that has never
// been calculated can still be chosen and calculated.
const yearChoices = computed(() => {
  const linked = Number(route.query.year);
  const all = new Set([...years.value, new Date().getFullYear() - 1]);
  if (linked) all.add(linked);
  return [...all].sort((a, b) => b - a);
});

onMounted(async () => {
  let lookups;
  try {
    lookups = await Service.lookups();
  } catch {
    Eventy.showHideMessage("Failed to load lookups.", "error", 4000);
    return;
  }
  years.value = lookups.years ?? [];
  // ?year= from a link (with ?focus=, which Manager reads), else the latest year.
  const linked = Number(route.query.year);
  year.value = linked || (years.value[0] ?? yearChoices.value[0]);
  options.value = pageOptions(lookups);
  if (route.query.wizard) confirming.value = true;
});

const recalculate = async () => {
  confirming.value = false;
  running.value = true;
  Eventy.showMessage(`Recalculating compliance for ${year.value}...`, "loading");
  try {
    const summary = await Service.recalculate(year.value);
    recalc.value = summary;
    Eventy.hideMessage();
    if (!years.value.includes(year.value)) years.value = [...years.value, year.value];
    dataVersion.value++;
  } catch {
    Eventy.hideMessage();
    // Request already surfaced the server message.
  } finally {
    running.value = false;
  }
};

const back = () => router.push({ name: "AssessmentData", query: { wizard: 1, year: year.value } });
</script>

<template>
  <Manager
    :key="`${year}-${dataVersion}`"
    name="Compliance assessment method"
    :options="options"
    :service="yearService"
    :show-add-button="false"
    :show-delete-button="false"
    :show-download-button="false"
  >
    <template #toolbar>
      <select v-if="yearChoices.length" v-model="year" class="select ml-3 self-center text-sm"
              @change="recalc = null">
        <option v-for="y in yearChoices" :key="y" :value="y">{{ y }}{{ years.includes(y) ? "" : " (not calculated)" }}</option>
      </select>
      <CircleHover class="ml-1 self-center" :title="`Recalculate compliance for ${year} (wizard, step 3 of 3)`"
                   @click="confirming = true">
        <icon-recalculate class="text-nord10 text-base self-center" :class="running ? 'animate-pulse' : ''" />
      </CircleHover>
    </template>
    <template #banner>
      <div v-if="confirming" class="mb-2 p-3 rounded border border-nord13 bg-nord13/20 text-sm flex items-center gap-3">
        <div class="flex-1">
          <strong>Step 3 of 3:</strong> recalculate ComplianceAssessmentMethod for {{ year }} from its assessment
          regimes and their linked sampling points and models. The year's rows are rebuilt; the columns you
          maintain by hand (PollutionLevel, MQI, Deletion and the others editable here) are kept.
        </div>
        <button class="button" @click="back">← Step 2</button>
        <button class="button" :disabled="running" @click="recalculate">Recalculate {{ year }}</button>
        <button class="button" @click="confirming = false">Cancel</button>
      </div>

      <div v-if="recalc">
        <ComplianceFeedback :summary="recalc" @dismiss="recalc = null" />
      </div>
    </template>
  </Manager>
</template>
