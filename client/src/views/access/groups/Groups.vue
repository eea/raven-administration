<script setup>
import { onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Crud from "./Crud.vue";
import Service from "./service";
import pageOptions from "./pageOptions";

const options = ref({});

onMounted(async () => {
  const networks = await Service.networks();
  options.value = pageOptions({ networks });
});
</script>

<template>
  <Manager name="Groups" :options="options" :service="Service" :crud-component="Crud" />
</template>

<style></style>
