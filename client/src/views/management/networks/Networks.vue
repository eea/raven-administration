<script setup>
import { onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Service from "./service";
import pageOptions from "./pageOptions";
import Eventy from "../../../helpers/eventy";
const options = ref({});

onMounted(async () => {
  Eventy.showMessage("Loading metadata", "loading");
  const authorities = await Service.authorities();
  const levels = await Service.levels();
  const media = await Service.media();
  const timezones = await Service.timezones();
  Eventy.hideMessage();
  options.value = pageOptions({ authorities, levels, media, timezones });
});
</script>
<template>
  <Manager name="Networks" :options="options" :service="Service" />
</template>
