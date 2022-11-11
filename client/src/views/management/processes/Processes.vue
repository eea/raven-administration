<script setup>
import Service from "./service";
import pageOptions from "./pageOptions";

const options = ref({});

onMounted(async () => {
  const measurement_types = await Service.measurement_types();
  const measurement_methods = await Service.measurement_methods();
  const measurement_equipments = await Service.measurement_equipment();
  const equiv_demonstrations = await Service.equiv_demonstrations();
  const concentrations = await Service.concentrations();
  const timesteps = await Service.timesteps();
  const authorities = await Service.authorities();

  options.value = pageOptions({ measurement_types, measurement_methods, measurement_equipments, equiv_demonstrations, concentrations, timesteps, authorities });
});
</script>
<template>
  <manager name="Processes" :options="options" :service="Service" />
</template>
