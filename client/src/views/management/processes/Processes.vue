<script setup>
import { onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Service from "./service";
import pageOptions from "./pageOptions";
import Eventy from "../../../helpers/eventy";

const options = ref({});

onMounted(async () => {
  Eventy.showMessage("Loading metadata", "loading");
  const measurement_types = await Service.measurement_types();
  const measurement_methods = await Service.measurement_methods();
  const measurement_equipments = await Service.measurement_equipment();
  const equiv_demonstrations = await Service.equiv_demonstrations();
  const concentrations = await Service.concentrations();
  const timesteps = await Service.timesteps();
  const authorities = await Service.authorities();
  Eventy.hideMessage();

  options.value = pageOptions({ measurement_types, measurement_methods, measurement_equipments, equiv_demonstrations, concentrations, timesteps, authorities });
});
</script>
<template>
  <manager name="Processes" :options="options" :service="Service" />
</template>
