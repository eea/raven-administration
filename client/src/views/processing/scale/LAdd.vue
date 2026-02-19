<script setup>
import { ref, watch } from "vue";
const props = defineProps({
  show: Boolean,
  obj: Object
});

const _obj = ref({});

watch(
  () => props.show,
  () => {
    _obj.value = Object.assign({}, props.obj);
  }
);
</script>

<template>
  <side-bar-crud :show="show" @cancel="$emit('close')" @commit="$emit('save', Object.assign({}, _obj))">
    <div class="mb-4 font-bold text-base border-b">Required</div>
    <div class="mb-2">
      <div class="font-bold">Zero point:</div>
      <input type="number" class="input w-72" v-model="_obj.zero_point" placeholder="float: Zero point value" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Span value:</div>
      <input type="number" class="input w-72" v-model="_obj.span_value" placeholder="float: Span value" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Gas concentration:</div>
      <input type="number" class="input w-72" v-model="_obj.gas_concentration" placeholder="float: Gas concentration" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Timestamp:</div>
      <n-datetime v-model="_obj.timestamp" class="w-72!" />
    </div>
  </side-bar-crud>
</template>
<style></style>
