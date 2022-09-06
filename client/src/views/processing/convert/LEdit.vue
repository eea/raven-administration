<script setup>
const props = defineProps({
  show: Boolean,
  convertion: Object,
  timeseries: Array,
  units: Array
});

const obj = ref({});

watch(
  () => props.convertion,
  () => (obj.value = Object.assign({}, props.convertion))
);
</script>

<template>
  <side-bar-crud :show="show" @cancel="$emit('close')" @commit="$emit('save', Object.assign({}, obj))">
    <div class="mb-4 font-bold text-base border-b">Required</div>
    <div class="mb-2">
      <div class="font-bold">Timeserie:</div>
      <input type="text" class="n-input w-64" :disabled="true" :value="obj.station + ', ' + obj.pollutant + ', ' + obj.timestep" />
    </div>
    <div class="mb-2">
      <div class="font-bold">From unit:</div>
      <n-select v-model="obj.source_id" class="!w-64" :searchable="true">
        <n-option v-for="a in units" :key="a.value" :value="a.value" :label="a.label" />
      </n-select>
    </div>
    <div class="mb-2">
      <div class="font-bold">To unit:</div>
      <n-select v-model="obj.target_id" class="!w-64" :searchable="true">
        <n-option v-for="a in units" :key="a.value" :value="a.value" :label="a.label" />
      </n-select>
    </div>

    <div class="mb-2">
      <div class="font-bold">Factor:</div>
      <input type="number" class="n-input w-64" v-model="obj.factor" placeholder="float: Factor to convert unit" />
    </div>
  </side-bar-crud>
</template>
<style></style>
