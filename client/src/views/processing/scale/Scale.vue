<script setup>
import Service from "./service";

const timeserieId = ref("");
const timeseries = ref([]);

onMounted(async () => {
  timeseries.value = await Service.timeseries();
});

const cls_timeseries = (hasscalingpoint) => {
  if (hasscalingpoint) return "border-l-2 border-nord7";
  return "";
};
</script>

<template>
  <common-layout>
    <tool-bar title="Scale" :show-filter="false" :show-add="false" :show-download="false" />

    <container>
      <div class="flex gap-3">
        <div class="flex-1">
          <div class="font-bold">Timeserie</div>
          <n-select class="!w-full" v-model="timeserieId" :searchable="true">
            <n-option v-for="opt in timeseries" :value="opt.value" :label="opt.label" :class="cls_timeseries(opt.hasscalingpoint)" />
          </n-select>
        </div>
        <div>
          <div>&nbsp;</div>
          <button class="n-button" :disabled="timeserieId.length == 0">Show scaling points</button>
        </div>
      </div>
    </container>
  </common-layout>
</template>

<style></style>
