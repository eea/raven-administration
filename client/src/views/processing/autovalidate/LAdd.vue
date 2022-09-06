<script setup>
const props = defineProps({
  show: Boolean,
  pollutants: Array
});

const obj = ref({});

watch(
  () => props.show,
  () => (obj.value = {})
);
</script>

<template>
  <side-bar-crud :show="show" @cancel="$emit('close')" @commit="$emit('save', Object.assign({}, obj))">
    <div class="mb-4 font-bold text-base border-b">Required</div>
    <div class="mb-2">
      <div class="font-bold">Pollutant:</div>
      <n-select v-model="obj.pollutant_id" class="!w-64" :searchable="true">
        <n-option v-for="a in pollutants" :key="a.value" :value="a.value" :label="a.label" />
      </n-select>
    </div>
    <div class="mb-2">
      <div class="font-bold">Minimum:</div>
      <input type="number" class="n-input w-64" v-model="obj.min" placeholder="float: Minimum valid value" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Maximum:</div>
      <input type="number" class="n-input w-64" v-model="obj.max" placeholder="float: Maximum valid value" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Repeat:</div>
      <input type="number" class="n-input w-64" v-model="obj.rep" placeholder="int: Maximum number of repeats" />
    </div>
  </side-bar-crud>
</template>
<style></style>
