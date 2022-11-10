<script setup>
import Service from "./service";
import pageOptions from "./pageOptions";

const options = ref({});

onMounted(async () => {
  const networks = await Service.networks();
  const measurementregimes = await Service.measurementregimes();
  const media = await Service.media();
  const areaclassifications = await Service.areaclassifications();
  options.value = pageOptions({ networks, measurementregimes, media, areaclassifications });
});
</script>

<template>
  <manager name="Stations" :options="options" :service="Service" />
</template>
