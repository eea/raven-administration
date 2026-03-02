<script setup>
import { onMounted, ref } from "vue";
import Service from "./service";
import pageOptions from "./pageOptions";
import Crud from "./Crud.vue";
import Eventy from "../../../helpers/eventy";

import Manager from "../../../components/n-manager/Manager.vue";

const options = ref({});

onMounted(async () => {
  Eventy.showMessage("Loading metadata", "loading");
  const zone_types = await Service.zone_types();
  const zone_categories = await Service.zone_categories();
  Eventy.hideMessage();

  options.value = pageOptions({ zone_types, zone_categories });
});
</script>

<template>
  <Manager name="Zones" :options="options" :service="Service" :show-add-button="true" :crud-component="Crud" />
</template>
