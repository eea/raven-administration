<script setup>
import { onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import GenerateRegimes from "./GenerateRegimes.vue";
import CircleHover from "../../../components/CircleHover.vue";
import Service from "./service";
import pageOptions from "./pageOptions";
import IconGenerate from "~icons/material-symbols/table-rows-narrow";

// AQR3 calls this table AssessmentRegimeZone (ARZ), which is why the page is titled
// that way while the module keeps the shorter name. A second, unrelated table
// `assessmentregime_zones` used to hold this menu slot; it could not express ARZ and
// nothing exported it, so migration 020 dropped it. Its bulk fill lives on in
// GenerateRegimes.vue, writing real regimes.

const options = ref({});
const showGenerate = ref(false);
// Remount Manager after a generate so its row set reloads.
const dataVersion = ref(0);

onMounted(async () => {
  const lookups = await Service.lookups();
  options.value = pageOptions(lookups);
});
</script>

<template>
  <generate-regimes :show="showGenerate" :lookups="options.lookups ?? {}"
                    @close="showGenerate = false" @generated="dataVersion++" />

  <Manager :key="dataVersion" name="Assessment regime zones" :options="options" :service="Service"
           :show-download-button="false">
    <template #toolbar>
      <CircleHover class="ml-1 self-center" title="Generate regimes for a year"
                   @click="showGenerate = true">
        <icon-generate class="text-nord10 text-base self-center" />
      </CircleHover>
    </template>
  </Manager>
</template>
