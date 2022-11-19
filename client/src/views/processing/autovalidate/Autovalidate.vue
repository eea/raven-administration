<script setup>
import Service from "./service";
import pageOptions from "./pageOptions";

const options = ref({});

onMounted(async () => {
  const pollutants = await Service.pollutants();
  options.value = pageOptions({ pollutants });
});
</script>
<template>
  <manager name="Auto validate" :options="options" :service="Service" :show-upload-button="false" />
</template>
