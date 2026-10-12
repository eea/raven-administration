<script setup>
import { onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Service from "./service";
import AssessmentDataCrud from "./AssessmentDataCrud.vue";
import pageOptions from "./pageOptions";

// Which assessment methods assess which assessment regime. Not an AQR3 table of its
// own -- it is the junction ComplianceAssessmentMethod is derived from, so until this
// page existed a fresh Raven v4 install could build zones, sampling points and
// assessment regimes and still export an empty CAM.
//
// Its own form, because the assessment type decides whether the method is a sampling
// point, a MOD_ model or an OBE_ one (methodKind.js).

const options = ref({});

onMounted(async () => {
  const lookups = await Service.lookups();
  options.value = pageOptions(lookups);
});
</script>

<template>
  <Manager name="Assessment data" :options="options" :service="Service" :crud-component="AssessmentDataCrud" />
</template>
