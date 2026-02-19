<script setup>
import { ref, onMounted } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Service from "./service";
import pageOptions from "./pageOptions";

const options = ref({});

onMounted(async () => {
  const units = await Service.units();
  const timeseries = await Service.timeseries();

  options.value = pageOptions({
    units: units,
    timeseries: timeseries
  });
});
</script>

<template>
  <manager name="Convert" :options="options" :service="Service" :show-download-button="true" />
</template>

<style></style>
