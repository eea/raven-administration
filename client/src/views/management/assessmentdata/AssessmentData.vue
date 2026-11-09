<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import Manager from "../../../components/n-manager/Manager.vue";
import CircleHover from "../../../components/CircleHover.vue";
import Service from "./service";
import AssessmentDataCrud from "./AssessmentDataCrud.vue";
import GenerateAssessmentData from "./GenerateAssessmentData.vue";
import pageOptions from "./pageOptions";
import IconGenerate from "~icons/material-symbols/wand-stars";

// Which assessment methods assess which assessment regime. Not an AQR3 table of its
// own -- it is the junction ComplianceAssessmentMethod is derived from, so until this
// page existed a fresh Raven v4 install could build zones, sampling points and
// assessment regimes and still export an empty CAM.
//
// Its own form, because the assessment type decides whether the method is a sampling
// point, a MOD_ model or an OBE_ one (methodKind.js). The wand opens step 2 of the
// assessment setup wizard, which links the sampling points inside each regime's zone.

const route = useRoute();
const options = ref({});
const showGenerate = ref(false);
const wizardYear = ref(Number(route.query.year) || null);
// Remount Manager after linking so its row set reloads.
const dataVersion = ref(0);

onMounted(async () => {
  const lookups = await Service.lookups();
  options.value = pageOptions(lookups);
  if (route.query.wizard) showGenerate.value = true;
});
</script>

<template>
  <generate-assessment-data :show="showGenerate" :initial-year="wizardYear"
                            @close="showGenerate = false" @linked="dataVersion++" />

  <Manager :key="dataVersion" name="Assessment data" :options="options" :service="Service"
           :crud-component="AssessmentDataCrud">
    <template #toolbar>
      <CircleHover class="ml-1 self-center" title="Link sampling points by zone (wizard, step 2 of 3)"
                   @click="showGenerate = true">
        <icon-generate class="text-nord10 text-base self-center" />
      </CircleHover>
    </template>
  </Manager>
</template>
