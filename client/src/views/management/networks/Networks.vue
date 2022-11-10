<script setup>
import Service from "./service";
import pageOptions from "./pageOptions";

const options = ref({});

onMounted(async () => {
  const authorities = await Service.authorities();
  const levels = await Service.levels();
  const media = await Service.media();
  const timezones = await Service.timezones();
  options.value = pageOptions({ authorities, levels, media, timezones });
});
</script>
<template>
  <manager name="Networks" :options="options" :service="Service" />
</template>
