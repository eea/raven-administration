<script setup>
import Service from "./service";
import pageOptions from "./pageOptions";
import Crud from "./Crud.vue";

const options = ref({});

onMounted(async () => {
  const authorities = await Service.authorities();
  const zone_types = await Service.zone_types();

  options.value = pageOptions({ authorities, zone_types });
});
</script>

<template>
  <manager name="Zones" :options="options" :service="Service" :show-add-button="false" :crud-component="Crud" />
</template>
