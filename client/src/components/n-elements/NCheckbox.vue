<script setup>
var p = defineProps({
  modelValue: {
    type: Boolean,
    default: false
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

const emit = defineEmits(["update:modelValue", "change"]);

const onClick = (el) => {
  internalValue.value = !internalValue.value;
  emit("update:modelValue", internalValue.value);
  emit("change");
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
  <div class="n-checkbox" v-bind="$attrs" :class="cls" @click.stop="onClick($el)"></div>
</template>
