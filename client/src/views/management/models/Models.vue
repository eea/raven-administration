<script setup>
import { onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Service from "./service";
import pageOptions from "./pageOptions";

const options = ref({});

onMounted(async () => {
  const lookups = await Service.lookups();
  options.value = pageOptions(lookups);
});
</script>

<template>
  <Manager name="Models / objective estimation" :options="options" :service="Service" :show-add-button="true" />
</template>
