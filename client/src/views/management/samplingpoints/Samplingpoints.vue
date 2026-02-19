<script setup>
import { onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Service from "./service";
import pageOptions from "./pageOptions";
import Eventy from "../../../helpers/eventy";

const options = ref({});

onMounted(async () => {
  Eventy.showMessage("Loading metadata", "loading");
  const media = await Service.media();
  const stations = await Service.stations();
  const pollutants = await Service.pollutants();
  const timesteps = await Service.timesteps();
  const assessmenttypes = await Service.assessmenttypes();
  const stationclassifications = await Service.stationclassifications();
  const concentrations = await Service.concentrations();
  const measurementregimes = await Service.measurementregimes();
  Eventy.hideMessage();

  options.value = pageOptions({ stations, pollutants, media, timesteps, assessmenttypes, stationclassifications, concentrations, measurementregimes });
});
</script>

<template>
  <manager name="Sampling points" :options="options" :service="Service" />
</template>
