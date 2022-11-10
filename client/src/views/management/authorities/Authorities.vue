<script setup>
import Service from "./service";
import pageOptions from "./pageOptions";

const options = ref({});

onMounted(async () => {
  options.value = pageOptions({});
});
</script>
<template>
  <manager name="Authorities" :options="options" :service="Service" />
</template>
