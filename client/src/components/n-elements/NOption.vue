<script setup>
var p = defineProps({
  value: {
    type: [String, Number],
    default: "",
  },
  label: {
    type: String,
    default: "",
  },
});
</script>
<template>
  <div class="n-option" n-id="n-option" @click="$parent.$emit('slot-click', value)" :value="value" :label="label">
    {{ label }}
  </div>
</template>
