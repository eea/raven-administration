<script setup>
import { onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Service from "./service";
import pageOptions from "./pageOptions";
import Eventy from "../../../helpers/eventy";

const options = ref({});

onMounted(async () => {
  Eventy.showMessage("Loading metadata", "loading");
  const sampling_points = await Service.sampling_points();
  const result_nature_values = await Service.result_nature_values();
  const processtype_values = await Service.processtype_values();
  const samples = await Service.samples();
  const processes = await Service.processes();
  Eventy.hideMessage();

  options.value = pageOptions({ sampling_points, result_nature_values, processtype_values, samples, processes });
});
</script>

<template>
  <manager name="Observing capabilities" :options="options" :service="Service" />
</template>
