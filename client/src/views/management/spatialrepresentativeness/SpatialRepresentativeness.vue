<script setup>
import { onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Service from "./service";
import pageOptions from "./pageOptions";
import SrCrud from "./SrCrud.vue";

const options = ref({});

onMounted(async () => {
  const lookups = await Service.lookups();
  options.value = {
    ...pageOptions(lookups),
    entityName: "Spatial Representativeness"
  };
});
</script>

<template>
  <Manager
    name="Spatial Representativeness"
    :options="options"
    :service="Service"
    :crud-component="SrCrud"
    :show-duplicate="true" />
</template>