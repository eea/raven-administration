<script setup>
import { onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Service from "./service";
import pageOptions from "./pageOptions";

const options = ref({});

onMounted(async () => {
  options.value = pageOptions({});
});
</script>
<template>
  <manager name="Samples" :options="options" :service="Service" />
</template>
