<script setup>
import Service from "./service";
import pageOptions from "./pageOptions";

const options = ref({});

onMounted(async () => {
  options.value = pageOptions({});
});
</script>
<template>
  <manager name="Settings" :options="options" :service="Service" :show-download-button="false" :show-upload-button="false" :show-add-button="false"></manager>
</template>
