<script setup>
import { onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Service from "./service";
import pageOptions from "./pageOptions";
import Crud from "./Crud.vue";
import Eventy from "../../../helpers/eventy";

const options = ref({});

onMounted(async () => {
  Eventy.showMessage("Loading metadata", "loading");
  const attainments = await Service.attainments();
  const exceedance_descriptions = await Service.exceedance_descriptions();
  const exceedance_types = await Service.exceedance_types();
  const area_classifications = await Service.area_classifications();
  const adjustment_types = await Service.adjustment_types();
  const adjustment_source_types = await Service.adjustment_source_types();
  const reasons = await Service.reasons();
  const sampling_points = await Service.sampling_points();
  Eventy.hideMessage();

  options.value = pageOptions({ attainments, exceedance_descriptions, exceedance_types, area_classifications, adjustment_types, adjustment_source_types, reasons, sampling_points });
});
</script>

<template>
  <manager name="Exceedances" :options="options" :service="Service" :crud-component="Crud" />
</template>
