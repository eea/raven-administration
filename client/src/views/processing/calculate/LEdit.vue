<script setup>
const props = defineProps({
  show: Boolean,
  calculation: Object,
  timeseries: Array
});

const obj = ref({});

watch(
  () => props.calculation,
  () => (obj.value = Object.assign({}, props.calculation))
);

// Make sure they come from the same station
const cmp_timeseries = computed(() => {
  if (obj.value.station == "") return [];
  return props.timeseries.filter((p) => p.label.startsWith(obj.value.station));
});
</script>

<template>
  <side-bar-crud :show="show" @cancel="$emit('close')" @commit="$emit('save', Object.assign({}, obj))">
    <div class="mb-4 font-bold text-base border-b">Required</div>
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
