<script setup>
import { onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Service from "./service";
import pageOptions from "./pageOptions";
import usePluginPageExtension from "../../../composables/usePluginPageExtension";

const { extendOptions, extendService } = usePluginPageExtension('samplingpoints');
const service = extendService(Service);
const options = ref({});

onMounted(async () => {
  const lookups = await service.lookups();
  options.value = extendOptions(pageOptions(lookups));
});
</script>

<template>
  <manager name="Sampling points" :options="options" :service="service" />
</template>
