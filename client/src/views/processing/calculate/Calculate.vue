<script setup>
import { ref, onMounted } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Crud from "./Crud.vue";
import Service from "./service";

const options = ref({});

onMounted(async () => {
  const timeseries = await Service.timeseries();

  options.value = {
    timeseries: timeseries,
    properties: [
      { prop: "id", label: "ID", showInGrid: false },
      { prop: "station", label: "Station", showInGrid: true, flex: 1 },
      { prop: "primary_pollutant", label: "Primary", showInGrid: true, flex: 1 },
      { prop: "operator", label: "Operator", showInGrid: true, flex: 1 },
      { prop: "secondary_pollutant", label: "Secondary", showInGrid: true, flex: 1 },
      { prop: "result_pollutant", label: "Result", showInGrid: true, flex: 1 }
    ]
  };
});
</script>

<template>
  <manager name="Calculations" :options="options" :service="Service" :crud-component="Crud" :show-download-button="true" />
</template>

<style></style>
