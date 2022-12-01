<script setup>
import Service from "./service";
import pageOptions from "./pageOptions";
import Crud from "./Crud.vue";
import Eventy from "../../../helpers/eventy";

const options = ref({});

onMounted(async () => {
  Eventy.showMessage("Loading metadata", "loading");
  const authorities = await Service.authorities();
  const zone_types = await Service.zone_types();
  Eventy.hideMessage();

  options.value = pageOptions({ authorities, zone_types });
});
</script>

<template>
  <manager name="Zones" :options="options" :service="Service" :show-add-button="false" :crud-component="Crud" />
</template>
