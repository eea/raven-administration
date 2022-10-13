<script setup>
var p = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  label: {
    type: String,
    default: ""
  }
});

const internalValue = ref(false);

onMounted(() => {
  if (p.modelValue != internalValue.value) internalValue.value = p.modelValue;
});

watch(
  () => p.modelValue,
  (nv) => {
    if (p.modelValue != internalValue.value) internalValue.value = p.modelValue;
  }
);

const emit = defineEmits(["update:modelValue"]);

const onClick = (el) => {
  internalValue.value = !internalValue.value;
  emit("update:modelValue", internalValue.value);
};

const cls = computed(() => {
  if (internalValue.value) return "n-checkbox-checked";
  else return "";
});
</script>

<script>
export default {
  inheritAttrs: false
};
</script>

<template>
  <label @click="onClick($el)" style="cursor: pointer">
    <div class="n-checkbox" v-bind="$attrs" :class="cls"></div>
    <span class="ml-1" style="position: relative; bottom: 2px">{{ label }}</span>
  </label>
</template>
