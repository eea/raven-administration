<script setup>
import { onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Service from "./service";
import pageOptions from "./pageOptions";
import Eventy from "../../../helpers/eventy";

const options = ref({});

onMounted(async () => {
  Eventy.showMessage("Loading metadata", "loading");
  const lookups = await Service.lookups();
  Eventy.hideMessage();

  options.value = pageOptions(lookups);
});
</script>
<template>
  <Manager name="Networks" :options="options" :service="Service" />
</template>
