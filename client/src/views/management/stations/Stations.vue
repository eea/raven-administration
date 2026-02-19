<script setup>
import { onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Service from "./service";
import pageOptions from "./pageOptions";
import Eventy from "../../../helpers/eventy";

const options = ref({});

onMounted(async () => {
  Eventy.showMessage("Loading metadata", "loading");
  const networks = await Service.networks();
  const measurementregimes = await Service.measurementregimes();
  const media = await Service.media();
  const areaclassifications = await Service.areaclassifications();
  Eventy.hideMessage();
  options.value = pageOptions({ networks, measurementregimes, media, areaclassifications });
});
</script>

<template>
  <manager name="Stations" :options="options" :service="Service" />
</template>
