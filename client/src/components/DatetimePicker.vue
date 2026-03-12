<script setup>
import { computed } from "vue";
import { VueDatePicker } from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";

const props = defineProps({
  modelValue: null
});
const emit = defineEmits(["update:modelValue"]);

// Normalize timestamp to ensure it has seconds and handle various input types
const normalizedValue = computed(() => {
  if (!props.modelValue) return null;

  // If it's a Date object, convert to string format
  if (props.modelValue instanceof Date) {
    const date = props.modelValue;
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const seconds = String(date.getSeconds()).padStart(2, "0");
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  }

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
  <VueDatePicker :model-value="normalizedValue" @update:model-value="handleUpdate" v-bind="$attrs" model-type="yyyy-MM-dd HH:mm:ss" :time-config="{ enableMinutes: false, is24: true, timePickerInline: true }" :formats="{ input: 'yyyy-MM-dd, HH', preview: 'yyyy-MM-dd, HH' }" teleport="body" />
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
