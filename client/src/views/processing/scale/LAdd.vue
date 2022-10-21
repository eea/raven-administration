<script setup>
const props = defineProps({
  show: Boolean,
  obj: Object
});

// const obj = ref({});

watch(
  () => props.show,
  () => (props.obj = {})
);
</script>

<template>
  <side-bar-crud :show="show" @cancel="$emit('close')" @commit="$emit('save', Object.assign({}, obj))">
    <div class="mb-4 font-bold text-base border-b">Required</div>
    <div class="mb-2">
      <div class="font-bold">Zero point:</div>
      <input type="number" class="n-input w-64" v-model="obj.zero_point" placeholder="float: Zero point value" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Span value:</div>
      <input type="number" class="n-input w-64" v-model="obj.span_value" placeholder="float: Span value" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Gas concentration:</div>
      <input type="number" class="n-input w-64" v-model="obj.gas_concentration" placeholder="float: Gas concentration" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Timestamp:</div>
      <n-datetime v-model="obj.timestamp" />
    </div>
  </side-bar-crud>
</template>
<style></style>
