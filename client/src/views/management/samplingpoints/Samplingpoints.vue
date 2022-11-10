<script setup>
import Service from "./service";
import pageOptions from "./pageOptions";

const options = ref({});

onMounted(async () => {
  const media = await Service.media();
  const stations = await Service.stations();
  const pollutants = await Service.pollutants();
  const timesteps = await Service.timesteps();
  const assessmenttypes = await Service.assessmenttypes();
  const stationclassifications = await Service.stationclassifications();
  const concentrations = await Service.concentrations();
  const measurementregimes = await Service.measurementregimes();

  options.value = pageOptions({ stations, pollutants, media, timesteps, assessmenttypes, stationclassifications, concentrations, measurementregimes });
});
</script>

<template>
  <manager name="Sampling points" :options="options" :service="Service" />
</template>
