<script setup>
import Service from "./service";
import pageOptions from "./pageOptions";
import Eventy from "../../../helpers/eventy";

const options = ref({});

onMounted(async () => {
  Eventy.showMessage("Loading metadata", "loading");
  const assessment_regimes = await Service.assessment_regimes();
  Eventy.hideMessage();
  options.value = pageOptions({ assessment_regimes });
});
</script>
<template>
  <manager name="Attainments" :options="options" :service="Service" />
</template>
