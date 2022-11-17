<script setup>
import Service from "./service";
import pageOptions from "./pageOptions";

const options = ref({});

onMounted(async () => {
  const assessment_regimes = await Service.assessment_regimes();
  console.log("AAA", assessment_regimes);
  options.value = pageOptions({ assessment_regimes });
});
</script>
<template>
  <manager name="Attainments" :options="options" :service="Service" />
</template>
