<script setup>
import { computed } from "@vue/reactivity";

const props = defineProps({
  show: Boolean,
  timeseries: Array
});

const obj = ref({});
const station = ref("");

watch(
  () => props.show,
  () => (obj.value = {})
);

const cmp_stations = computed(() => {
  return [...new Set(props.timeseries.map((p) => p.label.split(", ")[0]))];
});

// Make sure they come from the same station
const cmp_timeseries = computed(() => {
  if (station.value == "") return [];
  return props.timeseries.filter((p) => p.label.startsWith(station.value));
});
</script>

<template>
  <side-bar-crud :show="show" @cancel="$emit('close')" @commit="$emit('save', Object.assign({}, obj))">
    <div class="mb-4 font-bold text-base border-b">Required</div>
    <div class="mb-2">
      <div class="font-bold">Stations:</div>
      <n-select v-model="station" class="!w-64">
        <n-option v-for="a in cmp_stations" :key="a" :value="a" :label="a" />
      </n-select>
    </div>
    <div class="mb-2">
      <div class="font-bold">Primary:</div>
      <n-select v-model="obj.primary" class="!w-64" :searchable="true">
        <n-option v-for="a in cmp_timeseries" :key="a.value" :value="a.value" :label="a.label" />
      </n-select>
    </div>
    <div class="mb-2">
      <div class="font-bold">Operator:</div>
      <n-select v-model="obj.operator" class="!w-64">
        <n-option value="+" label="+" />
        <n-option value="-" label="-" />
      </n-select>
    </div>
    <div class="mb-2">
      <div class="font-bold">Secondary:</div>
      <n-select v-model="obj.secondary" class="!w-64" :searchable="true">
        <n-option v-for="a in cmp_timeseries" :key="a.value" :value="a.value" :label="a.label" />
      </n-select>
    </div>
    <div class="mb-2">
      <div class="font-bold">Result:</div>
      <n-select v-model="obj.result" class="!w-64" :searchable="true">
        <n-option v-for="a in cmp_timeseries" :key="a.value" :value="a.value" :label="a.label" />
      </n-select>
    </div>
  </side-bar-crud>
</template>
<style></style>
