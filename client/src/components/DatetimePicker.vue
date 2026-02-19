<script setup>
import { computed } from "vue";
import { VueDatePicker } from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";

const props = defineProps({
  modelValue: null
});
const emit = defineEmits(["update:modelValue"]);

// Normalize timestamp to ensure it has seconds
const normalizedValue = computed(() => {
  if (!props.modelValue) return null;

  const str = String(props.modelValue);
  // If it's missing seconds, add :00
  if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/.test(str)) {
    return str + ":00";
  }
  return str;
});

// Round time to the hour when changed
const handleUpdate = (val) => {
  if (!val) {
    emit("update:modelValue", val);
    return;
  }

  // Replace minutes and seconds with :00:00
  const rounded = val.replace(/:\d{2}:\d{2}$/, ":00:00");
  emit("update:modelValue", rounded);
};
</script>

<script>
export default {
  inheritAttrs: false
};
</script>

<template>
  <VueDatePicker :model-value="normalizedValue" @update:model-value="handleUpdate" v-bind="$attrs" model-type="yyyy-MM-dd HH:mm:ss" :time-config="{ enableMinutes: false, is24: true, timePickerInline: true }" :format="'yyyy-MM-dd, HH'" teleport="body" />
</template>

<style>
.dp__theme_light {
  --dp-text-color: inherit;
  --dp-primary-color: #4c566a; /* Nord blue-gray */
  --dp-primary-disabled-color: #d8dee9;
  --dp-primary-text-color: #fff;
}

:root {
  /*General*/
  --dp-font-family: inherit; /*Font family for the date picker*/

  --dp-input-padding: 3px 30px 3px 12px; /*Padding in the input*/

  /*Font sizes*/
  --dp-font-size: 0.9rem; /*Default font-size*/
}
</style>
