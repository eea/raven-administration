<script setup>
import Service from "./service";
import pageOptions from "./pageOptions";
import Crud from "./Crud.vue";
import Eventy from "../../../helpers/eventy";

const options = ref({});

onMounted(async () => {
  Eventy.showMessage("Loading metadata", "loading");
  const zones = await Service.zones();
  const pollutants = await Service.pollutants();
  const assessment_types = await Service.assessment_types();
  const object_types = await Service.object_types();
  const reporting_metrics = await Service.reporting_metrics();
  const protection_targets = await Service.protection_targets();
  const exceedances = await Service.exceedances();
  const sampling_points = await Service.sampling_points();
  Eventy.hideMessage();

  options.value = pageOptions({ zones, pollutants, assessment_types, object_types, reporting_metrics, protection_targets, exceedances, sampling_points });
});
</script>

<template>
  <manager name="Assessment regimes" :options="options" :service="Service" :crud-component="Crud" :is-two-file-upload="true" />
</template>
